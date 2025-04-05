

import os
import requests
from fastapi import APIRouter, Query, HTTPException, Body
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Blynk setup
BLYNK_AUTH_TOKEN = os.getenv("BLYNK_AUTH_TOKEN")
BLYNK_SERVER = "https://blynk.cloud/external/api/update"
BLYNK_EVENT_URL = "https://blynk.cloud/external/api/logEvent"

# Ensure OpenAI API Key is available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing. Please set it in your environment.")

# Create router
router = APIRouter()

def send_to_blynk(pin: str, value: str):
    if not BLYNK_AUTH_TOKEN:
        raise HTTPException(status_code=500, detail="BLYNK_AUTH_TOKEN is missing")
    
    url = f"{BLYNK_SERVER}?token={BLYNK_AUTH_TOKEN}&{pin}={value}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Error: {str(e)}"

def trigger_blynk_event(event_code: str, description: str = "Weather alert triggered"):
    if not BLYNK_AUTH_TOKEN:
        raise HTTPException(status_code=500, detail="BLYNK_AUTH_TOKEN is missing")
    
    url = f"https://sgp1.blynk.cloud/external/api/logEvent?token={BLYNK_AUTH_TOKEN}&event={event_code}&priority=WARNING&description={description}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return {"message": "Blynk event triggered successfully"}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Blynk Event API Error: {str(e)}")

def get_lat_lon_from_location(location: str):
    try:
        response = requests.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": location, "count": 1})
        response.raise_for_status()
        data = response.json()
        if "results" in data and data["results"]:
            return data["results"][0]["latitude"], data["results"][0]["longitude"]
    except requests.RequestException:
        pass
    raise HTTPException(status_code=400, detail="Invalid location")

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

        if "current" not in weather_data:
            raise HTTPException(status_code=500, detail="Invalid weather API response")

        temperature = weather_data["current"].get("temperature_2m", "N/A")
        humidity = weather_data["current"].get("relative_humidity_2m", "N/A")
        pressure = weather_data["current"].get("pressure_msl", "N/A")
        uv_index = weather_data["current"].get("uv_index", "N/A")

        blynk_results = {
            "latitude": send_to_blynk("V8", str(latitude)),
            "longitude": send_to_blynk("V9", str(longitude)),
            "pressure": send_to_blynk("V10", str(pressure)),
            "temperature": send_to_blynk("V11", str(temperature)),
            "humidity": send_to_blynk("V12", str(humidity)),
            "uv_index": send_to_blynk("V13", str(uv_index)),
            "location": send_to_blynk("V6", f"{latitude}, {longitude}"),
            "weather_fetch": send_to_blynk("V7", "1")
        }

        ai_message = generate_ai_advisory(temperature, humidity, uv_index)
        send_to_blynk("V15", ai_message)
        trigger_blynk_event("ai_weather_alert", ai_message)

        return {"weather": weather_data, "blynk_results": blynk_results}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Weather API request failed: {str(e)}")

def generate_ai_advisory(temperature, humidity, uv_index):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant providing weather advisories tailored for farmers. Give clear, practical farming tips."},
            {"role": "user", "content": f"Given these weather conditions: Temperature: {temperature}°C, Humidity: {humidity}%, UV Index: {uv_index}, what should a farmer do to protect crops and livestock?"}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

@router.post("/weather")
def fetch_weather(location: str = Body(None), latitude: float = Body(None), longitude: float = Body(None)):
    if location:
        latitude, longitude = get_lat_lon_from_location(location)
    if latitude is None or longitude is None:
        raise HTTPException(status_code=400, detail="Latitude and longitude are required")
    return get_weather_data(latitude, longitude)

@router.get("/schedule_notification")
def schedule_notification():
    advisory = generate_ai_advisory(30, 80, 5)
    send_to_blynk("V15", advisory)
    trigger_blynk_event("ai_weather_alert", advisory)
    return {"message": "Scheduled AI advisory sent"}

@router.get("/blynk/test")
def test_blynk():
    return {"blynk_response": send_to_blynk("V14", "Hello from FastAPI")}

@router.get("/blynk/send")
def send_blynk_data(pin: str, value: str):
    return {"blynk_response": send_to_blynk(pin, value)}
