import requests
import os

BLYNK_URL = "https://blynk.cloud/external/api/update"

def get_weather_data(latitude, longitude):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,pressure_msl,uv_index"
    response = requests.get(url)
    if response.status_code == 200:
        return {"weather": response.json()}
    return {"error": "Failed to fetch weather data"}

def send_to_blynk(pin, value):
    token = os.getenv("BLYNK_AUTH_TOKEN")
    if not token:
        return {"error": "Blynk token not found"}
    url = f"{BLYNK_URL}?token={token}&{pin}={value}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {"error": "Failed to send data to Blynk"}

def get_lat_lon_from_location(location):
    geocode_url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
    response = requests.get(geocode_url)
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data["lat"]), float(data["lon"])
    return None, None
