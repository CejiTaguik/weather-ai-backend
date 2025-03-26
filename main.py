from fastapi import FastAPI
from routes import router
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Weather AI Backend")

# Include API routes
app.include_router(router)

@app.get("/")
def home():
    return {"message": "Weather AI Backend is running!"}