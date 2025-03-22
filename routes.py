from fastapi import APIRouter, HTTPException, Query
from models import RecommendationRequest, RecommendationResponse, WeatherResponse
from services import generate_recommendation, get_weather_data

# Create a router
router = APIRouter()

# AI Recommendation Route
@router.post("/recommendation", response_model=RecommendationResponse)
async def get_recommendation(request: RecommendationRequest):
    try:
        recommendation = generate_recommendation(request.user_input)
        return {"recommendation": recommendation}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Weather Data Route
@router.get("/weather", response_model=WeatherResponse)
async def get_weather(
    latitude: float = Query(..., description="Latitude of the location"),
    longitude: float = Query(..., description="Longitude of the location"),
):
    try:
        weather_data = get_weather_data(latitude, longitude)
        if "error" in weather_data:
            raise HTTPException(status_code=500, detail=weather_data["error"])
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exception: {str(e)}")
