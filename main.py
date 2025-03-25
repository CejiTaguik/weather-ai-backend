import uvicorn
from fastapi import FastAPI
from routes import router  # Ensure you merged weather + Blynk routes

app = FastAPI(title="Weather AI Backend")

# Include routes
app.include_router(router, prefix="/api")

@app.get("/")
def home():
    return {"message": "Weather AI Backend is running on Railway!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 10000)), reload=True)
