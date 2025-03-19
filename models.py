from pydantic import BaseModel

# AI Recommendation Models (Unchanged)
class RecommendationRequest(BaseModel):
    user_input: str

class RecommendationResponse(BaseModel):
    recommendation: str

# Weather Data Model (New)
class WeatherDataResponse(BaseModel):
    temperature: float
    humidity: float
    pressure: float
    uv_index: float
    location: str
