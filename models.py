from pydantic import BaseModel, Field

# ✅ Weather Data Request Model
class WeatherRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, example=14.5995)  # Example: Manila
    longitude: float = Field(..., ge=-180, le=180, example=120.9842)  # Example: Manila

# ✅ AI Recommendation Request Model
class RecommendationRequest(BaseModel):
    query: str = Field(..., example="What should I do if it rains tomorrow?")
