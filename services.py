import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# OpenAI Client (Check if API key exists)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API Key in environment variables.")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Function to fetch weather data
def get_weather_data(latitude: float, longitude: float):
    api_url = os.getenv("OPEN_METEO_API", "https://api.open-meteo.com/v1/forecast")
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "relative_humidity_2m", "pressure_msl", "uv_index"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "timezone": "auto"
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=5)  # ⏳ Add timeout for reliability
        if response.status_code == 200:
            return response.json()
        return {"error": f"Weather API error: {response.status_code} - {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Weather API request failed: {str(e)}"}

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
        return {"error": f"AI error: {str(e)}"}
