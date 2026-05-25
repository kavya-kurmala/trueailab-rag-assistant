import json
from app.vectorstore.memory_store import MemoryVectorStore
from app.services.llm_service import generate_embedding, generate_answer

vector_store = MemoryVectorStore()
chat_history = {}


def chunk_text(text, chunk_size=400):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


def index_documents():
    with open("docs.json", "r", encoding="utf-8") as file:
        documents = json.load(file)

    for doc in documents:
        title = doc["title"]
        content = doc["content"]
        chunks = chunk_text(content)

        for index, chunk in enumerate(chunks):
            embedding = generate_embedding(chunk)

            metadata = {
                "title": title,
                "chunk_id": index,
                "source_document": title,
                "content": chunk
            }

            vector_store.add(embedding, metadata)

    print("Documents indexed successfully.")


def get_history(session_id):
    history = chat_history.get(session_id, [])
    recent_history = history[-5:]

    formatted_history = ""

    for item in recent_history:
        formatted_history += f"User: {item['user']}\nAssistant: {item['assistant']}\n"

    return formatted_history


def save_history(session_id, user_message, assistant_reply):
    if session_id not in chat_history:
        chat_history[session_id] = []

    chat_history[session_id].append({
        "user": user_message,
        "assistant": assistant_reply
    })


def process_chat(session_id, message):
    query_embedding = generate_embedding(message)

    retrieved_chunks = vector_store.search(
        query_embedding=query_embedding,
        top_k=3,
        threshold=0.70
    )

    print("Similarity scores:", [
        round(chunk["score"], 3) for chunk in retrieved_chunks
    ])

    if not retrieved_chunks:
        fallback = "I could not find enough information in the knowledge base to answer this question."
        save_history(session_id, message, fallback)

        return {
            "reply": fallback,
            "tokensUsed": 0,
            "retrievedChunks": 0
        }

    context = "\n\n".join([
        f"Title: {chunk['metadata']['title']}\nContent: {chunk['metadata']['content']}"
        for chunk in retrieved_chunks
    ])

    history = get_history(session_id)

    prompt = f"""
You are a helpful assistant.

Use ONLY the provided context to answer the user question.

Context:
{context}

Conversation History:
{history}

Question:
{message}

Answer:
"""

    reply = generate_answer(prompt)

    if "Gemini API could not generate" in reply or "quota" in reply.lower():
        reply = retrieved_chunks[0]["metadata"]["content"]
    save_history(session_id, message, reply)

    return {
        "reply": reply,
        "tokensUsed": 0,
        "retrievedChunks": len(retrieved_chunks)
    }