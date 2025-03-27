from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from routes import router

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Blynk Weather Monitoring API",
    description="FastAPI service for fetching weather data, sending AI-based recommendations, and interacting with Blynk.",
    version="1.0.0"
)

# ✅ Add CORS Middleware (Required for frontend or external API calls)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}

# ✅ Fix: Require lat and lon as query parameters
@app.get("/weather")
def get_weather(lat: float = Query(..., description="Latitude is required"), 
                lon: float = Query(..., description="Longitude is required")):
    print(f"Received lat: {lat}, lon: {lon}")  # Debugging log
    return {"latitude": lat, "longitude": lon}
