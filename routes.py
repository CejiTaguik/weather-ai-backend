from fastapi import APIRouter, Query
import os
from datetime import datetime, timedelta
from services import get_weather_data, generate_recommendation, send_to_blynk

router = APIRouter()

@router.get("/api/weather")
def fetch_weather(latitude: float = Query(...), longitude: float = Query(...)):
    data = get_weather_data(latitude, longitude)
    if "error" not in data:
        send_to_blynk("V6", f"Lat: {latitude}, Lon: {longitude}")
        send_to_blynk("V8", str(latitude))
        send_to_blynk("V9", str(longitude))
        send_to_blynk("V10", str(data["current"]["pressure_msl"]))
        send_to_blynk("V11", str(data["current"]["temperature_2m"]))
        send_to_blynk("V12", str(data["current"]["relative_humidity_2m"]))
        send_to_blynk("V13", str(data["current"]["uv_index"]))
    return data

@router.get("/api/recommendation")
def fetch_recommendation(query: str = Query(...)):
    recommendation = generate_recommendation(query)
    send_to_blynk("V15", recommendation)
    return {"recommendation": recommendation}

@router.get("/blynk/test")
def test_blynk():
    response = send_to_blynk("V7", "Hello from FastAPI")
    return {"blynk_response": response}

