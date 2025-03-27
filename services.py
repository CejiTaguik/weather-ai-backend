import requests
import os

BLYNK_URL = "https://blynk.cloud/external/api/update"
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

def get_weather_data(latitude: float, longitude: float):
    """Fetch weather data from Open-Meteo API with improved error handling."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,pressure_msl,uv_index",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }

    try:
        response = requests.get(WEATHER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        weather_data = response.json()

        if "current" not in weather_data:
            return {"error": "Invalid response from Weather API"}

        return weather_data
    except requests.RequestException as e:
        return {"error": f"Failed to fetch weather data: {str(e)}"}

def send_weather_to_blynk(temperature: float, humidity: float, pressure: float, uv_index: float, latitude: float, longitude: float):
    """Send weather data to Blynk virtual pins with improved reliability."""
    auth_token = os.getenv("BLYNK_AUTH_TOKEN")
    if not auth_token:
        return {"error": "Blynk authentication token is missing"}

    params = {
        "token": auth_token,
        "V11": temperature,  # Temperature
        "V12": humidity,     # Humidity
        "V10": pressure,     # Pressure
        "V13": uv_index,     # UV Index
        "V8": latitude,      # Latitude
        "V9": longitude      # Longitude
    }

    try:
        response = requests.get(BLYNK_URL, params=params, timeout=5)
        response.raise_for_status()
        return {"message": "Weather data sent to Blynk successfully"}
    except requests.RequestException as e:
        return {"error": f"Failed to send data to Blynk: {str(e)}"}
