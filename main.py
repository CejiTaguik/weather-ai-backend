from fastapi import FastAPI
from routes import router  

app = FastAPI(title="Weather AI Backend")

# ✅ Include the unified API router
app.include_router(router, prefix="/api")

# ✅ Root endpoint (Check if FastAPI is running)
@app.get("/")
def home():
    return {"message": "Weather AI Backend is running!"}
