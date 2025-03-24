from fastapi import APIRouter, Query, Body
from services import get_weather_data, generate_recommendation, ask_ai

weather_router = APIRouter()
blynk_router = APIRouter()  # New router for Blynk integration

# 🌤️ Endpoint to fetch weather data
@weather_router.get("/weather")
def fetch_weather(latitude: float = Query(...), longitude: float = Query(...)):
    return get_weather_data(latitude, longitude)

# 🤖 Endpoint to generate AI-based recommendations
@weather_router.get("/recommendation")
def fetch_recommendation(query: str = Query(...)):
    return {"recommendation": generate_recommendation(query)}

# 🟢 BLYNK INTEGRATION STARTS HERE 🟢

# 🌍 Webhook to fetch weather data for Blynk
@blynk_router.post("/get_weather/")
def blynk_get_weather(location: str = Body(..., embed=True)):
    """Fetch weather data based on user-inputted location (from Blynk)"""
    weather_data = get_weather_data(location)
    return weather_data  # Sends data back to Blynk

# 📌 Webhook to generate AI recommendations for Blynk
@blynk_router.post("/get_recommendation/")
def blynk_get_recommendation(
    temperature: float = Body(...),
    humidity: float = Body(...),
    pressure: float = Body(...),
    uv_index: float = Body(...),
    location: str = Body(...)
):
    """Generate AI recommendations based on weather conditions"""
    recommendation = generate_recommendation({
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure,
        "uv_index": uv_index,
        "location": location
    })
    return {"recommendation": recommendation}

# 💬 Webhook to handle AI chat from Blynk
@blynk_router.post("/ask_ai/")
def blynk_ask_ai(user_query: str = Body(..., embed=True)):
    """Allows users to chat with AI via Blynk"""
    response = ask_ai(user_query)
    return {"ai_response": response}
