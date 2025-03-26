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
        if response.status_code == 200 and response.text.strip() == "200":
            return {"status": "success", "pin": pin, "value": value}
        else:
            return {"status": "error", "message": response.text}
    except Exception as e:
        return {"status": "error", "message": f"Exception: {str(e)}"}

# ✅ Function to fetch weather data (Fixes Open-Meteo API issue)
def get_weather_data(latitude: float, longitude: float):
    try:
        api_url = os.getenv("OPEN_METEO_API", "https://api.open-meteo.com/v1/forecast")
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,pressure_msl,uv_index",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto"
        }
        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            return {"error": response.text}

        weather_data = response.json()
        current_weather = weather_data.get("current", {})

        if not current_weather:
            return {"error": "Weather data unavailable"}

        # ✅ Send correct weather data to Blynk
        send_to_blynk("V8", str(latitude))  # Latitude
        send_to_blynk("V9", str(longitude))  # Longitude
        send_to_blynk("V10", str(current_weather.get("pressure_msl", "N/A")))  # Pressure
        send_to_blynk("V11", str(current_weather.get("temperature_2m", "N/A")))  # Temperature
        send_to_blynk("V12", str(current_weather.get("relative_humidity_2m", "N/A")))  # Humidity
        send_to_blynk("V13", str(current_weather.get("uv_index", "N/A")))  # UV Index
        send_to_blynk("V6", f"{latitude}, {longitude}")  # Location (Formatted)

        return {"weather": current_weather}
    except Exception as e:
        return {"error": str(e)}

# ✅ Function to generate AI-based recommendations
def generate_recommendation(user_input: str):
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
        send_to_blynk("V14", ai_response[:200])  # Blynk has a char limit, so we trim
        send_to_blynk("V15", ai_response[:200])

        return {"recommendation": ai_response}
    except Exception as e:
        return {"error": f"AI error: {str(e)}"}

# ✅ Weather Endpoint (Fixes issue with Open-Meteo API)
@router.get("/weather")
def fetch_weather(latitude: float = Query(...), longitude: float = Query(...)):
    return get_weather_data(latitude, longitude)

# ✅ AI Recommendation Endpoint (Fixes OpenAI API issue)
@router.get("/recommendation")
def fetch_recommendation(query: str = Query(...)):
    return generate_recommendation(query)

# ✅ Blynk Test Endpoint
@router.get("/blynk/test")
def test_blynk():
    response = send_to_blynk("V14", "Hello from FastAPI")
    return {"blynk_response": response}

# ✅ Send Custom Data to Blynk (Fixes incorrect status handling)
@router.get("/blynk/send")
def send_blynk_data(pin: str = Query(...), value: str = Query(...)):
    response = send_to_blynk(pin, value)
    return response
