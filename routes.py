from fastapi import APIRouter, Query
import os
from openai import OpenAI
from utils import get_weather_data, send_to_blynk, get_lat_lon_from_location

router = APIRouter()

# ✅ Weather API Fetch Route
@router.get("/weather")
def fetch_weather(
    location: str = Query(..., description="Location name"),
    latitude: float = Query(None, description="Latitude"),
    longitude: float = Query(None, description="Longitude")
):
    if location:
        latitude, longitude = get_lat_lon_from_location(location)
        if latitude is None or longitude is None:
            return {"error": "Invalid location"}

    if latitude is None or longitude is None:
        return {"error": "Latitude and longitude are required"}

    weather_data = get_weather_data(latitude, longitude)

    if "weather" in weather_data:
        blynk_results = {
            "location": send_to_blynk("V6", location),
            "latitude": send_to_blynk("V8", str(latitude)),
            "longitude": send_to_blynk("V9", str(longitude)),
            "temperature": send_to_blynk("V11", str(weather_data['weather']['current'].get("temperature_2m", "N/A"))),
            "humidity": send_to_blynk("V12", str(weather_data['weather']['current'].get("relative_humidity_2m", "N/A"))),
            "pressure": send_to_blynk("V10", str(weather_data['weather']['current'].get("pressure_msl", "N/A"))),
            "uv_index": send_to_blynk("V13", str(weather_data['weather']['current'].get("uv_index", "N/A")))
        }
        return {"weather": weather_data, "blynk_results": blynk_results}

    return {"error": "Failed to fetch weather data"}

# ✅ AI Recommendation Endpoint (Fixed)
@router.get("/recommendation")
def fetch_recommendation(
    query: str = Query(..., description="User query for AI recommendations"),
    location: str = Query(None, description="Location name"),
    latitude: float = Query(None, description="Latitude"),
    longitude: float = Query(None, description="Longitude")
):
    if location:
        latitude, longitude = get_lat_lon_from_location(location)
        if latitude is None or longitude is None:
            return {"error": "Invalid location"}

    if latitude is None or longitude is None:
        return {"error": "Latitude and longitude are required"}

    result = generate_recommendation(query, latitude, longitude)

    return result

# ✅ Function to generate AI-based recommendations
def generate_recommendation(query: str, latitude: float, longitude: float) -> dict:
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    weather_data = get_weather_data(latitude, longitude)
    
    if "weather" in weather_data:
        weather_context = (
            f"Current temperature: {weather_data['weather']['current'].get('temperature_2m', 'N/A')}°C, "
            f"Humidity: {weather_data['weather']['current'].get('relative_humidity_2m', 'N/A')}%, "
            f"Pressure: {weather_data['weather']['current'].get('pressure_msl', 'N/A')} hPa, "
            f"UV Index: {weather_data['weather']['current'].get('uv_index', 'N/A')}."
        )
    else:
        weather_context = "Weather data unavailable."
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant for weather-based recommendations."},
                {"role": "user", "content": f"{query}\n\nWeather Context: {weather_context}"}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        ai_response = response.choices[0].message.content.strip()
        trimmed_response = ai_response[:255]  # ✅ Trim AI response to fit Blynk character limits

        # ✅ Send AI response to **V15** (AI Recommendation Display)
        blynk_results = {
            "recommendation": send_to_blynk("V15", trimmed_response)
        }

        return {"recommendation": trimmed_response, "blynk_results": blynk_results}
    except Exception as e:
        return {"error": f"AI error: {str(e)}"}
