from fastapi import FastAPI
from routes import router
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get port from Railway environment (fallback to 10000 for local testing)
PORT = int(os.getenv("PORT", 10000))

# Initialize FastAPI app
app = FastAPI(title="Weather AI Backend")

# Include API routes
app.include_router(router)

@app.get("/")
def home():
    return {"message": "Weather AI Backend is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
