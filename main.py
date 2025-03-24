import os
from fastapi import FastAPI
from routes.weather_routes import weather_router
from routes.blynk_routes import blynk_router

app = FastAPI(title="Weather AI Backend")

# ✅ Include routers
app.include_router(weather_router, prefix="/api", tags=["Weather"])
app.include_router(blynk_router, prefix="/blynk", tags=["Blynk"])

# ✅ Root endpoint to check API status
@app.get("/")
def home():
    return {"message": "Weather AI Backend is running!"}

# ✅ Ensure environment variables are loaded
if not os.getenv("BLYNK_AUTH_TOKEN"):
    print("⚠️ Warning: BLYNK_AUTH_TOKEN is missing. Blynk integration may not work.")
