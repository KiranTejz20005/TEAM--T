"""
TTS/STS integration service for chatbot with advanced voice capabilities.
"""
import asyncio
import base64
import io
import tempfile
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import json

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import whisper
except ImportError:
    whisper = None

try:
    import edge_tts
except ImportError:
    edge_tts = None

try:
    import pydub
    from pydub.playback import play
except ImportError:
    pydub = None
    play = None

import numpy as np

try:
    import soundfile as sf
except ImportError:
    sf = None
from app.config import settings


class TTSSTSIntegration:
    """Advanced TTS/STS integration for chatbot."""
    
    def __init__(self):
        """Initialize TTS/STS integration."""
        self.logger = logging.getLogger(__name__)
        self.recognizer = None
        self.tts_engine = None
        self.whisper_model = None
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize TTS/STS engines."""
        try:
            # Initialize TTS engine
            if pyttsx3:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.setProperty('volume', 0.9)
            
            # Initialize Whisper model
            if whisper:
                self.whisper_model = whisper.load_model("base")
            
            # Configure speech recognizer
            if sr:
                self.recognizer = sr.Recognizer()
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.8
            
        except Exception as e:
            self.logger.error(f"Error initializing TTS/STS engines: {str(e)}")
    
    async def process_voice_chat(
        self, 
        audio_data: bytes,
        context: str = "",
        session_id: Optional[int] = None,
        voice_settings: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Process voice chat with enhanced TTS/STS capabilities."""
        
        result = {
            'query_text': '',
            'response_text': '',
            'response_audio': None,
            'confidence': 0.0,
            'sentiment': 'neutral',
            'emotions': [],
            'processing_time': 0.0,
            'timestamp': datetime.utcnow().isoformat(),
            'success': False
        }
        
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Speech to Text with multiple engines
            stt_result = await self._enhanced_speech_to_text(audio_data)
            if not stt_result['success']:
                result['error'] = stt_result['error']
                return result
            
            result['query_text'] = stt_result['text']
            result['confidence'] = stt_result['confidence']
            
            # Step 2: Analyze sentiment and emotions
            sentiment_result = await self._analyze_voice_sentiment(audio_data)
            result['sentiment'] = sentiment_result['sentiment']
            result['emotions'] = sentiment_result['emotions']
            
            # Step 3: Process query with context
            response_text = await self._process_chat_query(
                stt_result['text'], 
                context, 
                sentiment_result
            )
            result['response_text'] = response_text
            
            # Step 4: Generate voice response with emotion
            tts_result = await self._generate_emotional_voice(
                response_text, 
                sentiment_result,
                voice_settings
            )
            if tts_result['success']:
                result['response_audio'] = tts_result['audio_data']
                result['duration'] = tts_result['duration']
            
            result['success'] = True
            
        except Exception as e:
            self.logger.error(f"Error processing voice chat: {str(e)}")
            result['error'] = str(e)
        
        finally:
            end_time = datetime.utcnow()
            result['processing_time'] = (end_time - start_time).total_seconds()
        
        return result
    
    async def _enhanced_speech_to_text(self, audio_data: bytes) -> Dict[str, Any]:
        """Enhanced speech-to-text with multiple engines."""
        result = {
            'text': '',
            'confidence': 0.0,
            'method': 'combined',
            'success': False
        }
        
        try:
            # Method 1: Whisper (best accuracy)
            whisper_result = await self._whisper_stt(audio_data)
            
            # Method 2: Google Speech Recognition
            google_result = await self._google_stt(audio_data)
            
            # Method 3: Azure Speech (if available)
            azure_result = await self._azure_stt(audio_data)
            
            # Combine results with confidence weighting
            results = []
            if whisper_result['success']:
                results.append(('whisper', whisper_result['text'], whisper_result['confidence']))
            if google_result['success']:
                results.append(('google', google_result['text'], google_result['confidence']))
            if azure_result['success']:
                results.append(('azure', azure_result['text'], azure_result['confidence']))
            
            if results:
                # Use the result with highest confidence
                best_result = max(results, key=lambda x: x[2])
                result['text'] = best_result[1]
                result['confidence'] = best_result[2]
                result['method'] = best_result[0]
                result['success'] = True
            else:
                result['error'] = 'All STT methods failed'
        
        except Exception as e:
            self.logger.error(f"Error in enhanced STT: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    async def _whisper_stt(self, audio_data: bytes) -> Dict[str, Any]:
        """Whisper speech-to-text."""
        result = {'success': False, 'text': '', 'confidence': 0.0}
        
        try:
            if not self.whisper_model:
                return result
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file.flush()
                
                transcription = self.whisper_model.transcribe(tmp_file.name)
                result['text'] = transcription["text"]
                result['confidence'] = 0.9  # Whisper doesn't provide confidence
                result['success'] = True
                
                os.unlink(tmp_file.name)
        
        except Exception as e:
            self.logger.error(f"Whisper STT error: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    async def _google_stt(self, audio_data: bytes) -> Dict[str, Any]:
        """Google Speech Recognition."""
        result = {'success': False, 'text': '', 'confidence': 0.0}
        
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file.flush()
                
                with sr.AudioFile(tmp_file.name) as source:
                    audio = self.recognizer.record(source)
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    result['text'] = text
                    result['confidence'] = 0.8
                    result['success'] = True
                except sr.UnknownValueError:
                    result['error'] = 'Could not understand audio'
                except sr.RequestError as e:
                    result['error'] = f'Google STT error: {e}'
                
                os.unlink(tmp_file.name)
        
        except Exception as e:
            self.logger.error(f"Google STT error: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    async def _azure_stt(self, audio_data: bytes) -> Dict[str, Any]:
        """Azure Speech Services (placeholder)."""
        # This would require Azure Speech SDK
        return {'success': False, 'text': '', 'confidence': 0.0}
    
    async def _analyze_voice_sentiment(self, audio_data: bytes) -> Dict[str, Any]:
        """Analyze voice sentiment and emotions."""
        result = {
            'sentiment': 'neutral',
            'confidence': 0.0,
            'emotions': [],
            'stress_level': 0.0,
            'energy_level': 0.0
        }
        
        try:
            # Convert audio to text first
            stt_result = await self._whisper_stt(audio_data)
            if not stt_result['success']:
                return result
            
            text = stt_result['text']
            
            # Analyze text sentiment
            sentiment = self._analyze_text_sentiment(text)
            result['sentiment'] = sentiment['sentiment']
            result['confidence'] = sentiment['confidence']
            
            # Extract emotions
            emotions = self._extract_emotions(text)
            result['emotions'] = emotions
            
            # Analyze voice characteristics
            voice_analysis = self._analyze_voice_characteristics(audio_data)
            result['stress_level'] = voice_analysis['stress_level']
            result['energy_level'] = voice_analysis['energy_level']
        
        except Exception as e:
            self.logger.error(f"Error analyzing voice sentiment: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def _analyze_text_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze text sentiment."""
        text_lower = text.lower()
        
        positive_words = [
            'good', 'great', 'excellent', 'positive', 'increase', 'growth', 
            'profit', 'success', 'improve', 'better', 'best', 'amazing'
        ]
        negative_words = [
            'bad', 'poor', 'negative', 'decrease', 'loss', 'decline', 
            'concern', 'worry', 'problem', 'issue', 'terrible', 'worst'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return {'sentiment': 'positive', 'confidence': min(0.9, 0.5 + (positive_count - negative_count) * 0.1)}
        elif negative_count > positive_count:
            return {'sentiment': 'negative', 'confidence': min(0.9, 0.5 + (negative_count - positive_count) * 0.1)}
        else:
            return {'sentiment': 'neutral', 'confidence': 0.5}
    
    def _extract_emotions(self, text: str) -> List[str]:
        """Extract emotions from text."""
        emotions = []
        text_lower = text.lower()
        
        emotion_keywords = {
            'excitement': ['excited', 'thrilled', 'enthusiastic', 'pumped'],
            'worry': ['worried', 'concerned', 'anxious', 'nervous'],
            'confidence': ['confident', 'sure', 'certain', 'optimistic'],
            'frustration': ['frustrated', 'annoyed', 'irritated', 'upset'],
            'curiosity': ['curious', 'interested', 'wondering', 'intrigued']
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                emotions.append(emotion)
        
        return emotions
    
    def _analyze_voice_characteristics(self, audio_data: bytes) -> Dict[str, float]:
        """Analyze voice characteristics."""
        try:
            # Convert audio data to numpy array for analysis
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Calculate basic audio features
            rms = np.sqrt(np.mean(audio_array**2))
            zero_crossings = np.sum(np.diff(np.sign(audio_array)) != 0)
            
            # Estimate stress level (simplified)
            stress_level = min(1.0, rms / 10000)  # Normalize RMS
            
            # Estimate energy level
            energy_level = min(1.0, np.mean(np.abs(audio_array)) / 1000)
            
            return {
                'stress_level': float(stress_level),
                'energy_level': float(energy_level)
            }
        
        except Exception as e:
            self.logger.error(f"Error analyzing voice characteristics: {str(e)}")
            return {'stress_level': 0.0, 'energy_level': 0.0}
    
    async def _process_chat_query(
        self, 
        query: str, 
        context: str, 
        sentiment_result: Dict[str, Any]
    ) -> str:
        """Process chat query with sentiment awareness."""
        # This would integrate with your existing chat system
        # For now, return a sentiment-aware response
        
        sentiment = sentiment_result.get('sentiment', 'neutral')
        emotions = sentiment_result.get('emotions', [])
        
        # Adjust response based on sentiment
        if sentiment == 'positive':
            prefix = "I'm glad to hear your positive outlook! "
        elif sentiment == 'negative':
            prefix = "I understand your concerns. Let me help you with "
        else:
            prefix = "I'll help you with "
        
        # Add emotion-aware context
        if 'excitement' in emotions:
            prefix += "I can see you're excited about this! "
        elif 'worry' in emotions:
            prefix += "I understand your concerns. "
        
        # Generate response based on query
        financial_keywords = ['revenue', 'profit', 'expense', 'ratio', 'forecast', 'trend']
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in financial_keywords):
            response = f"{prefix}your financial analysis. I can help you analyze financial documents, calculate ratios, and provide insights. Please upload your financial documents for detailed analysis."
        else:
            response = f"{prefix}your financial questions. I'm FinMDA-Bot, your AI financial assistant. I can help you with document analysis, ratio calculations, forecasting, and more. How can I assist you today?"
        
        return response
    
    async def _generate_emotional_voice(
        self, 
        text: str, 
        sentiment_result: Dict[str, Any],
        voice_settings: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate voice with emotional characteristics."""
        result = {
            'audio_data': None,
            'duration': 0.0,
            'success': False
        }
        
        try:
            sentiment = sentiment_result.get('sentiment', 'neutral')
            emotions = sentiment_result.get('emotions', [])
            stress_level = sentiment_result.get('stress_level', 0.0)
            energy_level = sentiment_result.get('energy_level', 0.0)
            
            # Adjust voice parameters based on sentiment
            if voice_settings is None:
                voice_settings = {}
            
            # Set rate based on energy level
            base_rate = voice_settings.get('rate', 150)
            rate = base_rate + (energy_level * 50)  # Higher energy = faster speech
            
            # Set volume based on stress level
            base_volume = voice_settings.get('volume', 0.9)
            volume = base_volume - (stress_level * 0.2)  # Higher stress = lower volume
            
            # Adjust text based on sentiment
            if sentiment == 'positive':
                text = f"Great news! {text}"
            elif sentiment == 'negative':
                text = f"I understand. {text}"
            
            # Generate speech
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                self.tts_engine.setProperty('rate', int(rate))
                self.tts_engine.setProperty('volume', volume)
                self.tts_engine.save_to_file(text, tmp_file.name)
                self.tts_engine.runAndWait()
                
                # Read the generated audio file
                with open(tmp_file.name, 'rb') as f:
                    audio_data = f.read()
                
                # Convert to base64
                result['audio_data'] = base64.b64encode(audio_data).decode('utf-8')
                result['success'] = True
                
                # Calculate duration
                audio = pydub.AudioSegment.from_wav(tmp_file.name)
                result['duration'] = len(audio) / 1000.0
                
                os.unlink(tmp_file.name)
        
        except Exception as e:
            self.logger.error(f"Error generating emotional voice: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    async def create_voice_summary_with_emotion(
        self, 
        text: str, 
        sentiment: str = 'neutral',
        max_length: int = 200
    ) -> Dict[str, Any]:
        """Create voice summary with emotional characteristics."""
        result = {
            'summary_text': '',
            'summary_audio': None,
            'duration': 0.0,
            'success': False
        }
        
        try:
            # Create summary
            if len(text) > max_length:
                summary_text = text[:max_length] + "..."
            else:
                summary_text = text
            
            # Add emotional context
            if sentiment == 'positive':
                summary_text = f"Exciting update: {summary_text}"
            elif sentiment == 'negative':
                summary_text = f"Important notice: {summary_text}"
            else:
                summary_text = f"Financial summary: {summary_text}"
            
            # Generate voice with emotion
            sentiment_result = {
                'sentiment': sentiment,
                'emotions': [],
                'stress_level': 0.0,
                'energy_level': 0.5
            }
            
            tts_result = await self._generate_emotional_voice(
                summary_text, 
                sentiment_result
            )
            
            if tts_result['success']:
                result['summary_text'] = summary_text
                result['summary_audio'] = tts_result['audio_data']
                result['duration'] = tts_result['duration']
                result['success'] = True
        
        except Exception as e:
            self.logger.error(f"Error creating emotional voice summary: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def get_voice_capabilities(self) -> Dict[str, Any]:
        """Get voice capabilities information."""
        return {
            'speech_to_text': {
                'engines': ['whisper', 'google', 'azure'],
                'languages': ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh'],
                'features': ['sentiment_analysis', 'emotion_detection', 'confidence_scoring']
            },
            'text_to_speech': {
                'engines': ['pyttsx3', 'edge_tts'],
                'features': ['emotional_voice', 'speed_control', 'volume_control'],
                'voices': self._get_available_voices()
            },
            'analysis': {
                'sentiment': True,
                'emotions': True,
                'stress_level': True,
                'energy_level': True
            }
        }
    
    def _get_available_voices(self) -> List[Dict[str, Any]]:
        """Get available TTS voices."""
        if not self.tts_engine:
            return []
        
        voices = self.tts_engine.getProperty('voices')
        return [
            {
                'id': voice.id,
                'name': voice.name,
                'languages': voice.languages,
                'gender': 'male' if 'male' in voice.name.lower() else 'female'
            }
            for voice in voices
        ]
