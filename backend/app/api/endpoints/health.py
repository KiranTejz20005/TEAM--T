"""
Health check endpoints for FinMDA-Bot.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.database import get_db
from app.schemas import HealthResponse
from app.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify system status."""
    
    # Check database connection
    try:
        db.execute("SELECT 1")
        database_status = "healthy"
    except Exception as e:
        database_status = f"unhealthy: {str(e)}"
    
    # Check services status
    services_status = {
        "database": database_status,
        "openai_api": "configured" if settings.openai_api_key else "missing",
        "upload_directory": "ready" if os.path.exists(settings.upload_directory) else "missing",
        "chroma_directory": "ready" if os.path.exists(settings.chroma_persist_directory) else "missing"
    }
    
    # Determine overall status
    overall_status = "healthy" if all(
        status in ["healthy", "ready", "configured"] 
        for status in services_status.values()
    ) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        database_status=database_status,
        services_status=services_status
    )
