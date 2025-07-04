# from dotenv import load_dotenv
# import os
# import requests 
# import pandas as pd 
# import json
# import streamlit as st 
# from datetime import datetime

# from aqi_calculator import calculate_overall_aqi
# from lat_lon import get_lat_lon
# from forecast_lstm import forecast_future_LSTM
# from chatbot import get_aqi_advice, get_aqi_category

# # Load API Key
# load_dotenv(dotenv_path=".env")
# api_key = os.getenv("API_KEY")

# # ---------------------- Dashboard Configuration ----------------------
# st.set_page_config(page_title="AQI Dashboard", layout="wide")
# st.title("🌍 Air Quality Monitoring Dashboard")
# st.markdown("Track air quality trends, evaluate health risks, and receive precautionary insights in real-time.")

# # ---------------------- City Input (Main Area) ----------------------
# st.header("📍 Enter Your Location")
# col1, col2 = st.columns([2, 1])

# with col1:
#     city = st.text_input("City name", value="Thane", placeholder="Enter city name...")

# with col2:
#     st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
#     search_button = st.button("🔍 Get AQI Data", type="primary")

# # ---------------------- Main Dashboard Content ----------------------
# if city and (search_button or st.session_state.get('data_loaded', False)):
    
#     # Check if we need to reload data (city changed or first time)
#     need_reload = (
#         not st.session_state.get('data_loaded', False) or 
#         st.session_state.get('current_city', '') != city or
#         search_button
#     )
    
#     if need_reload:
#         # Set flags
#         st.session_state.data_loaded = True
#         st.session_state.current_city = city
        
#         try:
#             # 1. Get coordinates
#             with st.spinner("Getting location coordinates..."):
#                 latitude, longitude, country, state = get_lat_lon(api_key, city)
#                 # Cache coordinates
#                 st.session_state.coordinates = {
#                     'latitude': latitude,
#                     'longitude': longitude,
#                     'country': country,
#                     'state': state
#                 }
            
#             # 2. Fetch historical AQI data
#             with st.spinner("Fetching historical air quality data..."):
#                 curr_ts = int(datetime.now().timestamp())
#                 half_years_ago_ts = curr_ts - (180 * 24 * 3600)
#                 resp = requests.get(
#                     "http://api.openweathermap.org/data/2.5/air_pollution/history",
#                     params={
#                         "lat": latitude,
#                         "lon": longitude,
#                         "start": half_years_ago_ts,
#                         "end": curr_ts,
#                         "appid": api_key
#                     }
#                 )
                
#                 if resp.status_code != 200:
#                     st.error(f"Failed to fetch data: {resp.status_code}")
#                     st.stop()

#             # 3. Process data
#             with st.spinner("Processing air quality data..."):
#                 data = resp.json()
#                 pd.json_normalize(data['list']).to_csv('air_pollution_data.csv', index=False)
#                 df = pd.read_csv('air_pollution_data.csv')
#                 df['Overall_AQI'] = df.apply(calculate_overall_aqi, axis=1)
#                 df['dt'] = pd.to_datetime(df['dt'], unit='s', utc=True).map(lambda x: x.tz_convert('Asia/Kolkata'))
#                 df['dt'] = df['dt'].dt.strftime('%Y-%m-%d %H:%M:%S')
#                 df['dt'] = pd.to_datetime(df['dt'])
#                 df = df.reset_index(drop=True)
#                 df.to_csv('air_pollution_data_AQI.csv', index=False)
                
#                 # Cache the processed dataframe
#                 st.session_state.aqi_df = df
                
#             # 4. Generate forecast (only when data is reloaded)
#             with st.spinner("Generating LSTM forecast..."):
#                 rmse, mae = forecast_future_LSTM()
#                 forecast_df = pd.read_csv("forecast_LSTM_AQI.csv")
                
#                 # Cache forecast data and metrics
#                 st.session_state.forecast_df = forecast_df
#                 st.session_state.model_metrics = {'rmse': rmse, 'mae': mae}
                
#         except Exception as e:
#             st.error(f"An error occurred while loading data: {str(e)}")
#             st.markdown("Please try again or check your city name.")
#             st.stop()
    
#     # Use cached data if available
#     if 'aqi_df' in st.session_state and 'forecast_df' in st.session_state:
#         df = st.session_state.aqi_df
#         forecast_df = st.session_state.forecast_df
#         coordinates = st.session_state.coordinates
#         model_metrics = st.session_state.model_metrics
        
#         # Display location info
#         st.success(f"📍 **{city}, {coordinates['state']}, {coordinates['country']}** (Lat: {coordinates['latitude']}, Lon: {coordinates['longitude']})")

#         # ---------------------- Current AQI Display ----------------------
#         st.header("📊 Current Air Quality")
        
#         current_aqi = df['Overall_AQI'].iloc[-1]
        
#         # Get AQI status using the chatbot function
#         aqi_status, aqi_color = get_aqi_category(current_aqi)

#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.metric("Current AQI", f"{current_aqi:.1f}")
#         with col2:
#             st.metric("Status", aqi_status)
#         with col3:
#             st.metric("Last Updated", df['dt'].iloc[-1].strftime("%Y-%m-%d %H:%M"))

#         # ---------------------- Forecast Section ----------------------
#         st.header("🔮 7-Day AQI Forecast")
        
#         col1, col2 = st.columns(2)
#         with col1:
#             st.metric("Model RMSE", f"{model_metrics['rmse']:.2f}")
#         with col2:
#             st.metric("Model MAE", f"{model_metrics['mae']:.2f}")
        
#         # Display forecast chart
#         st.subheader("📈 Forecasted AQI Trend")
#         st.line_chart(forecast_df.set_index('timestamp')['predicted_AQI'])
        
#         # Show forecast summary
#         avg_forecast = forecast_df['predicted_AQI'].mean()
#         max_forecast = forecast_df['predicted_AQI'].max()
#         min_forecast = forecast_df['predicted_AQI'].min()
        
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.metric("7-Day Average", f"{avg_forecast:.1f}")
#         with col2:
#             st.metric("Forecast Max", f"{max_forecast:.1f}")
#         with col3:
#             st.metric("Forecast Min", f"{min_forecast:.1f}")

#         # ---------------------- Chatbot Interface ----------------------
#         st.header("🤖 AQI Health Advisor Chat")
#         st.markdown("Ask questions about air quality, health impacts, or get personalized advice based on the forecast.")
        
#         # Initialize chat history (only for new city or first time)
#         chat_key = f"chat_messages_{city}"
#         if chat_key not in st.session_state:
#             st.session_state[chat_key] = []
#             # Add a welcome message
#             welcome_msg = f"Hello! I'm your AQI Health Advisor. The current air quality in {city} is {current_aqi:.1f} ({aqi_status}). How can I help you today?"
#             st.session_state[chat_key].append({"role": "assistant", "content": welcome_msg})
        
#         # Display chat history
#         for message in st.session_state[chat_key]:
#             with st.chat_message(message["role"]):
#                 st.markdown(message["content"])
        
#         # Chat input
#         if prompt := st.chat_input("Ask about air quality, health advice, or forecast..."):
#             # Add user message to chat history
#             st.session_state[chat_key].append({"role": "user", "content": prompt})
#             with st.chat_message("user"):
#                 st.markdown(prompt)
            
#             # Generate response
#             with st.chat_message("assistant"):
#                 with st.spinner("Thinking..."):
#                     # Get forecasted AQI values for context
#                     forecasted_aqi = forecast_df['predicted_AQI'].tolist()
                    
#                     try:
#                         response = get_aqi_advice(
#                             forecasted_aqi=forecasted_aqi,
#                             user_health_issues=prompt,
#                             current_aqi=current_aqi,
#                             city=city
#                         )
#                         st.markdown(response)
                        
#                         # Add assistant response to chat history
#                         st.session_state[chat_key].append({"role": "assistant", "content": response})
#                     except Exception as e:
#                         error_msg = f"Sorry, I encountered an error: {str(e)}. Please try rephrasing your question."
#                         st.markdown(error_msg)
#                         st.session_state[chat_key].append({"role": "assistant", "content": error_msg})
        
#         # Suggested questions
#         st.markdown("### 💡 Suggested Questions:")
#         col1, col2 = st.columns(2)
        
#         suggested_questions = [
#             "What precautions should I take today?",
#             "Is it safe to exercise outdoors?",
#             "I have asthma, what should I do?",
#             "How will air quality change this week?",
#             "What indoor air purification tips do you have?",
#             "Should I avoid outdoor activities?"
#         ]
        
#         for i, question in enumerate(suggested_questions):
#             col = col1 if i % 2 == 0 else col2
#             with col:
#                 if st.button(question, key=f"suggest_{i}"):
#                     # Add the suggested question as if user typed it
#                     st.session_state[chat_key].append({"role": "user", "content": question})
                    
#                     # Get response
#                     forecasted_aqi = forecast_df['predicted_AQI'].tolist()
#                     try:
#                         response = get_aqi_advice(
#                             forecasted_aqi=forecasted_aqi,
#                             user_health_issues=question,
#                             current_aqi=current_aqi,
#                             city=city
#                         )
#                         st.session_state[chat_key].append({"role": "assistant", "content": response})
#                     except Exception as e:
#                         error_msg = f"Sorry, I encountered an error: {str(e)}."
#                         st.session_state[chat_key].append({"role": "assistant", "content": error_msg})
                    
#                     st.rerun()
        
#         # Clear chat button
#         col1, col2 = st.columns([1, 4])
#         with col1:
#             if st.button("🗑️ Clear Chat"):
#                 st.session_state[chat_key] = []
#                 st.rerun()
                
#     else:
#         st.error("Failed to load AQI data. Please try searching again.")

# elif city:
#     st.info("👆 Click 'Get AQI Data' to load air quality information for your city.")
# else:
#     st.info("👆 Please enter a city name to get started.")
    
#     # Show some example cities
#     st.markdown("### 🌟 Popular Cities")
#     example_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad"]
#     cols = st.columns(len(example_cities))
    
#     for i, example_city in enumerate(example_cities):
#         with cols[i]:
#             if st.button(example_city, key=f"example_{i}"):
#                 st.session_state.city_input = example_city
#                 st.rerun()

# # ---------------------- Footer ----------------------
# st.markdown("---")
# st.markdown("*Data provided by OpenWeatherMap Air Pollution API. Forecasts generated using LSTM neural networks.*")


# -----------------------------------------------------


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

# Load API Key
load_dotenv(dotenv_path=".env")
api_key = os.getenv("API_KEY")

# ---------------------- Dashboard Configuration ----------------------
st.set_page_config(page_title="AQI Dashboard", layout="wide")
st.title("🌍 Air Quality Monitoring Dashboard")
st.markdown("Track air quality trends, evaluate health risks, and receive precautionary insights in real-time.")

# ---------------------- City Input (Main Area) ----------------------
st.header("📍 Enter Your Location")
col1, col2 = st.columns([2, 1])

with col1:
    city = st.text_input("City name", value="Thane", placeholder="Enter city name...")

with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
    search_button = st.button("🔍 Get AQI Data", type="primary")

# ---------------------- Main Dashboard Content ----------------------
if city and (search_button or st.session_state.get('basic_data_loaded', False)):
    
    # Check if we need to reload basic data (city changed or first time)
    need_basic_reload = (
        not st.session_state.get('basic_data_loaded', False) or 
        st.session_state.get('current_city', '') != city or
        search_button
    )
    
    if need_basic_reload:
        # Set flags
        st.session_state.basic_data_loaded = True
        st.session_state.current_city = city
        
        try:
            # 1. Get coordinates
            with st.spinner("Getting location coordinates..."):
                latitude, longitude, country, state = get_lat_lon(api_key, city)
                # Cache coordinates
                st.session_state.coordinates = {
                    'latitude': latitude,
                    'longitude': longitude,
                    'country': country,
                    'state': state
                }
            
            # 2. Fetch current AQI data (last 24 hours for current reading)
            with st.spinner("Fetching current air quality data..."):
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
                    st.error(f"Failed to fetch data: {resp.status_code}")
                    st.stop()

            # 3. Process current data
            with st.spinner("Processing current air quality data..."):
                data = resp.json()
                current_df = pd.json_normalize(data['list'])
                current_df['Overall_AQI'] = current_df.apply(calculate_overall_aqi, axis=1)
                current_df['dt'] = pd.to_datetime(current_df['dt'], unit='s', utc=True).map(lambda x: x.tz_convert('Asia/Kolkata'))
                current_df['dt'] = current_df['dt'].dt.strftime('%Y-%m-%d %H:%M:%S')
                current_df['dt'] = pd.to_datetime(current_df['dt'])
                current_df = current_df.reset_index(drop=True)
                
                # Cache the current dataframe
                st.session_state.current_aqi_df = current_df
                
        except Exception as e:
            st.error(f"An error occurred while loading data: {str(e)}")
            st.markdown("Please try again or check your city name.")
            st.stop()
    
    # Use cached data if available
    if 'current_aqi_df' in st.session_state:
        current_df = st.session_state.current_aqi_df
        coordinates = st.session_state.coordinates
        
        # Display location info
        st.success(f"📍 **{city}, {coordinates['state']}, {coordinates['country']}** (Lat: {coordinates['latitude']}, Lon: {coordinates['longitude']})")

        # ---------------------- Current AQI Display (MOVED TO TOP) ----------------------
        st.header("📊 Current Air Quality")
        
        current_aqi = current_df['Overall_AQI'].iloc[-1]
        
        # Get AQI status using the chatbot function
        aqi_status, aqi_color = get_aqi_category(current_aqi)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current AQI", f"{current_aqi:.1f}")
        with col2:
            st.metric("Status", aqi_status)
        with col3:
            st.metric("Last Updated", current_df['dt'].iloc[-1].strftime("%Y-%m-%d %H:%M"))

        # ---------------------- Chatbot Interface (ALWAYS VISIBLE) ----------------------
        st.header("🤖 AQI Health Advisor Chat")
        st.markdown("Ask questions about air quality, health impacts, or get personalized advice.")
        
        # Initialize chat history (only for new city or first time)
        chat_key = f"chat_messages_{city}"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []
            # Add a welcome message
            welcome_msg = f"Hello! I'm your AQI Health Advisor. The current air quality in {city} is {current_aqi:.1f} ({aqi_status}). How can I help you today?"
            st.session_state[chat_key].append({"role": "assistant", "content": welcome_msg})
        
        # Display chat history
        for message in st.session_state[chat_key]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about air quality, health advice, or general information..."):
            # Add user message to chat history
            st.session_state[chat_key].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Use empty forecast list if forecast not available
                        forecasted_aqi = st.session_state.get('forecast_df', {}).get('predicted_AQI', []) if 'forecast_df' in st.session_state else []
                        
                        response = get_aqi_advice(
                            forecasted_aqi=forecasted_aqi,
                            user_health_issues=prompt,
                            current_aqi=current_aqi,
                            city=city
                        )
                        st.markdown(response)
                        
                        # Add assistant response to chat history
                        st.session_state[chat_key].append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"Sorry, I encountered an error: {str(e)}. Please try rephrasing your question."
                        st.markdown(error_msg)
                        st.session_state[chat_key].append({"role": "assistant", "content": error_msg})
        
        # Suggested questions
        st.markdown("### 💡 Suggested Questions:")
        col1, col2 = st.columns(2)
        
        suggested_questions = [
            "What precautions should I take today?",
            "Is it safe to exercise outdoors?",
            "I have asthma, what should I do?",
            "What indoor air purification tips do you have?",
            "Should I avoid outdoor activities?",
            "What does this AQI level mean for my health?"
        ]
        
        for i, question in enumerate(suggested_questions):
            col = col1 if i % 2 == 0 else col2
            with col:
                if st.button(question, key=f"suggest_{i}"):
                    # Add the suggested question as if user typed it
                    st.session_state[chat_key].append({"role": "user", "content": question})
                    
                    # Get response
                    try:
                        forecasted_aqi = st.session_state.get('forecast_df', {}).get('predicted_AQI', []) if 'forecast_df' in st.session_state else []
                        response = get_aqi_advice(
                            forecasted_aqi=forecasted_aqi,
                            user_health_issues=question,
                            current_aqi=current_aqi,
                            city=city
                        )
                        st.session_state[chat_key].append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"Sorry, I encountered an error: {str(e)}."
                        st.session_state[chat_key].append({"role": "assistant", "content": error_msg})
                    
                    st.rerun()
        
        # Clear chat button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state[chat_key] = []
                st.rerun()

        # ---------------------- Optional LSTM Forecast Section ----------------------
        st.header("🔮 Advanced 7-Day Forecast")
        st.markdown("Generate detailed forecasts using machine learning models (may take a moment to process)")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**LSTM Neural Network Forecast** - Get predictions for the next 7 days based on historical patterns")
        with col2:
            forecast_button = st.button("📈 Generate LSTM Forecast", type="secondary")
        
        # Check if forecast should be generated
        if forecast_button or st.session_state.get('forecast_requested', False):
            if forecast_button:
                st.session_state.forecast_requested = True
                # Clear any existing forecast data when new forecast is requested
                if 'forecast_df' in st.session_state:
                    del st.session_state.forecast_df
                if 'model_metrics' in st.session_state:
                    del st.session_state.model_metrics
            
            # Only generate forecast if not already cached
            if 'forecast_df' not in st.session_state:
                try:
                    # First, we need full historical data for LSTM training
                    with st.spinner("Fetching extended historical data for model training..."):
                        curr_ts = int(datetime.now().timestamp())
                        half_years_ago_ts = curr_ts - (180 * 24 * 3600)
                        resp = requests.get(
                            "http://api.openweathermap.org/data/2.5/air_pollution/history",
                            params={
                                "lat": coordinates['latitude'],
                                "lon": coordinates['longitude'],
                                "start": half_years_ago_ts,
                                "end": curr_ts,
                                "appid": api_key
                            }
                        )
                        
                        if resp.status_code != 200:
                            st.error(f"Failed to fetch historical data for forecast: {resp.status_code}")
                        else:
                            # Process full historical data
                            with st.spinner("Processing historical data..."):
                                data = resp.json()
                                pd.json_normalize(data['list']).to_csv('air_pollution_data.csv', index=False)
                                df = pd.read_csv('air_pollution_data.csv')
                                df['Overall_AQI'] = df.apply(calculate_overall_aqi, axis=1)
                                df['dt'] = pd.to_datetime(df['dt'], unit='s', utc=True).map(lambda x: x.tz_convert('Asia/Kolkata'))
                                df['dt'] = df['dt'].dt.strftime('%Y-%m-%d %H:%M:%S')
                                df['dt'] = pd.to_datetime(df['dt'])
                                df = df.reset_index(drop=True)
                                df.to_csv('air_pollution_data_AQI.csv', index=False)
                            
                            # Generate forecast
                            with st.spinner("Training LSTM model and generating forecast..."):
                                rmse, mae = forecast_future_LSTM()
                                forecast_df = pd.read_csv("forecast_LSTM_AQI.csv")
                                
                                # Cache forecast data and metrics
                                st.session_state.forecast_df = forecast_df
                                st.session_state.model_metrics = {'rmse': rmse, 'mae': mae}
                                
                except Exception as e:
                    st.error(f"An error occurred while generating forecast: {str(e)}")
                    st.session_state.forecast_requested = False
            
            # Display forecast if available
            if 'forecast_df' in st.session_state and 'model_metrics' in st.session_state:
                forecast_df = st.session_state.forecast_df
                model_metrics = st.session_state.model_metrics
                
                st.success("✅ Forecast generated successfully!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Model RMSE", f"{model_metrics['rmse']:.2f}")
                with col2:
                    st.metric("Model MAE", f"{model_metrics['mae']:.2f}")
                
                # Display forecast chart
                st.subheader("📈 Forecasted AQI Trend")
                st.line_chart(forecast_df.set_index('timestamp')['predicted_AQI'])
                
                # Show forecast summary
                avg_forecast = forecast_df['predicted_AQI'].mean()
                max_forecast = forecast_df['predicted_AQI'].max()
                min_forecast = forecast_df['predicted_AQI'].min()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("7-Day Average", f"{avg_forecast:.1f}")
                with col2:
                    st.metric("Forecast Max", f"{max_forecast:.1f}")
                with col3:
                    st.metric("Forecast Min", f"{min_forecast:.1f}")
                
        else:
            st.info("Click the button above to generate detailed forecasts using machine learning models.")
                
    else:
        st.error("Failed to load AQI data. Please try searching again.")

elif city:
    st.info("👆 Click 'Get AQI Data' to load air quality information for your city.")
    
    # ---------------------- General Chatbot (No City Data) ----------------------
    st.header("🤖 AQI Health Advisor Chat")
    st.markdown("Ask general questions about air quality and health. Enter a city above for personalized advice.")
    
    # Initialize general chat history
    general_chat_key = "general_chat_messages"
    if general_chat_key not in st.session_state:
        st.session_state[general_chat_key] = []
        welcome_msg = "Hello! I'm your AQI Health Advisor. I can answer general questions about air quality and health. For personalized advice, please enter a city name above and get AQI data first."
        st.session_state[general_chat_key].append({"role": "assistant", "content": welcome_msg})
    
    # Display general chat history
    for message in st.session_state[general_chat_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # General chat input
    if prompt := st.chat_input("Ask general questions about air quality and health..."):
        # Add user message to chat history
        st.session_state[general_chat_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response for general questions
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = get_aqi_advice(
                        forecasted_aqi=[],
                        user_health_issues=prompt,
                        current_aqi=None,
                        city="your location"
                    )
                    st.markdown(response)
                    st.session_state[general_chat_key].append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}. Please try rephrasing your question."
                    st.markdown(error_msg)
                    st.session_state[general_chat_key].append({"role": "assistant", "content": error_msg})
    
    # General suggested questions
    st.markdown("### 💡 General Questions:")
    col1, col2 = st.columns(2)
    
    general_questions = [
        "What is AQI and how is it calculated?",
        "What are the health effects of air pollution?",
        "How can I protect myself from bad air quality?",
        "What are the main air pollutants?",
        "Best indoor air purification methods?",
        "How does weather affect air quality?"
    ]
    
    for i, question in enumerate(general_questions):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.button(question, key=f"general_suggest_{i}"):
                st.session_state[general_chat_key].append({"role": "user", "content": question})
                try:
                    response = get_aqi_advice(
                        forecasted_aqi=[],
                        user_health_issues=question,
                        current_aqi=None,
                        city="your location"
                    )
                    st.session_state[general_chat_key].append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}."
                    st.session_state[general_chat_key].append({"role": "assistant", "content": error_msg})
                st.rerun()
    
    # Clear general chat button
    if st.button("🗑️ Clear Chat", key="clear_general_chat"):
        st.session_state[general_chat_key] = []
        st.rerun()

else:
    st.info("👆 Please enter a city name to get started.")
    
    # Show some example cities
    st.markdown("### 🌟 Popular Cities")
    example_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad"]
    cols = st.columns(len(example_cities))
    
    for i, example_city in enumerate(example_cities):
        with cols[i]:
            if st.button(example_city, key=f"example_{i}"):
                st.session_state.city_input = example_city
                st.rerun()
    
    # ---------------------- General Chatbot (No City Data) ----------------------
    st.header("🤖 AQI Health Advisor Chat")
    st.markdown("Ask general questions about air quality and health. Enter a city above for personalized advice.")
    
    # Initialize general chat history
    general_chat_key = "general_chat_messages"
    if general_chat_key not in st.session_state:
        st.session_state[general_chat_key] = []
        welcome_msg = "Hello! I'm your AQI Health Advisor. I can answer general questions about air quality and health. For personalized advice, please enter a city name above and get AQI data first."
        st.session_state[general_chat_key].append({"role": "assistant", "content": welcome_msg})
    
    # Display general chat history
    for message in st.session_state[general_chat_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # General chat input
    if prompt := st.chat_input("Ask general questions about air quality and health..."):
        # Add user message to chat history
        st.session_state[general_chat_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response for general questions
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = get_aqi_advice(
                        forecasted_aqi=[],
                        user_health_issues=prompt,
                        current_aqi=None,
                        city="your location"
                    )
                    st.markdown(response)
                    st.session_state[general_chat_key].append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}. Please try rephrasing your question."
                    st.markdown(error_msg)
                    st.session_state[general_chat_key].append({"role": "assistant", "content": error_msg})
    
    # General suggested questions
    st.markdown("### 💡 General Questions:")
    col1, col2 = st.columns(2)
    
    general_questions = [
        "What is AQI and how is it calculated?",
        "What are the health effects of air pollution?",
        "How can I protect myself from bad air quality?",
        "What are the main air pollutants?",
        "Best indoor air purification methods?",
        "How does weather affect air quality?"
    ]
    
    for i, question in enumerate(general_questions):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.button(question, key=f"general_suggest_{i}_bottom"):
                st.session_state[general_chat_key].append({"role": "user", "content": question})
                try:
                    response = get_aqi_advice(
                        forecasted_aqi=[],
                        user_health_issues=question,
                        current_aqi=None,
                        city="your location"
                    )
                    st.session_state[general_chat_key].append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}."
                    st.session_state[general_chat_key].append({"role": "assistant", "content": error_msg})
                st.rerun()
    
    # Clear general chat button
    if st.button("🗑️ Clear Chat", key="clear_general_chat_bottom"):
        st.session_state[general_chat_key] = []
        st.rerun()

# ---------------------- Footer ----------------------
st.markdown("---")
st.markdown("*Data provided by OpenWeatherMap Air Pollution API. Forecasts generated using LSTM neural networks.*")