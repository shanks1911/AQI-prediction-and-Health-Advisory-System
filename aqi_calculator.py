def calculate_aqi_pm25(pm25_value):
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

# Overall AQI calculation
def calculate_overall_aqi(row):
    # Calculate AQI for each pollutant
    aqi_values = [
        calculate_aqi_pm25(row['components.pm2_5']),
        calculate_aqi_pm10(row['components.pm10']),
        calculate_aqi_co(row['components.co']),
        calculate_aqi_no2(row['components.no']),
        calculate_aqi_so2(row['components.so2']),
        calculate_aqi_o3(row['components.o3']),
        calculate_aqi_nh3(row['components.nh3'])
    ]
    
    # Filter out None values
    aqi_values = [aqi for aqi in aqi_values if aqi is not None]
    
    # Return the maximum AQI value, or None if no valid AQI values
    return max(aqi_values) if aqi_values else None