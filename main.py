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

# ✅ Debugging: Ensure latitude and longitude are correctly received
@app.get("/weather")
def get_weather(lat: float = Query(None), lon: float = Query(None)):
    print(f"Received lat: {lat}, lon: {lon}")  # Debugging log
    if lat is None or lon is None:
        return {"detail": "Latitude and longitude are required"}
    return {"latitude": lat, "longitude": lon}
