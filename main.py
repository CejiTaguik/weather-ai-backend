from fastapi import FastAPI
from routes import weather_router

app = FastAPI(title="Weather AI Backend")

# Include the weather router
app.include_router(weather_router, prefix="/api")

# Root endpoint
@app.get("/")
def home():
    return {"message": "Weather AI Backend is running!"}
