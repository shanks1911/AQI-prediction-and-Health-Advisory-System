from dotenv import load_dotenv
import os
import requests 
import pandas as pd 
import json
import streamlit as st 
from datetime import datetime

from aqi_calculator import calculate_overall_aqi
from lat_lon import get_lat_lon
from forecast_lstm import forecast_future_LSTM
from chatbot import get_aqi_advice, get_aqi_category

# =====================================================
# CONFIGURATION AND SETUP
# =====================================================

def load_config():
    """Load environment variables and API keys"""
    load_dotenv(dotenv_path=".env")
    return os.getenv("API_KEY")

def setup_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="AQI Dashboard", 
        layout="wide",
        page_icon="🌍"
    )
    
    st.title("🌍 Air Quality Monitoring Dashboard")
    st.markdown("Track air quality trends, evaluate health risks, and receive personalized health insights in real-time.")
    st.markdown("---")

# =====================================================
# DATA FETCHING AND PROCESSING
# =====================================================

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def fetch_coordinates(api_key, city):
    """Fetch coordinates for a given city"""
    return get_lat_lon(api_key, city)

@st.cache_data(ttl=600)  # Cache for 10 minutes
def fetch_current_aqi_data(api_key, latitude, longitude):
    """Fetch current AQI data (last 24 hours)"""
    curr_ts = int(datetime.now().timestamp())
    one_day_ago_ts = curr_ts - (24 * 3600)
    
    resp = requests.get(
        "http://api.openweathermap.org/data/2.5/air_pollution/history",
        params={
            "lat": latitude,
            "lon": longitude,
            "start": one_day_ago_ts,
            "end": curr_ts,
            "appid": api_key
        }
    )
    
    if resp.status_code != 200:
        raise Exception(f"API request failed with status {resp.status_code}")
    
    return resp.json()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_historical_data(api_key, latitude, longitude):
    """Fetch extended historical data for LSTM training"""
    curr_ts = int(datetime.now().timestamp())
    half_years_ago_ts = curr_ts - (180 * 24 * 3600)
    
    resp = requests.get(
        "http://api.openweathermap.org/data/2.5/air_pollution/history",
        params={
            "lat": latitude,
            "lon": longitude,
            "start": half_years_ago_ts,
            "end": curr_ts,
            "appid": api_key
        }
    )
    
    if resp.status_code != 200:
        raise Exception(f"Historical data API request failed with status {resp.status_code}")
    
    return resp.json()

def process_aqi_data(data):
    """Process raw API data into structured DataFrame"""
    df = pd.json_normalize(data['list'])
    df['Overall_AQI'] = df.apply(calculate_overall_aqi, axis=1)
    df['dt'] = pd.to_datetime(df['dt'], unit='s', utc=True).map(
        lambda x: x.tz_convert('Asia/Kolkata')
    )
    df['dt'] = df['dt'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['dt'] = pd.to_datetime(df['dt'])
    return df.reset_index(drop=True)

# =====================================================
# UI COMPONENTS
# =====================================================

def render_location_input():
    """Render the location input section"""
    st.header("📍 Select Your Location")
    
    col1, col2, col3 = st.columns([3, 1, 2])
    
    with col1:
        city = st.text_input(
            "Enter city name", 
            value=st.session_state.get('last_city', 'Mumbai'),
            placeholder="e.g., Mumbai, Delhi, Bangalore..."
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button("🔍 Get AQI Data", type="primary")
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📋 Example Cities"):
            show_example_cities()
    
    return city, search_button

def show_example_cities():
    """Display example cities as buttons"""
    st.markdown("### 🌟 Popular Cities")
    example_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad"]
    cols = st.columns(4)
    
    for i, example_city in enumerate(example_cities):
        col_idx = i % 4
        with cols[col_idx]:
            if st.button(f"📍 {example_city}", key=f"example_{i}"):
                st.session_state.selected_city = example_city
                st.rerun()

def render_location_info(city, coordinates):
    """Display location information"""
    st.success(
        f"📍 **{city}, {coordinates['state']}, {coordinates['country']}** "
        f"(Lat: {coordinates['latitude']:.4f}, Lon: {coordinates['longitude']:.4f})"
    )

def render_current_aqi_display(current_df, city):
    """Render current AQI metrics and status"""
    st.header("📊 Current Air Quality Status")
    
    current_aqi = current_df['Overall_AQI'].iloc[-1]
    aqi_status, aqi_color = get_aqi_category(current_aqi)
    last_updated = current_df['dt'].iloc[-1].strftime("%Y-%m-%d %H:%M")
    
    # Create metrics with better styling
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Current AQI", 
            value=f"{current_aqi:.1f}",
            help="Air Quality Index - Lower is better"
        )
    
    with col2:
        st.metric(
            label="Air Quality", 
            value=aqi_status,
            help="Health category based on current AQI"
        )
    
    with col3:
        st.metric(
            label="Location", 
            value=city,
            help="Current monitoring location"
        )
    
    with col4:
        st.metric(
            label="Last Updated", 
            value=last_updated.split()[1],  # Show only time
            delta=last_updated.split()[0],  # Show date in delta
            help="Last data update timestamp"
        )
    
    # AQI Status with color coding
    if current_aqi <= 50:
        st.success(f"🟢 Air quality is **{aqi_status}** - Great for outdoor activities!")
    elif current_aqi <= 100:
        st.info(f"🟡 Air quality is **{aqi_status}** - Acceptable for most people.")
    elif current_aqi <= 150:
        st.warning(f"🟠 Air quality is **{aqi_status}** - Sensitive individuals should limit outdoor exposure.")
    elif current_aqi <= 200:
        st.error(f"🔴 Air quality is **{aqi_status}** - Everyone should limit outdoor activities.")
    else:
        st.error(f"🚫 Air quality is **{aqi_status}** - Avoid outdoor activities!")
    
    return current_aqi, aqi_status

def render_forecast_section(coordinates, api_key):
    """Render the LSTM forecast section"""
    st.header("🔮 AI-Powered 7-Day Forecast")
    st.markdown("Generate detailed forecasts using LSTM neural networks (processing may take 1-2 minutes)")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**Machine Learning Forecast** - Get predictions for the next 7 days based on historical patterns")
        st.markdown("*Uses LSTM (Long Short-Term Memory) neural networks for accurate predictions*")
    
    with col2:
        forecast_button = st.button("📈 Generate Forecast", type="secondary")
    
    # Handle forecast generation
    if forecast_button or st.session_state.get('forecast_requested', False):
        if forecast_button:
            st.session_state.forecast_requested = True
            # Clear existing forecast data for new request
            for key in ['forecast_df', 'model_metrics']:
                if key in st.session_state:
                    del st.session_state[key]
        
        generate_and_display_forecast(coordinates, api_key)
    else:
        st.info("💡 Click the button above to generate AI-powered forecasts using historical data patterns.")

def generate_and_display_forecast(coordinates, api_key):
    """Generate and display LSTM forecast"""
    if 'forecast_df' not in st.session_state:
        try:
            # Fetch historical data
            with st.spinner("🔍 Fetching extended historical data for AI model training..."):
                historical_data = fetch_historical_data(
                    api_key, 
                    coordinates['latitude'], 
                    coordinates['longitude']
                )
            
            # Process and save data
            with st.spinner("⚙️ Processing historical data..."):
                df = process_aqi_data(historical_data)
                df.to_csv('air_pollution_data_AQI.csv', index=False)
            
            # Generate forecast
            with st.spinner("🧠 Training LSTM neural network and generating forecast..."):
                rmse, mae = forecast_future_LSTM()
                forecast_df = pd.read_csv("forecast_LSTM_AQI.csv")
                
                # Cache results
                st.session_state.forecast_df = forecast_df
                st.session_state.model_metrics = {'rmse': rmse, 'mae': mae}
        
        except Exception as e:
            st.error(f"❌ Forecast generation failed: {str(e)}")
            st.session_state.forecast_requested = False
            return
    
    # Display forecast results
    if 'forecast_df' in st.session_state:
        display_forecast_results()

def display_forecast_results():
    """Display the generated forecast results"""
    forecast_df = st.session_state.forecast_df
    model_metrics = st.session_state.model_metrics
    
    st.success("✅ Forecast generated successfully!")
    
    # Model performance metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Model Accuracy (RMSE)", f"{model_metrics['rmse']:.2f}", help="Root Mean Square Error - Lower is better")
    with col2:
        st.metric("Model Precision (MAE)", f"{model_metrics['mae']:.2f}", help="Mean Absolute Error - Lower is better")
    
    # Forecast visualization
    st.subheader("📈 7-Day AQI Forecast Trend")
    st.line_chart(
        data=forecast_df.set_index('timestamp')['predicted_AQI'], 
        height=400
    )
    
    # Forecast summary statistics
    st.subheader("📋 Forecast Summary")
    avg_forecast = forecast_df['predicted_AQI'].mean()
    max_forecast = forecast_df['predicted_AQI'].max()
    min_forecast = forecast_df['predicted_AQI'].min()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("7-Day Average AQI", f"{avg_forecast:.1f}")
    with col2:
        st.metric("Peak AQI (Worst)", f"{max_forecast:.1f}")
    with col3:
        st.metric("Best AQI (Lowest)", f"{min_forecast:.1f}")
    
    # Forecast interpretation
    if avg_forecast <= 50:
        st.success("🟢 **Good news!** The forecast shows generally good air quality for the next 7 days.")
    elif avg_forecast <= 100:
        st.info("🟡 **Moderate conditions** expected over the next week. Generally acceptable for most people.")
    elif avg_forecast <= 150:
        st.warning("🟠 **Caution advised.** Air quality may be unhealthy for sensitive groups during the forecast period.")
    else:
        st.error("🔴 **Health alert!** Poor air quality expected. Plan indoor activities and take necessary precautions.")

# =====================================================
# CHAT INTERFACE COMPONENTS
# =====================================================

def render_chat_interface(city=None, current_aqi=None):
    """Render the main chat interface"""
    st.header("💬 AQI Health Advisor Chatbot")
    
    if city and current_aqi is not None:
        st.markdown(f"Get personalized health advice for **{city}** (Current AQI: {current_aqi:.1f})")
        chat_key = f"chat_messages_{city}"
        render_personalized_chat(chat_key, city, current_aqi)
    else:
        st.markdown("Ask general questions about air quality and health. Enter a city above for personalized advice.")
        chat_key = "general_chat_messages"
        render_general_chat(chat_key)

def render_personalized_chat(chat_key, city, current_aqi):
    """Render chat interface with city-specific context"""
    # Initialize chat history
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
        aqi_status, _ = get_aqi_category(current_aqi)
        welcome_msg = (
            f"Hello! I'm your AQI Health Advisor. The current air quality in **{city}** is "
            f"{current_aqi:.1f} ({aqi_status}). How can I help you stay healthy today?"
        )
        st.session_state[chat_key].append({"role": "assistant", "content": welcome_msg})
    
    # Display chat messages
    display_chat_messages(chat_key)
    
    # Chat input
    handle_chat_input(chat_key, city, current_aqi)
    
    # Suggested questions
    render_suggested_questions(chat_key, city, current_aqi, is_personalized=True)
    
    # Chat controls
    render_chat_controls(chat_key)

def render_general_chat(chat_key):
    """Render general chat interface without city context"""
    # Initialize general chat
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
        welcome_msg = (
            "Hello! I'm your AQI Health Advisor. I can answer general questions about air quality "
            "and health. For personalized advice, please enter a city name above and get AQI data first."
        )
        st.session_state[chat_key].append({"role": "assistant", "content": welcome_msg})
    
    # Display chat messages
    display_chat_messages(chat_key)
    
    # Chat input
    handle_chat_input(chat_key, city=None, current_aqi=None)
    
    # Suggested questions
    render_suggested_questions(chat_key, city=None, current_aqi=None, is_personalized=False)
    
    # Chat controls
    render_chat_controls(chat_key)

def display_chat_messages(chat_key):
    """Display chat message history"""
    for message in st.session_state[chat_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_chat_input(chat_key, city, current_aqi):
    """Handle chat input and generate responses"""
    placeholder_text = "Ask about air quality, health advice, or general information..." if city else "Ask general questions about air quality and health..."
    
    if prompt := st.chat_input(placeholder_text):
        # Add user message
        st.session_state[chat_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    # Get forecast data if available
                    forecasted_aqi = st.session_state.get('forecast_df', {}).get('predicted_AQI', []) if 'forecast_df' in st.session_state else []
                    
                    response = get_aqi_advice(
                        forecasted_aqi=forecasted_aqi,
                        user_health_issues=prompt,
                        current_aqi=current_aqi,
                        city=city or "your location"
                    )
                    st.markdown(response)
                    st.session_state[chat_key].append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}. Please try rephrasing your question."
                    st.markdown(error_msg)
                    st.session_state[chat_key].append({"role": "assistant", "content": error_msg})

def render_suggested_questions(chat_key, city, current_aqi, is_personalized):
    """Render suggested questions section"""
    st.markdown("### 💡 Suggested Questions")
    
    if is_personalized:
        questions = [
            "What precautions should I take today?",
            "Is it safe to exercise outdoors?",
            "I have asthma, what should I do?",
            "What indoor air purification tips do you have?",
            "Should I avoid outdoor activities today?",
            "What does this AQI level mean for my health?"
        ]
    else:
        questions = [
            "What is AQI and how is it calculated?",
            "What are the health effects of air pollution?",
            "How can I protect myself from bad air quality?",
            "What are the main air pollutants?",
            "Best indoor air purification methods?",
            "How does weather affect air quality?"
        ]
    
    # Display questions in columns
    col1, col2 = st.columns(2)
    for i, question in enumerate(questions):
        col = col1 if i % 2 == 0 else col2
        with col:
            button_key = f"suggest_{chat_key}_{i}"
            if st.button(question, key=button_key):
                handle_suggested_question_click(chat_key, question, city, current_aqi)

def handle_suggested_question_click(chat_key, question, city, current_aqi):
    """Handle suggested question button clicks"""
    st.session_state[chat_key].append({"role": "user", "content": question})
    
    try:
        forecasted_aqi = st.session_state.get('forecast_df', {}).get('predicted_AQI', []) if 'forecast_df' in st.session_state else []
        response = get_aqi_advice(
            forecasted_aqi=forecasted_aqi,
            user_health_issues=question,
            current_aqi=current_aqi,
            city=city or "your location"
        )
        st.session_state[chat_key].append({"role": "assistant", "content": response})
    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}."
        st.session_state[chat_key].append({"role": "assistant", "content": error_msg})
    
    st.rerun()

def render_chat_controls(chat_key):
    """Render chat control buttons"""
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🗑️ Clear Chat", key=f"clear_{chat_key}"):
            st.session_state[chat_key] = []
            st.rerun()

# =====================================================
# MAIN APPLICATION LOGIC
# =====================================================

def main():
    """Main application function"""
    # Setup
    api_key = load_config()
    if not api_key:
        st.error("❌ API key not found! Please check your .env file.")
        return
    
    setup_page()
    
    # Location input
    city, search_button = render_location_input()
    
    # Handle example city selection
    if 'selected_city' in st.session_state:
        city = st.session_state.selected_city
        del st.session_state.selected_city
        search_button = True
    
    # Main dashboard logic
    if city and (search_button or st.session_state.get('basic_data_loaded', False)):
        handle_main_dashboard(api_key, city, search_button)
    elif city:
        st.info("👆 Click 'Get AQI Data' to load air quality information for your city.")
        render_chat_interface()
    else:
        st.info("👆 Please enter a city name to get started.")
        show_example_cities()
        render_chat_interface()
    
    # Footer
    render_footer()

def handle_main_dashboard(api_key, city, search_button):
    """Handle the main dashboard when city data is available"""
    # Check if we need to reload data
    need_reload = (
        not st.session_state.get('basic_data_loaded', False) or 
        st.session_state.get('current_city', '') != city or
        search_button
    )
    
    if need_reload:
        load_city_data(api_key, city)
    
    # Display dashboard content if data is available
    if 'current_aqi_df' in st.session_state and 'coordinates' in st.session_state:
        current_df = st.session_state.current_aqi_df
        coordinates = st.session_state.coordinates
        
        # Display location info
        render_location_info(city, coordinates)
        
        # Current AQI display
        current_aqi, aqi_status = render_current_aqi_display(current_df, city)
        
        # Add separator
        st.markdown("---")
        
        # Chat interface (prominently placed)
        render_chat_interface(city, current_aqi)
        
        # Add separator
        st.markdown("---")
        
        # Forecast section
        render_forecast_section(coordinates, api_key)
    else:
        st.error("❌ Failed to load AQI data. Please try searching again.")

def load_city_data(api_key, city):
    """Load city coordinate and AQI data"""
    try:
        # Get coordinates
        with st.spinner("🌍 Getting location coordinates..."):
            latitude, longitude, country, state = fetch_coordinates(api_key, city)
            coordinates = {
                'latitude': latitude,
                'longitude': longitude,
                'country': country,
                'state': state
            }
            st.session_state.coordinates = coordinates
        
        # Fetch current AQI data
        with st.spinner("📊 Fetching current air quality data..."):
            data = fetch_current_aqi_data(api_key, latitude, longitude)
        
        # Process data
        with st.spinner("⚙️ Processing air quality data..."):
            current_df = process_aqi_data(data)
            st.session_state.current_aqi_df = current_df
        
        # Set flags
        st.session_state.basic_data_loaded = True
        st.session_state.current_city = city
        st.session_state.last_city = city
        
    except Exception as e:
        st.error(f"❌ An error occurred while loading data: {str(e)}")
        st.markdown("Please try again or check your city name.")

def render_footer():
    """Render application footer"""
    st.markdown("---")
    st.markdown(
        "*Data provided by OpenWeatherMap Air Pollution API. "
        "Forecasts generated using LSTM neural networks. "
        "Chat responses powered by AI health advisor.*"
    )
    st.markdown(
        "<div style='text-align: center; color: gray; font-size: 0.8em;'>"
        "🌍 Built for healthier communities through air quality awareness"
        "</div>", 
        unsafe_allow_html=True
    )

# =====================================================
# APPLICATION ENTRY POINT
# =====================================================

if __name__ == "__main__":
    main()