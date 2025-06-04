🌫️ AQI Prediction & Health Advisory System
This project is a real-time Air Quality Index (AQI) Forecasting and Health Risk Advisory System that uses deep learning to predict hourly AQI levels for the next 7 days and provides personalized health precautions based on forecasted pollution levels and user health conditions.

🔍 Features
📈 7-Day Hourly AQI Forecast using an LSTM deep learning model

🤖 Streamlit Web App for interactive visualization and advisory

🧠 Health Risk Advisory Bot using OpenAI GPT for:

General precautions based on AQI trends

Tailored advice based on personal health conditions (e.g., asthma, heart disease)

🧠 Tech Stack

| Component         | Technology          |
| ----------------- | ------------------- |
| Forecasting Model | TensorFlow LSTM     |
| Data Handling     | Pandas, NumPy       |
| Visualization     | Matplotlib, Seaborn |
| Web App Interface | Streamlit           |
| Health Advisory   | OpenAI GPT-4 (API)  |
| Forecast Storage  | CSV (for AQI data)  |


📊 Forecasting Model Details
Input: Past 240 hours of pollutant levels (CO, NO, NO2, O3, SO2, PM2.5, PM10, NH3)

Output: AQI predictions for the next 168 hours (7 days)

Model: LSTM with 2 layers + Dense + Dropout

Evaluation: MAE, RMSE

🩺 Health Advisory System
Automatically analyzes predicted AQI values

Provides health recommendations based on AQI severity

Accepts user health issues (e.g., asthma) and generates personalized health precautions