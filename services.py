import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# XWeather API credentials
XWEATHER_API_ID = os.getenv("XWEATHER_API_ID")
XWEATHER_API_SECRET = os.getenv("XWEATHER_API_SECRET")
XWEATHER_NAMESPACE = os.getenv("XWEATHER_NAMESPACE")

# Base URL for XWeather API
XWEATHER_API_URL = "https://api.xweather.com/v1/weather"

# Function to fetch weather data from XWeather API
def get_weather_data(location: str):
    try:
        if not XWEATHER_API_ID or not XWEATHER_API_SECRET:
            return {"error": "XWeather API credentials are missing."}
        
        # Define request parameters
        params = {
            "lat": location.split(",")[0],
            "lon": location.split(",")[1],
            "api_id": XWEATHER_API_ID,
            "api_secret": XWEATHER_API_SECRET,
            "namespace": XWEATHER_NAMESPACE
        }
        
        response = requests.get(XWEATHER_API_URL, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch weather data: {response.status_code}, Response: {response.text}"}
    
    except Exception as e:
        return {"error": f"Exception: {str(e)}"}

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
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# XWeather API credentials
XWEATHER_API_ID = os.getenv("XWEATHER_API_ID")
XWEATHER_API_SECRET = os.getenv("XWEATHER_API_SECRET")
XWEATHER_NAMESPACE = os.getenv("XWEATHER_NAMESPACE")

# Base URL for XWeather API
XWEATHER_API_URL = "https://api.xweather.com/v1/weather"

# Function to fetch weather data from XWeather API
def get_weather_data(location: str):
    try:
        if not XWEATHER_API_ID or not XWEATHER_API_SECRET:
            return {"error": "XWeather API credentials are missing."}
        
        # Define request parameters
        params = {
            "lat": location.split(",")[0],
            "lon": location.split(",")[1],
            "api_id": XWEATHER_API_ID,
            "api_secret": XWEATHER_API_SECRET,
            "namespace": XWEATHER_NAMESPACE
        }
        
        response = requests.get(XWEATHER_API_URL, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch weather data: {response.status_code}, Response: {response.text}"}
    
    except Exception as e:
        return {"error": f"Exception: {str(e)}"}

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
