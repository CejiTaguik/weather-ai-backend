import os
import requests
import logging
from fastapi import APIRouter, Query
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Blynk setup
BLYNK_AUTH_TOKEN = os.getenv("BLYNK_AUTH_TOKEN")
BLYNK_SERVER = "https://blynk.cloud/external/api/update"
BLYNK_GET_SERVER = "https://blynk.cloud/external/api/get"

# Create router
router = APIRouter()

# ✅ Function to send data to Blynk
def send_to_blynk(pin: str, value: str):
    if not BLYNK_AUTH_TOKEN:
        return {"error": "BLYNK_AUTH_TOKEN is missing"}
    url = f"{BLYNK_SERVER}?token={BLYNK_AUTH_TOKEN}&{pin}={value}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return {"error": f"Exception: {str(e)}"}

# ✅ Function to fetch data from Blynk
@router.get("/fetch_blynk_data")
async def fetch_blynk_data():
    """ Fetches data from Blynk Virtual Pin V6 """
    if not BLYNK_AUTH_TOKEN:
        return {"error": "BLYNK_AUTH_TOKEN is missing"}

    url = f"{BLYNK_GET_SERVER}?token={BLYNK_AUTH_TOKEN}&V6"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        logging.info(f"Blynk API Response: {response.text}")
        return {"blynk_data": response.text}
    except requests.RequestException as e:
        logging.error(f"Error fetching Blynk data: {e}")
        return {"error": f"Request failed: {str(e)}"}

# ✅ Convert location to lat/lon
def get_lat_lon_from_location(location: str):
    """ Converts a location name to latitude & longitude using Open-Meteo API """
    try:
        response = requests.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": location, "count": 1})
        response.raise_for_status()
        data = response.json()
        if "results" in data and data["results"]:
            return data["results"][0]["latitude"], data["results"][0]["longitude"]
    except requests.RequestException:
        return None, None

# ✅ Function to fetch weather data (Updates Blynk)
def get_weather_data(latitude: float, longitude: float):
    try:
        api_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,pressure_msl,uv_index",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto"
        }
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        weather_data = response.json()

        if "current" not in weather_data or not isinstance(weather_data["current"], dict):
            return {"error": "Invalid weather API response"}

        # Extracting weather values
        temperature = weather_data["current"].get("temperature_2m", "N/A")
        humidity = weather_data["current"].get("relative_humidity_2m", "N/A")
        pressure = weather_data["current"].get("pressure_msl", "N/A")
        uv_index = weather_data["current"].get("uv_index", "N/A")

        # ✅ Send data to Blynk with correct Virtual Pins
        blynk_results = {
            "latitude": send_to_blynk("V8", str(latitude)),
            "longitude": send_to_blynk("V9", str(longitude)),
            "pressure": send_to_blynk("V10", str(pressure)),
            "temperature": send_to_blynk("V11", str(temperature)),
            "humidity": send_to_blynk("V12", str(humidity)),
            "uv_index": send_to_blynk("V13", str(uv_index)),
            "location": send_to_blynk("V6", f"{latitude}, {longitude}"),
            "weather_fetch": send_to_blynk("V7", "1")  # Indicate successful fetch
        }

        return {"weather": weather_data, "blynk_results": blynk_results}
    except requests.RequestException as e:
        return {"error": f"Weather API request failed: {str(e)}"}

# ✅ AI Recommendation Endpoint
@router.get("/recommendation")
def fetch_recommendation(query: str = Query(...), location: str = Query(None), latitude: float = Query(None), longitude: float = Query(None)):
    if location:
        latitude, longitude = get_lat_lon_from_location(location)
        if latitude is None or longitude is None:
            return {"error": "Invalid location"}

    if latitude is None or longitude is None:
        return {"error": "Latitude and longitude are required"}

    return generate_recommendation(query, latitude, longitude)

# ✅ Weather Endpoint (Supports Both Lat/Lon & Location Name)
@router.get("/weather")
def fetch_weather(location: str = Query(None), latitude: float = Query(None), longitude: float = Query(None)):
    if location:
        latitude, longitude = get_lat_lon_from_location(location)
        if latitude is None or longitude is None:
            return {"error": "Invalid location"}

    if latitude is None or longitude is None:
        return {"error": "Latitude and longitude are required"}

    return get_weather_data(latitude, longitude)

# ✅ Blynk Test Endpoint
@router.get("/blynk/test")
def test_blynk():
    response = send_to_blynk("V14", "Hello from FastAPI")
    return {"blynk_response": response}

# ✅ Send Custom Data to Blynk
@router.get("/blynk/send")
def send_blynk_data(pin: str = Query(...), value: str = Query(...)):
    response = send_to_blynk(pin, value)
    return {"blynk_response": response}
