from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from routes import router  # Import the API routes

# Initialize FastAPI app
app = FastAPI(
    title="Blynk Weather Monitoring API",
    description="FastAPI service for fetching weather data, sending AI-based recommendations, and interacting with Blynk.",
    version="1.0.0"
)

# ✅ CORS Middleware (Allows external access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include API Routes from `routes.py`
app.include_router(router)

# ✅ Root endpoint for testing if the API is running
@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}

# ✅ Updated weather endpoint to support both `lat/lon` and `latitude/longitude`
@app.get("/weather")
def fetch_weather(
    location: str = Query(None),
    latitude: float = Query(None, alias="lat"),  # Accepts "lat"
    longitude: float = Query(None, alias="lon")  # Accepts "lon"
):
    if location:
        latitude, longitude = get_lat_lon_from_location(location)

    if latitude is None or longitude is None:
        raise HTTPException(status_code=400, detail="Latitude and longitude are required")

    return get_weather_data(latitude, longitude)