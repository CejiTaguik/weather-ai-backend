from fastapi import FastAPI
from routes import router
import uvicorn
import os

app = FastAPI()

# Include routes from routes.py
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 10000)), reload=True)
