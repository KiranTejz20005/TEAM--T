"""
Voice assistant API endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Dict, Any, Optional
import logging

from app.services.voice_assistant import VoiceAssistant
<<<<<<< HEAD
=======
from app.schemas import ChatRequest, ChatResponse
>>>>>>> 5c3a0a0f3539fc0d352cb6c8a94fa282129f33e9
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize voice assistant
voice_assistant = VoiceAssistant()


@router.post("/speech-to-text")
async def speech_to_text(
    audio_file: UploadFile = File(...),
    method: str = Form("whisper"),
    language: str = Form("en")
) -> Dict[str, Any]:
    """Convert speech to text."""
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        # Process speech to text
        result = await voice_assistant.speech_to_text(
            audio_data=audio_data,
            method=method,
            language=language
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in speech-to-text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Speech-to-text processing failed: {str(e)}")


@router.post("/text-to-speech")
async def text_to_speech(
    text: str = Form(...),
    voice_id: Optional[str] = Form(None),
    speed: float = Form(1.0),
    volume: float = Form(0.9)
) -> Dict[str, Any]:
    """Convert text to speech."""
    try:
        # Process text to speech
        result = await voice_assistant.text_to_speech(
            text=text,
            voice_id=voice_id,
            speed=speed,
            volume=volume
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in text-to-speech: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text-to-speech processing failed: {str(e)}")


@router.post("/voice-query")
async def process_voice_query(
    audio_file: UploadFile = File(...),
    context: str = Form(""),
    session_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Process a complete voice query (speech-to-text + processing + text-to-speech)."""
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        # Process complete voice query
        result = await voice_assistant.process_voice_query(
            audio_data=audio_data,
            context=context,
            session_id=session_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing voice query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice query processing failed: {str(e)}")


@router.post("/voice-sentiment")
async def analyze_voice_sentiment(
    audio_file: UploadFile = File(...)
) -> Dict[str, Any]:
    """Analyze sentiment from voice tone."""
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        # Analyze sentiment
        result = await voice_assistant.analyze_voice_sentiment(audio_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing voice sentiment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice sentiment analysis failed: {str(e)}")


@router.post("/voice-summary")
async def create_voice_summary(
    text: str = Form(...),
    max_length: int = Form(200)
) -> Dict[str, Any]:
    """Create a voice summary of text."""
    try:
        # Create voice summary
        result = await voice_assistant.create_voice_summary(
            text=text,
            max_length=max_length
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating voice summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice summary creation failed: {str(e)}")


@router.get("/voices")
async def get_available_voices() -> Dict[str, Any]:
    """Get list of available TTS voices."""
    try:
        voices = voice_assistant.get_available_voices()
        return {
            'voices': voices,
            'count': len(voices)
        }
        
    except Exception as e:
        logger.error(f"Error getting available voices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get available voices: {str(e)}")


@router.get("/languages")
async def get_supported_languages() -> Dict[str, Any]:
    """Get list of supported languages for speech recognition."""
    try:
        languages = voice_assistant.get_supported_languages()
        return {
            'languages': languages,
            'count': len(languages)
        }
        
    except Exception as e:
        logger.error(f"Error getting supported languages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get supported languages: {str(e)}")


@router.get("/voice-status")
async def get_voice_status() -> Dict[str, Any]:
    """Get voice assistant status and capabilities."""
    try:
        return {
            'status': 'active',
            'capabilities': {
                'speech_to_text': True,
                'text_to_speech': True,
                'voice_sentiment': True,
                'voice_summary': True,
                'multi_language': True
            },
            'engines': {
                'whisper': voice_assistant.whisper_model is not None,
                'google_speech': True,
                'tts': voice_assistant.tts_engine is not None
            },
            'supported_formats': ['wav', 'mp3', 'm4a', 'flac'],
            'max_file_size': '10MB'
        }
        
    except Exception as e:
        logger.error(f"Error getting voice status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get voice status: {str(e)}")
