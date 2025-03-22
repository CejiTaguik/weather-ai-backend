from pydantic import BaseModel

# AI Recommendation Models
class RecommendationRequest(BaseModel):
    user_input: str

class RecommendationResponse(BaseModel):
    recommendation: str

# Weather Response Model
class WeatherResponse(BaseModel):
    temperature: float
    humidity: float
    pressure: float
    uv_index: float
