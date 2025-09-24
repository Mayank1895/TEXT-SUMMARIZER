# app/services/document_service.py

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from fastapi import HTTPException, status

class DocumentService:
    def __init__(self, ollama_model: str = "mistral"):
        """
        Initializes the document service with the specified Ollama model.
        """
        self.ollama_model = ollama_model
        # Use the updated OllamaEmbeddings class
        self.embeddings = OllamaEmbeddings(model=ollama_model)
        self.vector_db = None
        self.qa_chain = None

    async def process_document(self, file_path: str):
        """
        Loads and processes a PDF document, and stores its chunks in a vector database.
        
        Args:
            file_path (str): The path to the PDF document.
        """
        # Load the PDF document
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)

        # Create the vector store from the document chunks
        self.vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=f"./chroma_db/{os.path.basename(file_path).split('.')[0]}"
        )
        self.vector_db.persist()
        
        # Set up the RetrievalQA chain for Q&A
        self.llm = Ollama(model=self.ollama_model)
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_db.as_retriever()
        )

        return len(chunks)

    async def get_summary(self, question: str):
        """
        Generates a summary of the document using the RAG-based QA chain.
        """
        if not self.qa_chain:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No document has been processed yet. Please upload a PDF."
            )
        
        # Create a specific prompt for summarization
        prompt = f"Provide a comprehensive summary of the document based on the following question: '{question}'. Make sure the summary is detailed and includes all key points. Do not include any information that is not in the document."
        
        response = self.qa_chain.run(prompt)
        return response

    async def get_answer(self, question: str):
        """
        Answers a question about the uploaded document.
        """
        if not self.qa_chain:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No document has been processed yet. Please upload a PDF."
            )
            
        response = self.qa_chain.run(question)
        return response
