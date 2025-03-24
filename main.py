from fastapi import FastAPI
from routes import weather_router, blynk_router  # Import Blynk router

app = FastAPI(title="Weather AI Backend")

# Include routers
app.include_router(weather_router, prefix="/api")
app.include_router(blynk_router, prefix="/blynk")  # Add Blynk integration

# Root endpoint
@app.get("/")
def home():
    return {"message": "Weather AI Backend is running!"}
