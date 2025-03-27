import requests
import os

BLYNK_URL = "https://blynk.cloud/external/api/update"

def get_weather_data(latitude, longitude):
    """Fetch current and daily weather data from Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,pressure_msl,uv_index",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an exception for HTTP errors
        return {"weather": response.json()}
    except requests.RequestException as e:
        return {"error": f"Failed to fetch weather data: {str(e)}"}

def send_to_blynk(pin, value):
    """Send data to Blynk Virtual Pin."""
    token = os.getenv("BLYNK_AUTH_TOKEN")
    if not token:
        return {"error": "Blynk token not found"}
    
    url = f"{BLYNK_URL}?token={token}&{pin}={value}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for HTTP errors
        return response.text  # Blynk returns plain text, not JSON
    except requests.RequestException as e:
        return {"error": f"Failed to send data to Blynk: {str(e)}"}

def get_lat_lon_from_location(location):
    """Convert location name to latitude and longitude using Open-Meteo Geocoding API."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": location, "count": 1}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data and data["results"]:
            return float(data["results"][0]["latitude"]), float(data["results"][0]["longitude"])
        return None, None
    except requests.RequestException as e:
        return None, None
