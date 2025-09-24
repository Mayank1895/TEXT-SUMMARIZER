# app/api/endpoints/document.py

import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.document_service import DocumentService

# Define the path where uploaded documents will be stored
UPLOAD_DIRECTORY = "documents"

# Initialize the document service globally
document_service = DocumentService()

# Create a FastAPI router for our document-related endpoints
router = APIRouter()

@router.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Accepts a PDF file, saves it to the documents directory, and processes it for summarization and Q&A.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files are allowed."
        )

    try:
        # Create the upload directory if it doesn't exist
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
        
        # Define the full file path
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)

        # Save the uploaded file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Log the successful file save
        print(f"File '{file.filename}' saved successfully to '{file_path}'")

        # Process the document with the new service
        num_chunks = await document_service.process_document(file_path)

        return {
            "filename": file.filename,
            "message": "File uploaded and processed successfully!",
            "chunks_created": num_chunks
        }
    except Exception as e:
        # Log the detailed error
        print(f"An error occurred during file processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during file processing: {e}"
        )

@router.post("/summarize/")
async def summarize_document():
    """
    Generates a summary of the uploaded document.
    """
    try:
        summary = await document_service.get_summary(question="Provide a concise summary.")
        return {"summary": summary}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating summary: {e}"
        )

@router.post("/ask/")
async def ask_question(question: str):
    """
    Answers a question about the uploaded document.
    """
    try:
        answer = await document_service.get_answer(question)
        return {"question": question, "answer": answer}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while getting answer: {e}"
        )
