from fastapi import FastAPI
from routes import router

app = FastAPI(title="Weather AI Backend")

# Include all routes
app.include_router(router)
