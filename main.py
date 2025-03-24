from fastapi import FastAPI
from routes import router  # Import merged router

app = FastAPI(title="Weather AI Backend")

# Include router
app.include_router(router, prefix="/api")

# Root endpoint
@app.get("/")
def home():
    return {"message": "Weather AI Backend is running!"}
