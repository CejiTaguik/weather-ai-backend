import os
import requests
from fastapi import APIRouter, HTTPException, Body
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Blynk setup
BLYNK_AUTH_TOKEN = os.getenv("BLYNK_AUTH_TOKEN")
BLYNK_SERVER = "https://blynk.cloud/external/api/update"
BLYNK_EVENT_URL = "https://blynk.cloud/external/api/logEvent"

# Ensure OpenAI API Key is available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing. Please set it in your environment.")

# Create router
router = APIRouter()

def send_to_blynk(pin: str, value: str):
    """Send data to Blynk virtual pin"""
    if not BLYNK_AUTH_TOKEN:
        raise HTTPException(status_code=500, detail="BLYNK_AUTH_TOKEN is missing")
    
    url = f"{BLYNK_SERVER}?token={BLYNK_AUTH_TOKEN}&{pin}={value}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Error: {str(e)}"

def trigger_blynk_event(event_code: str, description: str = "Weather alert triggered"):
    """Trigger Blynk push notification"""
    if not BLYNK_AUTH_TOKEN:
        raise HTTPException(status_code=500, detail="BLYNK_AUTH_TOKEN is missing")
    
    url = f"{BLYNK_EVENT_URL}?token={BLYNK_AUTH_TOKEN}&event={event_code}&description={description}&priority=CRITICAL"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return {"message": "Blynk event triggered successfully"}
    except requests.RequestException as e:
        return f"Error: {str(e)}"

def get_lat_lon_from_location(location: str):
    """Convert location name to latitude & longitude"""
    try:
        response = requests.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": location, "count": 1})
        response.raise_for_status()
        data = response.json()
        if "results" in data and data["results"]:
            return data["results"][0]["latitude"], data["results"][0]["longitude"]
    except requests.RequestException:
        pass
    raise HTTPException(status_code=400, detail="Invalid location")

def get_weather_data(latitude: float, longitude: float):
    """Fetch weather data from Open-Meteo API and update Blynk"""
    try:
        api_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,pressure_msl,uv_index",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto"
        }
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        weather_data = response.json()

        if "current" not in weather_data:
            raise HTTPException(status_code=500, detail="Invalid weather API response")

        temperature = weather_data["current"].get("temperature_2m", "N/A")
        humidity = weather_data["current"].get("relative_humidity_2m", "N/A")
        pressure = weather_data["current"].get("pressure_msl", "N/A")
        uv_index = weather_data["current"].get("uv_index", "N/A")

        # Send weather data to Blynk
        blynk_results = {
            "latitude": send_to_blynk("V8", str(latitude)),
            "longitude": send_to_blynk("V9", str(longitude)),
            "pressure": send_to_blynk("V10", str(pressure)),
            "temperature": send_to_blynk("V11", str(temperature)),
            "humidity": send_to_blynk("V12", str(humidity)),
            "uv_index": send_to_blynk("V13", str(uv_index)),
            "location": send_to_blynk("V6", f"{latitude}, {longitude}"),
            "weather_fetch": send_to_blynk("V7", "1")
        }

        # Generate AI advisory
        ai_message = generate_ai_advisory(temperature, humidity, uv_index)
        send_to_blynk("V15", ai_message)  # Display AI response in Blynk AI Recommendation Display

        # Trigger push notification
        trigger_blynk_event("ai_weather_alert", ai_message)

        return {"weather": weather_data, "blynk_results": blynk_results}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Weather API request failed: {str(e)}")

def generate_ai_advisory(temperature, humidity, uv_index):
    """Generate AI-based farming advisory based on weather conditions"""
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant providing weather advisories tailored for farmers. Provide clear and practical farming tips."},
            {"role": "user", "content": f"Given these weather conditions: Temperature: {temperature}°C, Humidity: {humidity}%, UV Index: {uv_index}, what should a farmer do to protect crops and livestock?"}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

@router.post("/weather")
def fetch_weather(location: str = Body(None), latitude: float = Body(None), longitude: float = Body(None)):
    """Fetch weather data and AI recommendations for a given location"""
    if location:
        latitude, longitude = get_lat_lon_from_location(location)
    if latitude is None or longitude is None:
        raise HTTPException(status_code=400, detail="Latitude and longitude are required")
    return get_weather_data(latitude, longitude)

@router.get("/schedule_notification")
def schedule_notification():
    """Schedule AI-generated recommendation and send notification"""
    try:
        # Fetch latest weather data for AI recommendation
        advisory = generate_ai_advisory(30, 80, 5)  # Example values

        # Send AI response to AI Recommendation Display (V15)
        blynk_response = send_to_blynk("V15", advisory)
        if "Error" in blynk_response:
            raise HTTPException(status_code=500, detail=f"Failed to send AI recommendation: {blynk_response}")

        # Trigger Blynk push notification event
        event_response = trigger_blynk_event("ai_weather_alert", advisory)
        if "Error" in event_response:
            raise HTTPException(status_code=500, detail=f"Failed to trigger push notification: {event_response}")

        return {"message": "Scheduled AI advisory sent", "recommendation": advisory}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendation: {str(e)}")

@router.get("/blynk/test")
def test_blynk():
    """Test sending a message to Blynk terminal"""
    return {"blynk_response": send_to_blynk("V14", "Hello from FastAPI")}

@router.get("/blynk/send")
def send_blynk_data(pin: str, value: str):
    """Manually send data to a Blynk virtual pin"""
    response = send_to_blynk(pin, value)
    if "Error" in response:
        raise HTTPException(status_code=500, detail="Failed to send data to Blynk.")
    return {"blynk_response": response}

@router.get("/blynk/ai_chat")
def ai_chat_request(chat_message: str):
    """AI chat request using the Blynk terminal widget"""
    ai_response = generate_ai_advisory(30, 60, 3)  # Example values for testing
    send_to_blynk("V14", ai_response)  # Sending AI response to the Blynk Terminal Widget
    return {"message": "AI recommendation sent to terminal", "response": ai_response}
