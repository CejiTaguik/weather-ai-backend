import os
import requests
from fastapi import APIRouter, Query
from services import get_weather_data, generate_recommendation

# Initialize Router
router = APIRouter()

# ✅ Fetch weather data from API
@router.get("/weather")
def fetch_weather(latitude: float = Query(...), longitude: float = Query(...)):
    return get_weather_data(latitude, longitude)

# ✅ Generate AI-based recommendations
@router.get("/recommendation")
def fetch_recommendation(query: str = Query(...)):
    return {"recommendation": generate_recommendation(query)}

# ✅ Blynk Configuration
BLYNK_AUTH_TOKEN = os.getenv("BLYNK_AUTH_TOKEN")
BLYNK_SERVER = "https://blynk.cloud/external/api/update"

# Function to send data to Blynk
def send_to_blynk(pin: str, value: str):
    if not BLYNK_AUTH_TOKEN:
        return {"error": "BLYNK_AUTH_TOKEN is missing"}

    url = f"{BLYNK_SERVER}?token={BLYNK_AUTH_TOKEN}&{pin}={value}"
    
    try:
        response = requests.get(url)
        return response.text if response.status_code == 200 else f"Error: {response.text}"
    except Exception as e:
        return f"Exception: {str(e)}"

# ✅ Test Endpoint: Send Sample Data to Blynk
@router.get("/blynk/test")
def test_blynk():
    response = send_to_blynk("V1", "Hello from FastAPI")
    return {"blynk_response": response}
