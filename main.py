from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import openai

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

# FastAPI app
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class QuestionRequest(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/ask")
async def ask_question(query: QuestionRequest):
    question = query.question.strip()

    # Optional filter: reject clearly unrelated questions
    unrelated_keywords = ["movie", "weather", "politics", "sports", "actor", "news", "recipe"]
    if any(word in question.lower() for word in unrelated_keywords):
        return {"answer": "❌ This chatbot only answers Python programming-related questions."}

    try:
        # Query OpenRouter with a strong Python-only prompt
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful and expert Python programming assistant. "
                        "Only answer questions that are related to Python. "
                        "If the question is not related to Python, politely refuse to answer."
                    )
                },
                {"role": "user", "content": question}
            ],
            temperature=0.5,
        )
        result = response["choices"][0]["message"]["content"].strip()
        return {"answer": result}

    except Exception as e:
        return JSONResponse(status_code=500, content={"answer": f"❌ Error: {str(e)}"})
