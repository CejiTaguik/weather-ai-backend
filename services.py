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
        if response.status_code != 200:
            return {"error": f"Weather API request failed with status {response.status_code}: {response.text}"}
        
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
    blynk_data = {
        "V11": temperature,  # Temperature
        "V12": humidity,     # Humidity
        "V10": pressure,     # Pressure
        "V13": uv_index,     # UV Index
        "V8": latitude,      # Latitude
        "V9": longitude      # Longitude
    }

    try:
        for pin, value in blynk_data.items():
            response = requests.get(f"{blynk_url}?token={auth_token}&{pin}={value}", timeout=5)
            if response.status_code != 200:
                return {"error": f"Failed to send {pin} to Blynk: {response.text}"}
        
        return {"message": "Weather data sent to Blynk successfully"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to send data to Blynk: {str(e)}"}
