"""
SQLAlchemy models for FinMDA-Bot.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Document(Base):
    """Document model for storing uploaded financial documents."""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_error = Column(Text, nullable=True)
    
    # Extracted content
    extracted_text = Column(Text, nullable=True)
    extracted_tables = Column(JSON, nullable=True)
<<<<<<< HEAD
    document_metadata = Column(JSON, nullable=True)
=======
    metadata = Column(JSON, nullable=True)
>>>>>>> 5c3a0a0f3539fc0d352cb6c8a94fa282129f33e9
    
    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="document")


class ChatSession(Base):
    """Chat session model for tracking conversations."""
    
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    session_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    """Chat message model for storing conversation history."""
    
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # AI-specific fields
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    confidence_score = Column(Float, nullable=True)
    citations = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class FinancialAnalysis(Base):
    """Financial analysis results model."""
    
    __tablename__ = "financial_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    analysis_type = Column(String(50), nullable=False)  # 'ratios', 'forecast', 'trends'
    results = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Analysis metadata
    model_version = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    validation_status = Column(String(20), default="pending")  # 'pending', 'validated', 'failed'


class DocumentChunk(Base):
    """Document chunk model for RAG system."""
    
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
<<<<<<< HEAD
    chunk_metadata = Column(JSON, nullable=True)
=======
    metadata = Column(JSON, nullable=True)
>>>>>>> 5c3a0a0f3539fc0d352cb6c8a94fa282129f33e9
    embedding_id = Column(String(100), nullable=True)  # ChromaDB embedding ID
    
    # Chunk characteristics
    chunk_type = Column(String(20), nullable=False)  # 'text', 'table', 'metadata'
    page_number = Column(Integer, nullable=True)
    section = Column(String(100), nullable=True)

