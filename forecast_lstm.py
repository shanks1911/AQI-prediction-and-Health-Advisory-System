from tensorflow import keras
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
import seaborn as sns
from datetime import datetime

def forecast_future_LSTM():
    data = pd.read_csv('air_pollution_data_AQI.csv')
    # print(data.head())
    # print(data.describe())
    # print(data.info())

    # numerical columns
    numerical_cols = data.select_dtypes(include=["float64", "int64"])

    # plt.figure(figsize=(10, 6))
    # sns.heatmap(numerical_cols.corr(), annot=True, fmt=".2f", cmap='coolwarm')
    # plt.title('Correlation Heatmap')
    # plt.savefig('correlation_heatmap.png')

    data['date'] = pd.to_datetime(data['dt'])
    # print(data.info())

    # Features
    feature_cols = ['components.co', 'components.no', 'components.no2',
                    'components.o3', 'components.so2', 'components.pm2_5',
                    'components.pm10', 'components.nh3']
    # Target variable
    target_col = 'Overall_AQI'

    # Usse MinMaxScaler to scale the features and target variable, result between 0-1
    scaler_x = MinMaxScaler()
    scaler_y = MinMaxScaler()

    # Scale the features and return a numpy array
    x_scaled = scaler_x.fit_transform(data[feature_cols]) 
    y_scaled = scaler_y.fit_transform(data[[target_col]])

    # Sliding Window to create sequences to train the model
    def create_sequences(X , y , input_window, forecast_horizon):
        Xs, ys = [], []
        for i in range(len(X) - input_window - forecast_horizon + 1):
            Xs.append(X[i:i + input_window])
            ys.append(y[i + input_window:i + input_window + forecast_horizon].flatten())
        return np.array(Xs), np.array(ys)

    input_window = 240 # 96 time steps (4 days with 24 hours)
    forecast_horizon = 168 # 168 time steps (7 days with 24 hours)

    X_sequences, y_sequences = create_sequences(x_scaled, y_scaled, input_window, forecast_horizon)

    # print(X_sequences)
    # print(X_sequences.shape)
    # print(y_sequences)
    # print(y_sequences.shape)

    split = int(0.95*len(X_sequences))
    X_train, X_test = X_sequences[:split], X_sequences[split:]
    y_train, y_test = y_sequences[:split], y_sequences[split:]

    # Building model
    model = keras.Sequential()
    num_features = len(feature_cols)

    # Input Layer
    model.add(keras.Input(shape=(input_window, num_features)))

    # First layer - LSTM Layer
    model.add(keras.layers.LSTM(64, return_sequences = True))

    # Second layer - LSTM Layer
    model.add(keras.layers.LSTM(64, return_sequences=False))

    # Third Layer (Dense Layer)
    model.add(keras.layers.Dense(128, activation='relu'))

    # Fourth Layer
    model.add(keras.layers.Dropout(0.4))

    # Fifth Layer - Output Layer
    model.add(keras.layers.Dense(168))

    model.summary()

    # Compile the model
    model.compile(optimizer='adam',
                loss='mae',
                metrics=[keras.metrics.RootMeanSquaredError()])

    # train the model
    history = model.fit(
        X_train, y_train,
        epochs = 20, 
        batch_size = 32
    )

    loss, mae = model.evaluate(X_test, y_test)
    print(f"Test Loss: {loss:.4f}, MAE: {mae:.4f}")

    y_pred = model.predict(X_test)  # shape: (191, 168)

    y_pred_original = scaler_y.inverse_transform(y_pred)
    y_test_original = scaler_y.inverse_transform(y_test)

    # idx = 0  # test sample index
    # plt.figure(figsize=(12, 5))
    # plt.plot(y_test_original[idx], label='Actual AQI')
    # plt.plot(y_pred_original[idx], label='Predicted AQI')
    # plt.title("7-Day Hourly AQI Forecast")
    # plt.xlabel("Hour")
    # plt.ylabel("AQI")
    # plt.legend()
    # plt.grid(True)
    # plt.show()

    # # Recalculate metrics
    rmse = np.sqrt(mean_squared_error(y_test_original, y_pred_original))
    mae = mean_absolute_error(y_test_original, y_pred_original)

    print(f"Real RMSE: {rmse:.2f}, Real MAE: {mae:.2f}")

    # storing data in forecast_LSTM_AQI.csv
    last_timestamp = data['date'].iloc[-1]
    forecast_timestamps = pd.date_range(start=last_timestamp + pd.Timedelta(hours=1), periods=168, freq='H')

    latest_input = X_test[-1].reshape(1, input_window, num_features)
    latest_pred = model.predict(latest_input)
    latest_pred_original = scaler_y.inverse_transform(latest_pred)[0]  # shape: (168,)

    # Create a DataFrame with timestamp and predicted AQI
    forecast_df = pd.DataFrame({
        'timestamp': forecast_timestamps,
        'predicted_AQI': latest_pred_original
    })

    # Save to CSV
    forecast_df.to_csv("forecast_LSTM_AQI.csv", index=False)
    print("Forecast saved to 'forecast_LSTM_AQI.csv'")

    return rmse, mae