import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise Exception("GEMINI_API_KEY is missing in .env file")


def generate_embedding(text: str):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={api_key}"
        payload = {
            "model": "models/gemini-embedding-001",
            "content": {
                "parts": [
                    {
                        "text": text
                    }
                ]
            }
        }

        response = requests.post(url, json=payload, timeout=30)
        data = response.json()

        if response.status_code != 200:
            raise Exception(data)

        return data["embedding"]["values"]

    except Exception as e:
        raise Exception(f"Embedding generation failed: {str(e)}")


def generate_answer(prompt: str):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 500
            }
        }

        response = requests.post(url, json=payload, timeout=30)
        data = response.json()

        if response.status_code != 200:
            if data.get("error", {}).get("code") == 429:
                return "Based on the retrieved knowledge base context, the answer is available in the relevant document. Gemini quota is currently exceeded, so please try again later for full LLM-generated response."
            raise Exception(data)

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return "Based on the retrieved context, Gemini API could not generate a response right now due to API limit or connection issue."