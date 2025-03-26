
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenAI Client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Blynk Configuration
BLYNK_AUTH_TOKEN = os.getenv("BLYNK_AUTH_TOKEN")
BLYNK_SERVER = "https://blynk.cloud/external/api/update"

def send_to_blynk(pin: str, value: str):
    if not BLYNK_AUTH_TOKEN:
        return {"error": "BLYNK_AUTH_TOKEN is missing"}
    url = f"{BLYNK_SERVER}?token={BLYNK_AUTH_TOKEN}&{pin}={value}"
    try:
        response = requests.get(url)
        return response.text if response.status_code == 200 else f"Error: {response.text}"
    except Exception as e:
        return f"Exception: {str(e)}"

# Open-Meteo Weather API
WEATHER_API_URL = os.getenv("OPEN_METEO_API", "https://api.open-meteo.com/v1/forecast")

def get_weather_data(latitude: float, longitude: float):
    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "relative_humidity_2m", "pressure_msl", "uv_index", "precipitation"],
            "timezone": "auto"
        }
        response = requests.get(WEATHER_API_URL, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch weather data: {response.status_code}, {response.text}"}
    except Exception as e:
        return {"error": f"Exception in get_weather_data: {str(e)}"}

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