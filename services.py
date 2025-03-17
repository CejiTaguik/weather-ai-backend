import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_recommendation(user_input: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant for weather recommendations."},
            {"role": "user", "content": user_input}
        ],
        max_tokens=1500,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()
