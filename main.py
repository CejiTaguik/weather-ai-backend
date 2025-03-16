import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()
 
# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the request model
class WeatherData(BaseModel):
    condition: str
    temperature: float
    humidity: float

@app.get("/")
async def root():
    return {"message": "Weather AI Backend is running!"}

@app.post("/recommendation")
async def get_recommendation(data: WeatherData):
    try:
        prompt = (
            f"Given the weather condition is '{data.condition}', "
            f"the temperature is {data.temperature}°C, and humidity is {data.humidity}%, "
            "provide an actionable recommendation."
        )

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant providing weather-based recommendations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )

        recommendation = response.choices[0].message.content.strip()
        return {"recommendation": recommendation}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app with dynamic port detection
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
