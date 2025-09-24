# app/main.py

from fastapi import FastAPI
from app.api.endpoints import document

# Create the main FastAPI application instance
app = FastAPI(
    title="PROJECT-2: AI Document Summarizer",
    description="API for document summarization and Q&A using Ollama and RAG."
)

@app.get("/")
async def root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "PROJECT-2 API is running successfully!"}

app.include_router(document.router, tags=["Document Operations"])
