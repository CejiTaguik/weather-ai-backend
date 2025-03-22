import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# XWeather API Credentials
XWEATHER_API_ID = os.getenv("XWEATHER_API_ID")
XWEATHER_API_SECRET = os.getenv("XWEATHER_API_SECRET")
XWEATHER_NAMESPACE = os.getenv("XWEATHER_NAMESPACE")

# Function to generate AI-based recommendations
def generate_recommendation(user_input: str) -> str:
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant for weather recommendations."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating recommendation: {str(e)}"

# Function to fetch weather data from XWeather API
def get_weather_data(latitude: float, longitude: float):
    try:
        url = f"https://platform.xweather.com/v1/weather?lat={latitude}&lon={longitude}"
        headers = {
            "X-API-Key": XWEATHER_API_ID,
            "X-API-Secret": XWEATHER_API_SECRET,
            "X-API-Namespace": XWEATHER_NAMESPACE
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch weather data: {response.status_code}, Response: {response.text}"}

    except Exception as e:
        return {"error": f"Exception: {str(e)}"}
