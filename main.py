from fastapi import FastAPI
from routes import recommendation_router

app = FastAPI()

# Include the recommendation router
app.include_router(recommendation_router)

@app.get("/")
def read_root():
    return {"message": "Weather AI Backend is running."}
