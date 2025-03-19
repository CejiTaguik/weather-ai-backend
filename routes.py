from fastapi import APIRouter, HTTPException
from models import RecommendationRequest, RecommendationResponse
from services import generate_recommendation, get_weather_data

recommendation_router = APIRouter()

# AI Recommendation Endpoint
@recommendation_router.post("/recommendation", response_model=RecommendationResponse)
async def get_recommendation(request: RecommendationRequest):
    try:
        recommendation = generate_recommendation(request.user_input)
        return {"recommendation": recommendation}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Weather Data Endpoint
@recommendation_router.get("/weather/{location}")
async def get_weather(location: str):
    try:
        weather_data = get_weather_data(location)
        if "error" in weather_data:
            raise HTTPException(status_code=500, detail=weather_data["error"])
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
