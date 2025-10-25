"""
Document processing endpoints for FinMDA-Bot.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.models import Document
from app.schemas import DocumentResponse, DocumentDetail, FileUploadResponse
from app.services.document_processor import DocumentProcessor
from app.config import settings

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a financial document."""
    
    # Validate file type
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.allowed_file_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} not allowed. Allowed types: {settings.allowed_file_types}"
        )
    
    # Validate file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File size {file_size / 1024 / 1024:.2f}MB exceeds limit of {settings.max_file_size_mb}MB"
        )
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = file.filename.split('.')[-1]
    safe_filename = f"{file_id}.{file_extension}"
    file_path = os.path.join(settings.upload_directory, safe_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Create database record
    document = Document(
        filename=file.filename,
        file_path=file_path,
        file_type=file_extension,
        file_size=file_size
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Process document asynchronously
    try:
        processor = DocumentProcessor()
        await processor.process_document(document.id, file_path, file_extension)
        
        # Update processing status
        document.is_processed = True
        db.commit()
        
        processing_status = "completed"
    except Exception as e:
        # Update error status
        document.processing_error = str(e)
        db.commit()
        
        processing_status = "failed"
    
    return FileUploadResponse(
        document_id=document.id,
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        upload_date=document.upload_date,
        processing_status=processing_status
    )


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all uploaded documents."""
    documents = db.query(Document).offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific document."""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a document and its associated data."""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from filesystem
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # Delete from database (cascade will handle related records)
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}
