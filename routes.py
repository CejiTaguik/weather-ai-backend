import os
import requests
from fastapi import APIRouter, Query, HTTPException, Body
from dotenv import load_dotenv
from openai import OpenAI
import schedule
import time
import threading

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

        # Generate AI recommendation
        ai_message = generate_ai_advisory(temperature, humidity, uv_index)
        send_to_blynk("V7", ai_message)  # Send AI recommendation to terminal widget (V7)
        send_to_blynk("V15", ai_message)  # Send AI message to V15 for display
        trigger_blynk_event("ai_weather_alert", ai_message)

        return {"weather": weather_data, "blynk_results": blynk_results}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Weather API request failed: {str(e)}")

def generate_ai_advisory(temperature, humidity, uv_index):
    # Use OpenAI API to generate AI-based recommendation
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[ 
            {"role": "system", "content": "You are an AI assistant providing weather advisories tailored for farmers. Give clear, practical farming tips."},
            {"role": "user", "content": f"Given these weather conditions: Temperature: {temperature}°C, Humidity: {humidity}%, UV Index: {uv_index}, what should a farmer do to protect crops and livestock?"}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

# Modify the scheduled notifications to run at 3 AM and 6 PM, with real-time weather data.
@router.get("/schedule_notification")
def schedule_notification():
    # Scheduling the AI advisory notification at 3 AM and 6 PM
    schedule.every().day.at("03:00").do(send_scheduled_advisory)
    schedule.every().day.at("18:00").do(send_scheduled_advisory)
    
    # Starting a background thread to run the schedule
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    # Start the background thread
    threading.Thread(target=run_schedule, daemon=True).start()
    
    return {"message": "Scheduled AI advisory notifications will now be sent daily at 3 AM and 6 PM."}

def send_scheduled_advisory():
    # Fetch the current weather data
    temperature = 30  # placeholder
    humidity = 80     # placeholder
    uv_index = 5      # placeholder

    ai_message = generate_ai_advisory(temperature, humidity, uv_index)
    send_to_blynk("V15", ai_message)
    trigger_blynk_event("ai_weather_alert", ai_message)
    print(f"Scheduled advisory sent: {ai_message}")

# Modify the fetch_weather route to accept location input and dynamically update Blynk V6
@router.post("/weather")
def fetch_weather(location: str = Body(..., embed=True), latitude: float = Body(None), longitude: float = Body(None)):
    if location:
        latitude, longitude = get_lat_lon_from_location(location)
        # Send the location to Blynk V6 (location will reflect here)
        send_to_blynk("V6", location)
    
    if latitude is None or longitude is None:
        raise HTTPException(status_code=400, detail="Latitude and longitude are required")
    
    return get_weather_data(latitude, longitude)

# New route to trigger AI recommendation manually to the terminal widget V7
@router.get("/trigger_ai_recommendation")
def trigger_ai():
    # Generate the AI recommendation with placeholder values for temperature, humidity, and uv_index
    ai_message = generate_ai_advisory(30, 80, 5)
    send_to_blynk("V7", ai_message)  # Send AI recommendation to terminal widget (V7)
    send_to_blynk("V15", ai_message)  # Send AI message to V15 for display
    trigger_blynk_event("ai_weather_alert", ai_message)

    return {"message": "AI recommendation triggered successfully", "ai_message": ai_message}

@router.get("/blynk/test")
def test_blynk():
    return {"blynk_response": send_to_blynk("V14", "Hello from FastAPI")}

@router.get("/blynk/send")
def send_blynk_data(pin: str, value: str):
    return {"blynk_response": send_to_blynk(pin, value)}
