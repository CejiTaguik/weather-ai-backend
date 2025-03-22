from pydantic import BaseModel

# Model for AI recommendation request
class RecommendationRequest(BaseModel):
    user_input: str

# Model for AI recommendation response
class RecommendationResponse(BaseModel):
    recommendation: str

# Model for WeatherAPI response
class WeatherResponse(BaseModel):
    location: str
    temperature: float
    humidity: float
    pressure: float
    uv_index: float
    forecast: list
