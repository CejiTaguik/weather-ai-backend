from fastapi import APIRouter, Query
from services import get_weather_data, generate_recommendation
from models import RecommendationRequest, RecommendationResponse

router = APIRouter()

# Weather route
@router.get("/weather")
def fetch_weather(
    latitude: float = Query(..., description="Latitude of the location"),
    longitude: float = Query(..., description="Longitude of the location")
):
    return get_weather_data(latitude, longitude)

# AI recommendation route
@router.post("/recommendation", response_model=RecommendationResponse)
def get_recommendation(request: RecommendationRequest):
    recommendation = generate_recommendation(request.user_input)
    return {"recommendation": recommendation}
