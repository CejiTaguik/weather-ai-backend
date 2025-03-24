import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load Blynk credentials
BLYNK_AUTH_TOKEN = os.getenv("BLYNK_AUTH_TOKEN")  # Your Blynk token from .env
BLYNK_BASE_URL = os.getenv("BLYNK_BASE_URL", "https://blynk.cloud/external/api")

# Function to fetch weather data from Open-Meteo
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

        # Debugging: Print API response in logs
        print("Weather API Response:", response.text)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch weather data: {response.status_code}, {response.text}"}

    except Exception as e:
        return {"error": f"Exception in get_weather_data: {str(e)}"}

# Function to generate AI-based recommendations
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

# Function to send data to Blynk
def send_to_blynk(pin: str, value: str):
    url = f"{BLYNK_BASE_URL}/update?token={BLYNK_AUTH_TOKEN}&{pin}={value}"
    try:
        response = requests.get(url)
        print("Blynk Response:", response.text)  # Debugging log
        return response.text
    except Exception as e:
        return {"error": f"Failed to send data to Blynk: {str(e)}"}
