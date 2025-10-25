"""
Pydantic schemas for request/response validation.
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


# Document Schemas
class DocumentBase(BaseModel):
    """Base document schema."""
    filename: str
    file_type: str
    file_size: int


class DocumentCreate(DocumentBase):
    """Schema for document upload."""
    pass


class DocumentResponse(DocumentBase):
    """Schema for document response."""
    id: int
    upload_date: datetime
    is_processed: bool
    processing_error: Optional[str] = None
    
    class Config:
        from_attributes = True


class DocumentDetail(DocumentResponse):
    """Detailed document schema."""
    extracted_text: Optional[str] = None
    extracted_tables: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


# Chat Schemas
class ChatMessageBase(BaseModel):
    """Base chat message schema."""
    content: str
    role: str = Field(..., pattern="^(user|assistant)$")


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating chat messages."""
    session_id: Optional[int] = None


class ChatMessageResponse(ChatMessageBase):
    """Schema for chat message response."""
    id: int
    timestamp: datetime
    model_used: Optional[str] = None
    confidence_score: Optional[float] = None
    citations: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    """Schema for creating chat sessions."""
    document_id: Optional[int] = None
    session_name: Optional[str] = None


class ChatSessionResponse(BaseModel):
    """Schema for chat session response."""
    id: int
    document_id: Optional[int] = None
    session_name: Optional[str] = None
    created_at: datetime
    last_activity: datetime
    message_count: int = 0
    
    class Config:
        from_attributes = True


# Analytics Schemas
class FinancialRatioRequest(BaseModel):
    """Schema for financial ratio calculation request."""
    document_id: int
    ratio_types: List[str] = Field(..., description="List of ratio types to calculate")
    period: Optional[str] = Field(None, description="Specific period for analysis")


class FinancialRatioResponse(BaseModel):
    """Schema for financial ratio response."""
    document_id: int
    ratios: Dict[str, Union[float, Dict[str, float]]]
    calculation_date: datetime
    confidence_score: Optional[float] = None


class ForecastRequest(BaseModel):
    """Schema for forecasting request."""
    document_id: int
    metric: str = Field(..., description="Metric to forecast (e.g., 'revenue', 'expenses')")
    periods: int = Field(12, description="Number of periods to forecast")
    method: str = Field("prophet", description="Forecasting method")


class ForecastResponse(BaseModel):
    """Schema for forecast response."""
    document_id: int
    metric: str
    forecast_data: List[Dict[str, Any]]
    confidence_intervals: List[Dict[str, Any]]
    created_at: datetime


class TrendAnalysisRequest(BaseModel):
    """Schema for trend analysis request."""
    document_id: int
    metrics: List[str] = Field(..., description="Metrics to analyze")
    time_period: Optional[str] = Field(None, description="Time period for analysis")


class TrendAnalysisResponse(BaseModel):
    """Schema for trend analysis response."""
    document_id: int
    trends: Dict[str, Dict[str, Any]]
    analysis_date: datetime


# Chat Query Schemas
class ChatQueryRequest(BaseModel):
    """Schema for chat query request."""
    query: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[int] = None
    document_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None


class ChatQueryResponse(BaseModel):
    """Schema for chat query response."""
    response: str
    session_id: int
    message_id: int
    confidence_score: Optional[float] = None
    citations: Optional[List[Dict[str, Any]]] = None
    processing_time: float
    model_used: str


# Health Check Schema
class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    timestamp: datetime
    version: str
    database_status: str
    services_status: Dict[str, str]


# Error Schemas
class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime


# File Upload Schema
class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    document_id: int
    filename: str
    file_type: str
    file_size: int
    upload_date: datetime
    processing_status: str

