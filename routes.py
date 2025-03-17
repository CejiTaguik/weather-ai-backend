from fastapi import APIRouter, HTTPException
from models import RecommendationRequest, RecommendationResponse
from services import generate_recommendation

recommendation_router = APIRouter()

@recommendation_router.post("/recommendation", response_model=RecommendationResponse)
async def get_recommendation(request: RecommendationRequest):
    try:
        recommendation = generate_recommendation(request.user_input)
        return {"recommendation": recommendation}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
