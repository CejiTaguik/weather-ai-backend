import os
import requests
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

# ✅ Function to generate AI-based recommendations
def generate_recommendation(user_input: str) -> dict:
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant for weather-based recommendations."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        ai_response = response.choices[0].message.content.strip()
        
        # ✅ Trim AI response to fit Blynk character limits (max 255 chars)
        trimmed_response = ai_response[:255]
        
        # ✅ Send AI response to Blynk Terminal (V14) and Recommendation Widget (V15)
        blynk_results = {
            "terminal": send_to_blynk("V14", trimmed_response),
            "recommendation": send_to_blynk("V15", trimmed_response)
        }
        
        return {"recommendation": trimmed_response, "blynk_results": blynk_results}
    except Exception as e:
        return {"error": f"AI error: {str(e)}"}

# ✅ Weather Endpoint (Updates Blynk)
@router.get("/fetch_weather_api_weather_get")
def fetch_weather(latitude: float = Query(...), longitude: float = Query(...)):
    return get_weather_data(latitude, longitude)

# ✅ AI Recommendation Endpoint (Sends to Terminal Widget V14 & Recommendation Widget V15)
@router.get("/fetch_recommendation_api_recommendation_get")
def fetch_recommendation(query: str = Query(...)):
    return generate_recommendation(query)

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
