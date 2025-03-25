from fastapi import APIRouter, Query
import requests
import os
import time
from datetime import datetime, timedelta
from services import get_weather_data, generate_recommendation

router = APIRouter()

# ✅ Blynk Configuration
BLYNK_AUTH_TOKEN = os.getenv("BLYNK_AUTH_TOKEN", "YOUR_BLYNK_TOKEN_HERE")
BLYNK_SERVER = "https://blynk.cloud/external/api/update"

# ✅ Track last request time to prevent overload
last_blynk_request = datetime.min

def send_to_blynk(pin: str, value: str):
    """Send data to Blynk Cloud, ensuring we don't exceed request limits."""
    global last_blynk_request

    if not BLYNK_AUTH_TOKEN:
        print("⚠️ ERROR: BLYNK_AUTH_TOKEN is missing!")
        return {"error": "BLYNK_AUTH_TOKEN is missing"}

    # ✅ Prevent too many requests (Only allow 1 per 6 seconds)
    if datetime.now() - last_blynk_request < timedelta(seconds=6):
        print("⚠️ ERROR: Too many requests, try again later")
        return {"error": "Too many requests, try again later"}

    url = f"{BLYNK_SERVER}?token={BLYNK_AUTH_TOKEN}&{pin}={value}"
    print(f"📡 Sending to Blynk: {url}")  # ✅ Debugging Log

    try:
        response = requests.get(url)
        last_blynk_request = datetime.now()  # ✅ Update request time
        if response.status_code == 200:
            return {"success": response.text}
        else:
            print(f"⚠️ ERROR: Blynk responded with: {response.text}")
            return {"error": response.text}
    except Exception as e:
        print(f"⚠️ EXCEPTION: {str(e)}")
        return {"error": str(e)}

# ✅ Fetch Weather Data & Send to Blynk
@router.get("/weather")
def fetch_weather(latitude: float = Query(...), longitude: float = Query(...)):
    """Fetch weather data and send key values to Blynk."""
    weather_data = get_weather_data(latitude, longitude)

    if "error" not in weather_data:
        send_to_blynk("V8", str(latitude))  # API LATITUDE
        send_to_blynk("V9", str(longitude))  # API LONGITUDE
        send_to_blynk("V11", str(weather_data["current"]["temperature_2m"]))  # API TEMPERATURE
        send_to_blynk("V12", str(weather_data["current"]["relative_humidity_2m"]))  # API HUMIDITY
        send_to_blynk("V10", str(weather_data["current"]["pressure_msl"]))  # API PRESSURE
        send_to_blynk("V13", str(weather_data["current"]["uv_index"]))  # API UV INDEX

    return weather_data

# ✅ Generate AI-Based Recommendations & Send to Blynk
@router.get("/recommendation")
def fetch_recommendation(query: str = Query(...)):
    """Generate AI recommendation based on user input & send to Blynk."""
    recommendation = generate_recommendation(query)
    send_to_blynk("V15", recommendation)  # AI RECOMMENDATION
    return {"recommendation": recommendation}

# ✅ Blynk Test Route (Check if connection is active)
@router.get("/blynk/test")
def test_blynk():
    """Send a test message to Blynk to verify connection."""
    response = send_to_blynk("V14", "Hello from FastAPI")
    return {"blynk_response": response}
