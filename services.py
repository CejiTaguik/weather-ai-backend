import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

# Function to fetch weather data from WeatherAPI
def get_weather_data(latitude: float, longitude: float):
    try:
        api_key = os.getenv("WEATHERAPI_KEY")
        if not api_key:
            return {"error": "500: WeatherAPI key is missing in environment variables."}

        base_url = "http://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": api_key,
            "q": f"{latitude},{longitude}",
            "days": 3,  # Fetch 3-day weather forecast
            "aqi": "no",
            "alerts": "yes"
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch weather data: {response.status_code}, {response.text}"}

    except Exception as e:
        return {"error": f"Exception: {str(e)}"}
