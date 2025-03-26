from pydantic import BaseModel

# ✅ Weather Data Request Model
class WeatherRequest(BaseModel):
    latitude: float
    longitude: float

# ✅ AI Recommendation Request Model
class RecommendationRequest(BaseModel):
    query: str
