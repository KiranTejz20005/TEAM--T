"""
FinMDA-Bot FastAPI application entry point - Simplified version.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import os

# Create FastAPI application
app = FastAPI(
    title="FinMDA-Bot",
    version="1.0.0",
    description="Financial Multi-Domain AI Assistant for document analysis and insights",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to FinMDA-Bot",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_url": "/api/v1/health"
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "FinMDA-Bot API"
    }

@app.get("/api/v1/chat")
async def chat_test():
    """Simple chat test endpoint."""
    return {
        "message": "Chat endpoint is working!",
        "status": "success"
    }

@app.post("/api/v1/chat/query")
async def chat_query(data: dict):
    """Simple chat query endpoint."""
    query = data.get("query", "")
    return {
        "response": f"AI Response to: {query}",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/documents")
async def get_documents():
    """Get documents endpoint."""
    return {
        "documents": [],
        "message": "Documents endpoint is working!",
        "status": "success"
    }

@app.post("/api/v1/documents/upload")
async def upload_document(file: dict):
    """Upload document endpoint."""
    return {
        "message": "Document upload endpoint is working!",
        "status": "success",
        "file_id": "test-123"
    }

@app.get("/api/v1/analytics")
async def get_analytics():
    """Get analytics endpoint."""
    return {
        "analytics": {
            "total_documents": 0,
            "total_queries": 0,
            "success_rate": 100
        },
        "status": "success"
    }

@app.get("/api/v1/mda")
async def get_mda():
    """Get MD&A endpoint."""
    return {
        "mda": {
            "sections": ["Executive Summary", "Results of Operations", "Liquidity", "Risk Factors"],
            "status": "generated"
        },
        "status": "success"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
