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

# ✅ Function to fetch weather data from Open-Meteo
def get_weather_data(latitude: float, longitude: float):
    try:
        api_url = os.getenv("OPEN_METEO_API", "https://api.open-meteo.com/v1/forecast")
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "relative_humidity_2m", "pressure_msl", "uv_index", "precipitation"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            "timezone": "auto"
        }
        response = requests.get(api_url, params=params)
        print("Weather API Response:", response.text)  
        return response.json() if response.status_code == 200 else {"error": response.text}
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
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating recommendation: {str(e)}"

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

# ✅ Weather Endpoint
@router.get("/weather")
def fetch_weather(latitude: float = Query(...), longitude: float = Query(...)):
    return get_weather_data(latitude, longitude)

# ✅ AI Recommendation Endpoint
@router.get("/recommendation")
def fetch_recommendation(query: str = Query(...)):
    return {"recommendation": generate_recommendation(query)}

# ✅ Blynk Test Endpoint
@router.get("/blynk/test")
def test_blynk():
    response = send_to_blynk("V1", "Hello from FastAPI")
    return {"blynk_response": response}

# ✅ Send Custom Data to Blynk
@router.get("/blynk/send")
def send_blynk_data(pin: str = Query(...), value: str = Query(...)):
    response = send_to_blynk(pin, value)
    return {"blynk_response": response}
