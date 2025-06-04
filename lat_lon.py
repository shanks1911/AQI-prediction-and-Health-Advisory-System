from dotenv import load_dotenv
import os
import requests
from requests.exceptions import ConnectionError

load_dotenv(dotenv_path = '.env')

api_key = os.getenv('API_KEY')

# city = str(input("Enter the name of the city: "))

def get_lat_lon(api_key, city):
    url = "http://api.openweathermap.org/geo/1.0/direct?"
    params = {
        'q': city,
        'limit': 1,
        'appid': api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        data = response.json()
        latitude = data[0]['lat']
        longitude = data[0]['lon']
        country = data[0]['country']
        state = data[0]['state']

        return (latitude, longitude, country, state)

    except ConnectionError:
        print("Failed to connect to the API. Please check your internet connection and try again.")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")

# print(get_lat_lon(api_key, city))