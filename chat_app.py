import streamlit as st
import pandas as pd
from chatbot import get_aqi_advice  # Make sure this imports correctly
from datetime import datetime

# Streamlit app setup
st.set_page_config(page_title="AQI Health Chatbot", page_icon="🌬️")
st.title("💬 AQI Health Risk Chatbot")
st.markdown("Ask health-related questions based on forecasted AQI conditions.")

# Load forecast data
@st.cache_data
def load_forecast_data():
    df = pd.read_csv("forecast_LSTM_AQI.csv")
    return df['predicted_AQI'].tolist()

forecasted_aqi = load_forecast_data()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your AQI health advisor. Let me know your health concerns or ask how AQI might affect you."}
    ]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input field
user_input = st.chat_input("Describe your health concern or ask for AQI advice...")

if user_input:
    # Append user message to session
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call GPT-based advisor
    with st.spinner("Analyzing air quality forecast..."):
        try:
            assistant_response = get_aqi_advice(forecasted_aqi, user_input)
        except Exception as e:
            assistant_response = f"⚠️ Failed to get advice: {e}"

    # Append assistant response
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
