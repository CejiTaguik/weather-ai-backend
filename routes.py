from fastapi import APIRouter, Query
from services import get_weather_data, generate_recommendation

weather_router = APIRouter()

# ✅ Fetch weather data from API
@weather_router.get("/weather")
def fetch_weather(latitude: float = Query(...), longitude: float = Query(...)):
    return get_weather_data(latitude, longitude)

# ✅ Generate AI-based recommendations
@weather_router.get("/recommendation")
def fetch_recommendation(query: str = Query(...)):
    return {"recommendation": generate_recommendation(query)}
