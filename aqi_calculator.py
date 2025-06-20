import pandas as pd
import numpy as np

def calculate_aqi_pm25(pm25_value):
    # Handle NaN or None values
    if pd.isna(pm25_value) or pm25_value is None:
        return None
    
    breakpoints = [
        (0, 30, 0, 50),
        (31, 60, 51, 100),
        (61, 90, 101, 200),
        (91, 120, 201, 300),
        (121, 250, 301, 400),
        (251, 350, 401, 500)
    ]
    
    for low, high, low_aqi, high_aqi in breakpoints:
        if low <= pm25_value <= high:
            return int(((pm25_value - low) / (high - low)) * (high_aqi - low_aqi) + low_aqi)
    return None

def calculate_aqi_pm10(pm10_value):
    # Handle NaN or None values
    if pd.isna(pm10_value) or pm10_value is None:
        return None
    
    breakpoints = [
        (0, 50, 0, 50),
        (51, 100, 51, 100),
        (101, 250, 101, 200),
        (251, 350, 201, 300),
        (351, 430, 301, 400),
        (431, 530, 401, 500)
    ]
    
    for low, high, low_aqi, high_aqi in breakpoints:
        if low <= pm10_value <= high:
            return int(((pm10_value - low) / (high - low)) * (high_aqi - low_aqi) + low_aqi)
    return None

def calculate_aqi_co(co_value):
    # Handle NaN or None values
    if pd.isna(co_value) or co_value is None:
        return None
    
    co_mg_m3 = co_value / 1000
    breakpoints = [
        (0.0, 1.0,   0,  50),
        (1.1, 2.0,  51, 100),
        (2.1, 10.0, 101, 200),
        (10.1, 17.0, 201, 300),
        (17.1, 34.0, 301, 400),
        (34.1, 50.0, 401, 500)
    ]
    
    for low, high, low_aqi, high_aqi in breakpoints:
        if low <= co_mg_m3 <= high:
            return int(((co_mg_m3 - low) / (high - low)) * (high_aqi - low_aqi) + low_aqi)
    return None

def calculate_aqi_no2(no2_value):
    # Handle NaN or None values
    if pd.isna(no2_value) or no2_value is None:
        return None
    
    breakpoints = [
        (0, 40, 0, 50),
        (41, 80, 51, 100),
        (81, 180, 101, 150),
        (181, 280, 151, 200),
        (281, 400, 201, 300),
        (401, 800, 301, 400),
        (801, 1200, 401, 500)
    ]
    
    for low, high, low_aqi, high_aqi in breakpoints:
        if low <= no2_value <= high:
            return int(((no2_value - low) / (high - low)) * (high_aqi - low_aqi) + low_aqi)
    return None

def calculate_aqi_so2(so2_value):
    # Handle NaN or None values
    if pd.isna(so2_value) or so2_value is None:
        return None
    
    breakpoints = [
        (0, 40, 0, 50),
        (41, 80, 51, 100),
        (81, 380, 101, 150),
        (381, 800, 151, 200),
        (801, 1600, 201, 300),
        (1601, 2100, 301, 400),
        (2101, 2620, 401, 500)
    ]
    
    for low, high, low_aqi, high_aqi in breakpoints:
        if low <= so2_value <= high:
            return int(((so2_value - low) / (high - low)) * (high_aqi - low_aqi) + low_aqi)
    return None

def calculate_aqi_o3(o3_value):
    # Handle NaN or None values
    if pd.isna(o3_value) or o3_value is None:
        return None
    
    breakpoints = [
        (0, 84, 0, 50),
        (84, 124, 51, 100),
        (125, 164, 101, 150),
        (165, 204, 151, 200),
        (205, 404, 201, 300),
        (405, 504, 301, 400),
        (505, 604, 401, 500)
    ]
    
    for low, high, low_aqi, high_aqi in breakpoints:
        if low <= o3_value <= high:
            return int(((o3_value - low) / (high - low)) * (high_aqi - low_aqi) + low_aqi)
    return None

def calculate_aqi_nh3(nh3_value):
    # Handle NaN or None values
    if pd.isna(nh3_value) or nh3_value is None:
        return None
    
    breakpoints = [
        (0, 10, 0, 50),
        (11, 20, 51, 100),
        (21, 30, 101, 150),
        (31, 50, 151, 200),
        (51, 100, 201, 300),
        (101, 200, 301, 500)
    ]
    
    for low, high, low_aqi, high_aqi in breakpoints:
        if low <= nh3_value <= high:
            return int(((nh3_value - low) / (high - low)) * (high_aqi - low_aqi) + low_aqi)
    return None

# Overall AQI calculation with improved error handling
def calculate_overall_aqi(row):
    try:
        # Safely extract values with fallback for missing columns
        pm25_val = row.get('components.pm2_5', None) if hasattr(row, 'get') else getattr(row, 'components.pm2_5', None)
        pm10_val = row.get('components.pm10', None) if hasattr(row, 'get') else getattr(row, 'components.pm10', None)
        co_val = row.get('components.co', None) if hasattr(row, 'get') else getattr(row, 'components.co', None)
        no2_val = row.get('components.no', None) if hasattr(row, 'get') else getattr(row, 'components.no', None)
        so2_val = row.get('components.so2', None) if hasattr(row, 'get') else getattr(row, 'components.so2', None)
        o3_val = row.get('components.o3', None) if hasattr(row, 'get') else getattr(row, 'components.o3', None)
        nh3_val = row.get('components.nh3', None) if hasattr(row, 'get') else getattr(row, 'components.nh3', None)
        
        # Calculate AQI for each pollutant
        aqi_values = [
            calculate_aqi_pm25(pm25_val),
            calculate_aqi_pm10(pm10_val),
            calculate_aqi_co(co_val),
            calculate_aqi_no2(no2_val),
            calculate_aqi_so2(so2_val),
            calculate_aqi_o3(o3_val),
            calculate_aqi_nh3(nh3_val)
        ]
        
        # Filter out None values
        valid_aqi_values = [aqi for aqi in aqi_values if aqi is not None and not pd.isna(aqi)]
        
        # Return the maximum AQI value, or None if no valid AQI values
        if valid_aqi_values:
            return max(valid_aqi_values)
        else:
            return None
            
    except Exception as e:
        print(f"Error calculating AQI for row: {e}")
        return None