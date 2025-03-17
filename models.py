from pydantic import BaseModel

class RecommendationRequest(BaseModel):
    user_input: str

class RecommendationResponse(BaseModel):
    recommendation: str
