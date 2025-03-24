import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🌤️ Function to fetch weather data from Open-Meteo
def get_weather_data(location: str):
    try:
        # Open-Meteo API URL
        api_url = os.getenv("OPEN_METEO_API", "https://api.open-meteo.com/v1/forecast")

        # Convert location into latitude/longitude using Open-Meteo geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
        geo_response = requests.get(geo_url).json()

        if "results" not in geo_response or not geo_response["results"]:
            return {"error": "Invalid location"}

        latitude = geo_response["results"][0]["latitude"]
        longitude = geo_response["results"][0]["longitude"]

        # Define query parameters
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "relative_humidity_2m", "pressure_msl", "uv_index"],
            "timezone": "auto"
        }

        # Fetch weather data
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch weather data: {response.status_code}, {response.text}"}

    except Exception as e:
        return {"error": f"Exception: {str(e)}"}

# 📌 Function to generate AI-based recommendations
def generate_recommendation(weather_data: dict) -> str:
    try:
        # Format input for AI
        user_input = (
            f"Current weather details:\n"
            f"Location: {weather_data.get('location', 'Unknown')}\n"
            f"Temperature: {weather_data.get('temperature')}°C\n"
            f"Humidity: {weather_data.get('humidity')}%\n"
            f"Pressure: {weather_data.get('pressure')} hPa\n"
            f"UV Index: {weather_data.get('uv_index')}\n"
            f"Provide recommendations based on these conditions."
        )

        # Generate AI response
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

# 💬 Function to handle AI chat requests
def ask_ai(user_query: str) -> str:
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant. Provide helpful responses to user queries."},
                {"role": "user", "content": user_query}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error processing AI chat request: {str(e)}"
