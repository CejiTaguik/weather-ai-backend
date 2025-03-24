from pydantic import BaseModel

# 🌤️ Model for Weather API Request
class WeatherRequest(BaseModel):
    location: str

# 📌 Model for AI-Based Weather Recommendations
class AIRecommendationRequest(BaseModel):
    temperature: float
    humidity: float
    pressure: float
    uv_index: float
    location: str

# 💬 Model for AI Chat Requests (User Input)
class AIChatRequest(BaseModel):
    user_query: str
