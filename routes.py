from fastapi import APIRouter
import requests
import logging
import openai
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO)

# Blynk API Auth Token (replace with your actual token)
BLYNK_AUTH_TOKEN = "YOUR_BLYNK_AUTH_TOKEN"

# OpenAI API key (replace with your actual OpenAI API key)
openai.api_key = "YOUR_OPENAI_API_KEY"

# Initialize router for FastAPI
router = APIRouter()

# Function to send data to Blynk virtual pin
def send_to_blynk(pin: str, message: str):
    try:
        url = f"http://blynk-cloud.com/{BLYNK_AUTH_TOKEN}/update/{pin}?value={message}"
        response = requests.get(url)
        logging.info(f"Sent message to pin {pin}: {message}, Response status: {response.status_code}")
        return response.status_code
    except Exception as e:
        logging.error(f"Error sending to Blynk: {str(e)}")
        return None

# Function to generate AI recommendation for sudden weather change
def generate_ai_recommendation(temperature: float, humidity: float, uv_index: float):
    # Define the template structure of the recommendation that the AI will follow
    prompt = f"""
    The current weather conditions are:
    Temperature: {temperature}°C
    Humidity: {humidity}%
    UV Index: {uv_index}

    Based on these conditions, provide a weather timeline for farmers and an actionable plan. Include educational tips on farming practices.
    Format the response like this:

    **Weather Timeline:**
    - 8:00 AM - 9:00 AM: [Weather Condition]
    - 9:00 AM - 10:00 AM: [Weather Condition]
    - [Continue as needed]

    **ACTION PLAN:**
    - [Condition-based action steps]

    **EDUCATIONAL TIP:**
    - [Farming advice based on the conditions]
    """

    try:
        # Generate AI-based recommendation
        response = openai.Completion.create(
            engine="text-davinci-003",  # Or use the latest GPT model
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )
        ai_recommendation = response.choices[0].text.strip()
        logging.info(f"Generated AI Recommendation: {ai_recommendation}")
        return ai_recommendation
    except Exception as e:
        logging.error(f"Error generating AI recommendation: {str(e)}")
        return "Error generating recommendation."

# Trigger AI recommendation based on weather data
@router.get("/trigger_ai_recommendation")
def trigger_ai():
    try:
        # Fetching weather data (replace with actual sensor or API data)
        temperature = 40  # Placeholder value, fetch from real data
        humidity = 60      # Placeholder value, fetch from real data
        uv_index = 7       # Placeholder value, fetch from real data

        # Generate AI recommendation dynamically
        ai_message = generate_ai_recommendation(temperature, humidity, uv_index)

        # Send the AI recommendation to Virtual Pin V7 (Terminal) and V15 (AI Recommendation Display)
        v7_status = send_to_blynk("V7", ai_message)  # Terminal widget V7
        v15_status = send_to_blynk("V15", ai_message)  # AI Recommendation Display V15

        # Log the status of sending to Blynk
        logging.info(f"Status for sending to V7: {v7_status}")
        logging.info(f"Status for sending to V15: {v15_status}")

        return {"message": "AI recommendation triggered successfully", "ai_message": ai_message}
    
    except Exception as e:
        logging.error(f"Error in triggering AI recommendation: {str(e)}")
        return {"error": str(e)}

# Schedule AI recommendation based on weather data (manual scheduling)
@router.get("/schedule_notification")
def schedule_notification():
    try:
        # Fetching weather data (replace with actual sensor or API data)
        temperature = 40  # Placeholder value, fetch from real data
        humidity = 60      # Placeholder value, fetch from real data
        uv_index = 7       # Placeholder value, fetch from real data

        # Generate AI recommendation dynamically
        ai_message = generate_ai_recommendation(temperature, humidity, uv_index)

        # Send the AI recommendation to Virtual Pin V7 (Terminal) and V15 (AI Recommendation Display)
        v7_status = send_to_blynk("V7", ai_message)  # Terminal widget V7
        v15_status = send_to_blynk("V15", ai_message)  # AI Recommendation Display V15

        # Log the status of sending to Blynk
        logging.info(f"Scheduled AI Recommendation: {ai_message}")
        logging.info(f"Status for sending to V7: {v7_status}")
        logging.info(f"Status for sending to V15: {v15_status}")

        return {"message": "Scheduled AI recommendation sent successfully", "ai_message": ai_message}
    
    except Exception as e:
        logging.error(f"Error in scheduling AI recommendation: {str(e)}")
        return {"error": str(e)}
