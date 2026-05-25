from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.rag_service import index_documents, process_chat

app = FastAPI(title="TRUEAILAB RAG Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    sessionId: str
    message: str


@app.on_event("startup")
def startup_event():
    index_documents()


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/api/chat")
def chat(request: ChatRequest):
    if not request.message.strip():
        return {
            "error": "Message field is required"
        }

    if not request.sessionId.strip():
        return {
            "error": "SessionId field is required"
        }

    try:
        response = process_chat(request.sessionId, request.message)
        return response

    except Exception as e:
        return {
            "error": str(e)
        }