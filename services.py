import os
from openai import OpenAI
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key
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

# Function to fetch weather data from Meteomatics API
def get_weather_data(location: str):
    try:
        # Meteomatics API credentials
        meteo_api_url = "https://api.meteomatics.com/"
        meteo_user = os.getenv("METEOMATICS_USER")
        meteo_pass = os.getenv("METEOMATICS_PASS")

        # Define parameters for weather request
        params = {
            "temperature": "t_2m:C",
            "humidity": "humidity_2m:p",
            "pressure": "msl_pressure:hPa",
            "uv_index": "uv:idx"
        }

        # Construct the full API request URL
        endpoint = f"{meteo_api_url}now/{','.join(params.values())}/{location}/json"

        # Send the request
        response = requests.get(endpoint, auth=(meteo_user, meteo_pass))

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch weather data: {response.status_code}"}

    except Exception as e:
        return {"error": f"Exception: {str(e)}"}
