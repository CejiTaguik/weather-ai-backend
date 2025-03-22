import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
METEOMATICS_USER = os.getenv("METEOMATICS_USER")
METEOMATICS_PASS = os.getenv("METEOMATICS_PASS")

# Debugging: Ensure environment variables are loaded correctly (REMOVE after confirming it works)
print("Loaded METEOMATICS_USER:", METEOMATICS_USER)
print("Loaded METEOMATICS_PASS:", METEOMATICS_PASS)

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

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
        # Validate credentials
        if not METEOMATICS_USER or not METEOMATICS_PASS:
            return {"error": "Meteomatics API credentials are missing."}

        # Define Meteomatics API base URL
        meteo_api_url = "https://api.meteomatics.com/"

        # Define weather parameters
        params = [
            "t_2m:C",  # Temperature (Celsius)
            "humidity_2m:p",  # Humidity (%)
            "msl_pressure:hPa",  # Pressure (hPa)
            "uv:idx"  # UV Index
        ]

        # Construct the full API request URL
        endpoint = f"{meteo_api_url}now/{','.join(params)}/{location}/json"

        print("Requesting Meteomatics API:", endpoint)  # Debugging

        # Send the request with basic authentication
        response = requests.get(endpoint, auth=(METEOMATICS_USER, METEOMATICS_PASS))

        # Log the response details
        print("Meteomatics Response Code:", response.status_code)
        print("Meteomatics Response Text:", response.text)

        # Return JSON response if successful
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch weather data: {response.status_code}, Response: {response.text}"}

    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}
