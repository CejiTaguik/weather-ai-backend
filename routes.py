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
        return response.text if response.status_code == 200 else f"Error: {response.text}"
    except Exception as e:
        return f"Exception: {str(e)}"

# ✅ Function to fetch weather data (Updates Blynk)
def get_weather_data(latitude: float, longitude: float):
    try:
        api_url = os.getenv("OPEN_METEO_API", "https://api.open-meteo.com/v1/forecast")
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "relative_humidity_2m", "pressure_msl", "uv_index"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            "timezone": "auto"
        }
        response = requests.get(api_url, params=params)
        weather_data = response.json() if response.status_code == 200 else {"error": response.text}

        # ✅ Send data to Blynk with correct Virtual Pins
        send_to_blynk("V8", str(latitude))  # Latitude
        send_to_blynk("V9", str(longitude))  # Longitude
        send_to_blynk("V10", str(weather_data["current"]["pressure_msl"]))  # Pressure
        send_to_blynk("V11", str(weather_data["current"]["temperature_2m"]))  # Temperature
        send_to_blynk("V12", str(weather_data["current"]["relative_humidity_2m"]))  # Humidity
        send_to_blynk("V13", str(weather_data["current"]["uv_index"]))  # UV Index
        send_to_blynk("V6", f"{latitude}, {longitude}")  # Location (Formatted)

        return weather_data
    except Exception as e:
        return {"error": str(e)}

# ✅ Function to generate AI-based recommendations
def generate_recommendation(user_input: str) -> str:
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

        # ✅ Send AI response to Blynk Terminal (V14) and Recommendation Widget (V15)
        send_to_blynk("V14", ai_response)  # AI Response for Terminal
        send_to_blynk("V15", ai_response)  # AI Recommendation

        return {"recommendation": ai_response}
    except Exception as e:
        return {"error": f"AI error: {str(e)}"}

# ✅ Weather Endpoint (Updates Blynk)
@router.get("/weather")
def fetch_weather(latitude: float = Query(...), longitude: float = Query(...)):
    return get_weather_data(latitude, longitude)

# ✅ AI Recommendation Endpoint (Sends to Terminal Widget V14 & Recommendation Widget V15)
@router.get("/recommendation")
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
