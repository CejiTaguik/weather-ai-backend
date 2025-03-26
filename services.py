import requests
import os

def get_weather_data(latitude: float, longitude: float):
    """Fetch weather data from Open-Meteo API with improved error handling."""
    api_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&current=temperature_2m,relative_humidity_2m,pressure_msl,uv_index"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        f"&timezone=auto"
    )

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors
        weather_data = response.json()

        if "current" not in weather_data:
            return {"error": "Invalid response from Weather API"}

        return weather_data
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch weather data: {str(e)}"}

def send_weather_to_blynk(auth_token: str, temperature: float, humidity: float, pressure: float, uv_index: float, latitude: float, longitude: float):
    """Send weather data to Blynk virtual pins with improved reliability."""
    if not auth_token:
        return {"error": "Blynk authentication token is missing"}

    blynk_url = "https://blynk.cloud/external/api/update"
    
    # Batch update all values in a single request
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
        response = requests.get(blynk_url, params=params, timeout=5)
        response.raise_for_status()  # Ensure the request was successful
        return {"message": "Weather data sent to Blynk successfully"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to send data to Blynk: {str(e)}"}
