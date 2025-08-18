from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from contextlib import asynccontextmanager
import sys
from pathlib import Path
import shutil
import os
import time

# Add src to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.ingestion.document_loader import DocumentLoader
from src.ingestion.vector_store import VectorStoreManager
from src.retrieval.context_retriever import ContextRetriever
from src.orchestration.crew_manager import StudentLearningCrew
from config.settings import UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE, VECTORSTORE_DIR, get_vectorstore_path, list_available_vectorstores

# Global variables for tracking system state
active_document_stores = {}  # Maps document names to their vector store paths

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    global active_document_stores
    try:
        print("🚀 Initializing Student Learning Framework API...")
        # Check for existing vector stores
        available_stores = list_available_vectorstores()
        if not available_stores:
            print("⚠️ No vector stores found. Upload documents to get started.")
        else:
            print(f"✅ Found {len(available_stores)} document vector stores")
            # Map available stores to document names
            for store_path in available_stores:
                doc_name = store_path.name.replace('_faiss_index', '')
                active_document_stores[doc_name] = store_path
        print("✅ Student Learning Framework API ready!")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
    yield  # API is running
    print("👋 Shutting down Student Learning Framework API...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Student Learning Framework API",
    description="Multi-Agent RAG System with Per-Document Vector Stores",
    version="2.0.0",
    lifespan=lifespan
)

# -------- ENABLE CORS FOR FRONTEND DEV ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class QuestionInput(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="The question to ask the learning system")
    document_name: Optional[str] = Field(None, description="Name of document to query (without extension). If not provided, uses most recent.")

class AnswerOutput(BaseModel):
    context: str = Field(description="Retrieved context from documents")
    expert_responses: Dict[str, str] = Field(description="Responses from each expert agent")
    final_answer: str = Field(description="Final synthesized answer")
    document_used: str = Field(description="Document that was queried")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class SystemStatus(BaseModel):
    status: str
    message: str
    available_documents: List[str]
    total_vector_stores: int

# Helper Functions
def get_most_recent_document():
    """Get the most recently uploaded document"""
    global active_document_stores
    if not active_document_stores:
        return None
    if not UPLOAD_DIR.exists():
        return None
    files = [f for f in UPLOAD_DIR.iterdir() if f.is_file()]
    if not files:
        return None
    most_recent = max(files, key=lambda f: f.stat().st_mtime)
    doc_name = most_recent.stem
    return doc_name if doc_name in active_document_stores else None

def create_crew_for_document(document_name: str):
    """Create a crew system for a specific document"""
    global active_document_stores
    if document_name not in active_document_stores:
        raise HTTPException(status_code=404, detail=f"Document '{document_name}' not found")
    store_path = active_document_stores[document_name]
    if not store_path.exists():
        raise HTTPException(status_code=404, detail=f"Vector store for '{document_name}' not found")
    retriever = ContextRetriever(str(store_path))
    crew_system = StudentLearningCrew(retriever)
    return crew_system

# API Endpoints
@app.get("/")
async def root():
    """Welcome message and API information"""
    return {
        "message": "Welcome to Student Learning Framework API v2.0",
        "description": "Multi-Agent RAG System with Per-Document Vector Stores",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "ask_question": "POST /ask_question",
            "upload_document": "POST /upload_document",
            "list_documents": "GET /list_documents",
            "delete_document": "DELETE /delete_document",
            "system_status": "GET /status"
        }
    }

@app.post("/ask_question", response_model=AnswerOutput)
async def ask_question(question_input: QuestionInput):
    global active_document_stores
    if not active_document_stores:
        raise HTTPException(
            status_code=503, 
            detail="No documents available. Please upload documents first."
        )
    # Determine which document to use
    document_name = question_input.document_name
    if not document_name:
        document_name = get_most_recent_document()
        if not document_name:
            raise HTTPException(status_code=404, detail="No documents available")
    # Validate document exists
    if document_name not in active_document_stores:
        available_docs = list(active_document_stores.keys())
        raise HTTPException(
            status_code=404, 
            detail=f"Document '{document_name}' not found. Available: {available_docs}"
        )
    question = question_input.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        start_time = time.time()
        crew_system = create_crew_for_document(document_name)
        result = crew_system.process_question(question)
        processing_time = time.time() - start_time
        return AnswerOutput(
            context=result.get("context", ""),
            expert_responses=result.get("expert_outputs", {}),
            final_answer=result.get("final_answer", ""),
            document_used=document_name,
            processing_time=round(processing_time, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/status", response_model=SystemStatus)
async def system_status():
    global active_document_stores
    available_docs = list(active_document_stores.keys())
    return SystemStatus(
        status="ready" if active_document_stores else "no_documents",
        message=f"System ready with {len(available_docs)} documents" if available_docs else "No documents uploaded",
        available_documents=available_docs,
        total_vector_stores=len(available_docs)
    )

@app.post("/upload_document", summary="Upload and process a document")
async def upload_document(
    file: UploadFile = File(..., description="Document to upload"),
    background_tasks: BackgroundTasks = None
):
    global active_document_stores
    # Validate file type
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_extension} not supported. Allowed: {ALLOWED_EXTENSIONS}"
        )
    # Validate file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
        )
    # Create upload directory if it doesn't exist
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    # Save uploaded file
    file_location = UPLOAD_DIR / file.filename
    try:
        # Save the uploaded file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"✅ File saved: {file_location}")
        # Background task to ingest the document
        def ingest_uploaded_document(file_path: str, filename: str):
            global active_document_stores
            try:
                print(f"🔄 Starting ingestion of: {file_path}")
                loader = DocumentLoader()
                vector_manager = VectorStoreManager()
                documents = loader.load(file_path)
                print(f"📄 Loaded {len(documents)} document chunks")
                if not documents:
                    raise ValueError("No documents loaded - file may be empty or corrupted")
                valid_documents = [doc for doc in documents if doc.page_content.strip()]
                if not valid_documents:
                    raise ValueError("All document pages are empty after text extraction")
                print(f"✅ Found {len(valid_documents)} valid document chunks")
                store_path = get_vectorstore_path(filename)
                vector_manager.from_documents(valid_documents, str(store_path))
                print(f"🔍 Vector store created: {store_path}")
                doc_name = Path(filename).stem
                active_document_stores[doc_name] = store_path
                print("✅ Document ingestion completed successfully!")
            except Exception as e:
                print(f"❌ Ingestion failed: {e}")
                import traceback
                traceback.print_exc()
        # Add ingestion to background tasks
        if background_tasks:
            background_tasks.add_task(ingest_uploaded_document, str(file_location), file.filename)
            processing_message = "Document uploaded and processing started in background"
        else:
            ingest_uploaded_document(str(file_location), file.filename)
            processing_message = "Document uploaded and processed successfully"
        return JSONResponse(content={
            "message": processing_message,
            "filename": file.filename,
            "document_name": Path(file.filename).stem,
            "file_path": str(file_location),
            "file_size": f"{file.size / 1024 / 1024:.2f} MB" if file.size else "Unknown",
            "status": "uploaded"
        })
    except Exception as e:
        # Clean up file if processing failed
        if file_location.exists():
            file_location.unlink()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to save file: {str(e)}"
        )

@app.delete("/delete_document", summary="Delete document and its vector store")
async def delete_document(filename: str):
    global active_document_stores
    file_path = UPLOAD_DIR / filename
    doc_name = Path(filename).stem
    if not file_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"File '{filename}' not found in upload directory"
        )
    try:
        file_size = file_path.stat().st_size / 1024 / 1024  # MB
        file_path.unlink()
        print(f"🗑️ Deleted file: {filename}")
        store_path = get_vectorstore_path(filename)
        if store_path.exists():
            shutil.rmtree(store_path)
            print(f"🗑️ Deleted vector store: {store_path}")
        if doc_name in active_document_stores:
            del active_document_stores[doc_name]
        return JSONResponse(content={
            "message": f"Successfully deleted '{filename}' and its vector store",
            "deleted_file": filename,
            "document_name": doc_name,
            "file_size": f"{file_size:.2f} MB",
            "vector_store_cleared": True
        })
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete document: {str(e)}"
        )

@app.delete("/delete_all_documents", summary="Delete all documents and vector stores")
async def delete_all_documents():
    global active_document_stores
    try:
        files_deleted = []
        total_size = 0
        if UPLOAD_DIR.exists():
            for file_path in UPLOAD_DIR.iterdir():
                if file_path.is_file():
                    file_size = file_path.stat().st_size / 1024 / 1024  # MB
                    total_size += file_size
                    files_deleted.append({
                        "filename": file_path.name,
                        "size_mb": round(file_size, 2)
                    })
                    file_path.unlink()
        print(f"🗑️ Deleted {len(files_deleted)} files")
        if VECTORSTORE_DIR.exists():
            shutil.rmtree(VECTORSTORE_DIR)
            print("🗑️ Deleted all vector stores")
        active_document_stores.clear()
        return JSONResponse(content={
            "message": f"Successfully deleted all documents and vector stores",
            "files_deleted": files_deleted,
            "total_files": len(files_deleted),
            "total_size_mb": round(total_size, 2),
            "vector_stores_cleared": True
        })
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete all documents: {str(e)}"
        )

@app.get("/list_documents", summary="List all uploaded documents")
async def list_documents():
    global active_document_stores
    try:
        if not UPLOAD_DIR.exists():
            return {
                "documents": [], 
                "total_files": 0, 
                "total_size_mb": 0,
                "available_for_query": []
            }
        documents = []
        total_size = 0
        for file_path in UPLOAD_DIR.iterdir():
            if file_path.is_file():
                file_size = file_path.stat().st_size / 1024 / 1024  # MB
                total_size += file_size
                doc_name = file_path.stem
                has_vector_store = doc_name in active_document_stores
                documents.append({
                    "filename": file_path.name,
                    "document_name": doc_name,
                    "size_mb": round(file_size, 2),
                    "uploaded": file_path.stat().st_mtime,
                    "extension": file_path.suffix.lower(),
                    "has_vector_store": has_vector_store,
                    "queryable": has_vector_store
                })
        documents.sort(key=lambda x: x["uploaded"], reverse=True)
        return {
            "documents": documents,
            "total_files": len(documents),
            "total_size_mb": round(total_size, 2),
            "available_for_query": [doc["document_name"] for doc in documents if doc["queryable"]]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to list documents: {str(e)}"
        )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "message": "Please check the API documentation at /docs"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "Something went wrong. Please try again later."}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005, reload=True)
