from pydantic import BaseModel
from typing import Optional

# Model for weather response
class WeatherResponse(BaseModel):
    temperature: float
    humidity: float
    pressure: float
    uv_index: Optional[float] = None
    precipitation: Optional[float] = None

# Model for AI recommendation response
class RecommendationResponse(BaseModel):
    recommendation: str
