!pip install python-dotenv
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

from chatbot import get_aqi_advice

# Load API Key
load_dotenv(dotenv_path=".env")
api_key = os.getenv("API_KEY")

# ---------------------- Dashboard Title ----------------------
st.set_page_config(page_title="AQI Dashboard", layout="wide")
st.title("🌍 Air Quality Monitoring Dashboard")
st.markdown("Track air quality trends, evaluate health risks, and receive precautionary insights in real-time.")

# ---------------------- Sidebar Input ----------------------
with st.sidebar:
    st.header("📍 Location Input")
    city = st.text_input("Enter city name", value="Thane")
    st.markdown("This app uses OpenWeatherMap's Air Pollution API to retrieve AQI data.")

# ---------------------- Main Logic ----------------------
if city:
    # 1. Get coords
    latitude, longitude, country, state = get_lat_lon(api_key, city)
    with st.sidebar:
        st.markdown(f"**City:** {city}")
        st.markdown(f"**Country/State:** {country}, {state}")
        st.markdown(f"**Coordinates:** {latitude}, {longitude}")

    # 2. Fetch historical AQI (1/2 years)
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
        st.error(f"Failed to fetch data: {resp.status_code}")
        st.stop()

    # 3. Process raw JSON → CSV → DataFrame
    data = resp.json()
    pd.json_normalize(data['list']).to_csv('air_pollution_data.csv', index=False)
    df = pd.read_csv('air_pollution_data.csv')
    df['Overall_AQI'] = df.apply(calculate_overall_aqi, axis=1)
    df['dt'] = pd.to_datetime(df['dt'], unit='s', utc=True).map(lambda x: x.tz_convert('Asia/Kolkata'))
    df['dt'] = df['dt'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['dt'] = pd.to_datetime(df['dt'])
    df = df.reset_index(drop=True)
    df.to_csv('air_pollution_data_AQI.csv', index=False)

    # 4. Dashboard Display
    st.subheader(f"📊 Current AQI in {city}")
    st.metric("Current AQI", f"{df['Overall_AQI'].iloc[-1]:.2f}")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 AQI Trend", "📋 Last 10 Entries", "📚 Full Dataset", "🔮 Forecasting using LSTM", "🌤️ Full Forecasted Dataset", "🌬️ Health Risk Advisor"
    ])

    with tab1:
        st.subheader("AQI Trend Over Time")
        st.line_chart(df.set_index('dt')['Overall_AQI'])

    with tab2:
        st.subheader("Recent AQI Readings")
        st.table(
            df[['dt', 'Overall_AQI']]
            .tail(10)
            .reset_index(drop=True)
            .style.set_properties(**{'text-align': 'center'})
            .set_table_styles([{"selector": "th", "props": [("text-align", "center")]}])
        )

    with tab3:
        st.subheader("Complete AQI Dataset")
        st.dataframe(df.reset_index(drop=True), use_container_width=True)

    with tab4:
        st.header("🔮 7‑Day Hourly Forecast ")
        st.markdown("This section uses a LSTM model to forecast future AQI values based on historical data.")
        rmse, mae = forecast_future_LSTM()
        st.markdown(f"Model Performance (in AQI): RMSE: {rmse:.2f}, MAE: {mae:.2f}")
        forecast_df = pd.read_csv("forecast_LSTM_AQI.csv")
        st.line_chart(forecast_df.set_index('timestamp')['predicted_AQI'])

    forecast_df = pd.read_csv("forecast_LSTM_AQI.csv")

    with tab5:
        st.subheader("🌤️ Forecasted AQI Data")
        st.table(
            forecast_df[['timestamp', 'predicted_AQI']]
            .rename(columns={'timestamp': 'Date', 'predicted_AQI': 'Predicted AQI'})
            .reset_index(drop=True)
            .style.set_properties(**{'text-align': 'center'})
            .set_table_styles([{"selector": "th", "props": [("text-align", "center")]}])
        )

    with tab6:
        # st.header("🌬️ Health Risk Advisor")
        # st.markdown("Get personalized health advice based on the forecasted AQI.")
        # forecasted_aqi = forecast_df['predicted_AQI'].tolist()

        # # User input for health conditions
        # user_input_health = st.text_input(
        #     "Enter your health conditions (e.g. asthma, heart disease)", 
        #     key="health_input"
        # )

        # # Initialize session state for button click if not already present
        # if "show_advice" not in st.session_state:
        #     st.session_state.show_advice = False

        # # Button logic — set flag in session_state
        # if st.button("Get Health Advisory"):
        #     st.session_state.show_advice = True

        # # Display advice only if flag is True
        # if st.session_state.show_advice:
        #     advice = get_aqi_advice(
        #         forecasted_aqi=forecasted_aqi, 
        #         user_health_issues=user_input_health
        #     )
        #     st.subheader("Health Advisory")
        #     st.write(advice)
        import subprocess
        subprocess.run(["streamlit", "run", "chat_app.py"])
        import webbrowser
        url = "https://zainuddin110.github.io/AQI/"
        webbrowser.open(url)

else:
    st.info("Please enter a city name in the sidebar to begin.")
