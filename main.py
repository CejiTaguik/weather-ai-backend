from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import recommendation_router

app = FastAPI()

# Enable CORS (allows frontend or other domains to make requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify specific domains instead of "*"
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, etc.
    allow_headers=["*"],
)

# Include the router
app.include_router(recommendation_router)

# Root route (optional, for testing)
@app.get("/")
def read_root():
    return {"message": "Weather AI Backend is running!"}
