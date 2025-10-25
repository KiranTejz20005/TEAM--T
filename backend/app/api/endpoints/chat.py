"""
Chat and conversational AI endpoints for FinMDA-Bot.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import time

from app.database import get_db
from app.models import ChatSession, ChatMessage, Document
from app.schemas import (
    ChatQueryRequest, ChatQueryResponse, ChatSessionCreate, 
    ChatSessionResponse, ChatMessageResponse
)
from app.services.agent_system import AgentSystem
from app.services.rag_service import RAGService

router = APIRouter()


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new chat session."""
    
    # Verify document exists if provided
    if session_data.document_id:
        document = db.query(Document).filter(Document.id == session_data.document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
    
    # Create session
    session = ChatSession(
        document_id=session_data.document_id,
        session_name=session_data.session_name
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return ChatSessionResponse(
        id=session.id,
        document_id=session.document_id,
        session_name=session.session_name,
        created_at=session.created_at,
        last_activity=session.last_activity,
        message_count=0
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get chat session details."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    message_count = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).count()
    
    return ChatSessionResponse(
        id=session.id,
        document_id=session.document_id,
        session_name=session.session_name,
        created_at=session.created_at,
        last_activity=session.last_activity,
        message_count=message_count
    )


@router.post("/query", response_model=ChatQueryResponse)
async def chat_query(
    query_data: ChatQueryRequest,
    db: Session = Depends(get_db)
):
    """Process a chat query using the multi-agent system."""
    
    start_time = time.time()
    
    # Get or create session
    if query_data.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == query_data.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        # Create new session
        session = ChatSession(
            document_id=query_data.document_id,
            session_name=f"Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Save user message
    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=query_data.query
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    try:
        # Initialize services
        agent_system = AgentSystem()
        rag_service = RAGService()
        
        # Get document context if available
        context = ""
        if session.document_id:
            document = db.query(Document).filter(Document.id == session.document_id).first()
            if document and document.is_processed:
                # Retrieve relevant context using RAG
                context = await rag_service.retrieve_context(
                    query_data.query,
                    document_id=session.document_id
                )
        
        # Process query through agent system
        response_data = await agent_system.process_query(
            query=query_data.query,
            context=context,
            session_id=session.id,
            document_id=session.document_id
        )
        
        # Save assistant response
        assistant_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=response_data["response"],
            model_used=response_data.get("model_used"),
            tokens_used=response_data.get("tokens_used"),
            confidence_score=response_data.get("confidence_score"),
            citations=response_data.get("citations")
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        # Update session activity
        session.last_activity = datetime.utcnow()
        db.commit()
        
        processing_time = time.time() - start_time
        
        return ChatQueryResponse(
            response=response_data["response"],
            session_id=session.id,
            message_id=assistant_message.id,
            confidence_score=response_data.get("confidence_score"),
            citations=response_data.get("citations"),
            processing_time=processing_time,
            model_used=response_data.get("model_used", "gpt-4")
        )
        
    except Exception as e:
        # Save error message and return a graceful ChatQueryResponse
        error_text = f"I apologize, but I encountered an error processing your request: {str(e)}"
        error_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=error_text
        )
        db.add(error_message)
        db.commit()
        db.refresh(error_message)

        processing_time = time.time() - start_time
        return ChatQueryResponse(
            response=error_text,
            session_id=session.id,
            message_id=error_message.id,
            confidence_score=0.0,
            citations=[],
            processing_time=processing_time,
            model_used="gemini-1.5-flash",
        )


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    session_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get chat messages for a session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).offset(skip).limit(limit).all()
    
    return messages
