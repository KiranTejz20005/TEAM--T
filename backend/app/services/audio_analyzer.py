"""
Audio and transcript analysis service.
"""
import speech_recognition as sr
import whisper
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
import re
from io import BytesIO
import tempfile
import os

from app.config import settings


class AudioAnalyzer:
    """Service for analyzing audio files and transcripts."""
    
    def __init__(self):
        """Initialize audio analyzer."""
        self.logger = logging.getLogger(__name__)
        self.recognizer = sr.Recognizer()
        self.whisper_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize speech recognition models."""
        try:
            # Initialize Whisper model for better accuracy
            self.whisper_model = whisper.load_model("base")
        except Exception as e:
            self.logger.warning(f"Could not load Whisper model: {str(e)}")
            self.whisper_model = None
    
    async def analyze_audio(
        self, 
        audio_file_path: str,
        analysis_type: str = 'earnings_call'
    ) -> Dict[str, Any]:
        """Analyze audio file and extract financial insights."""
        
        analysis = {
            'audio_file': audio_file_path,
            'analysis_type': analysis_type,
            'timestamp': datetime.utcnow().isoformat(),
            'transcript': '',
            'sentiment_analysis': {},
            'financial_insights': {},
            'key_metrics': {},
            'speaker_analysis': {},
            'confidence_score': 0.0
        }
        
        try:
            # Transcribe audio
            transcript = await self._transcribe_audio(audio_file_path)
            analysis['transcript'] = transcript
            
            # Analyze sentiment
            sentiment = await self._analyze_sentiment(transcript)
            analysis['sentiment_analysis'] = sentiment
            
            # Extract financial insights
            financial_insights = await self._extract_financial_insights(transcript, analysis_type)
            analysis['financial_insights'] = financial_insights
            
            # Extract key metrics
            key_metrics = await self._extract_key_metrics(transcript)
            analysis['key_metrics'] = key_metrics
            
            # Analyze speakers
            speaker_analysis = await self._analyze_speakers(transcript)
            analysis['speaker_analysis'] = speaker_analysis
            
            # Calculate confidence score
            analysis['confidence_score'] = self._calculate_confidence_score(
                transcript, sentiment, financial_insights
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing audio: {str(e)}")
            analysis['error'] = str(e)
        
        return analysis
    
    async def _transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio file to text."""
        try:
            # Try Whisper first for better accuracy
            if self.whisper_model:
                result = self.whisper_model.transcribe(audio_file_path)
                return result["text"]
            
            # Fallback to speech_recognition
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
            
            # Try Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                self.logger.warning("Google Speech Recognition could not understand audio")
                return ""
            except sr.RequestError as e:
                self.logger.error(f"Could not request results from Google Speech Recognition: {e}")
                return ""
        
        except Exception as e:
            self.logger.error(f"Error transcribing audio: {str(e)}")
            return ""
    
    async def _analyze_sentiment(self, transcript: str) -> Dict[str, Any]:
        """Analyze sentiment of the transcript."""
        sentiment = {
            'overall_sentiment': 'neutral',
            'sentiment_score': 0.0,
            'positive_keywords': [],
            'negative_keywords': [],
            'neutral_keywords': [],
            'sentiment_by_section': {}
        }
        
        try:
            # Define financial sentiment keywords
            positive_keywords = [
                'growth', 'increase', 'improve', 'strong', 'excellent', 'outstanding',
                'profit', 'revenue', 'success', 'achievement', 'milestone', 'record',
                'expansion', 'opportunity', 'positive', 'optimistic', 'confident'
            ]
            
            negative_keywords = [
                'decline', 'decrease', 'weak', 'poor', 'loss', 'challenge', 'difficulty',
                'concern', 'risk', 'uncertainty', 'volatility', 'pressure', 'headwind',
                'recession', 'crisis', 'problem', 'issue', 'negative', 'pessimistic'
            ]
            
            # Count keyword occurrences
            text_lower = transcript.lower()
            positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
            negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
            
            # Calculate sentiment score
            total_keywords = positive_count + negative_count
            if total_keywords > 0:
                sentiment['sentiment_score'] = (positive_count - negative_count) / total_keywords
            
            # Determine overall sentiment
            if sentiment['sentiment_score'] > 0.2:
                sentiment['overall_sentiment'] = 'positive'
            elif sentiment['sentiment_score'] < -0.2:
                sentiment['overall_sentiment'] = 'negative'
            else:
                sentiment['overall_sentiment'] = 'neutral'
            
            # Extract specific keywords
            sentiment['positive_keywords'] = [kw for kw in positive_keywords if kw in text_lower]
            sentiment['negative_keywords'] = [kw for kw in negative_keywords if kw in text_lower]
            
            # Analyze sentiment by sections (if transcript is long enough)
            if len(transcript) > 1000:
                sections = self._split_transcript_into_sections(transcript)
                for i, section in enumerate(sections):
                    section_sentiment = self._analyze_section_sentiment(section)
                    sentiment['sentiment_by_section'][f'section_{i+1}'] = section_sentiment
        
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {str(e)}")
            sentiment['error'] = str(e)
        
        return sentiment
    
    def _split_transcript_into_sections(self, transcript: str, section_length: int = 500) -> List[str]:
        """Split transcript into sections for analysis."""
        words = transcript.split()
        sections = []
        
        for i in range(0, len(words), section_length):
            section = ' '.join(words[i:i + section_length])
            sections.append(section)
        
        return sections
    
    def _analyze_section_sentiment(self, section: str) -> Dict[str, Any]:
        """Analyze sentiment of a specific section."""
        positive_keywords = [
            'growth', 'increase', 'improve', 'strong', 'excellent', 'outstanding',
            'profit', 'revenue', 'success', 'achievement', 'milestone', 'record'
        ]
        
        negative_keywords = [
            'decline', 'decrease', 'weak', 'poor', 'loss', 'challenge', 'difficulty',
            'concern', 'risk', 'uncertainty', 'volatility', 'pressure', 'headwind'
        ]
        
        text_lower = section.lower()
        positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
        
        total_keywords = positive_count + negative_count
        sentiment_score = (positive_count - negative_count) / total_keywords if total_keywords > 0 else 0
        
        return {
            'sentiment_score': sentiment_score,
            'positive_count': positive_count,
            'negative_count': negative_count
        }
    
    async def _extract_financial_insights(self, transcript: str, analysis_type: str) -> Dict[str, Any]:
        """Extract financial insights from transcript."""
        insights = {
            'revenue_mentions': [],
            'profit_mentions': [],
            'growth_mentions': [],
            'risk_mentions': [],
            'opportunity_mentions': [],
            'key_financial_data': {},
            'forward_looking_statements': []
        }
        
        try:
            # Extract revenue mentions
            revenue_patterns = [
                r'revenue[:\s]*\$?([\d,]+\.?\d*)\s*(million|billion|thousand|k|m|b)?',
                r'sales[:\s]*\$?([\d,]+\.?\d*)\s*(million|billion|thousand|k|m|b)?',
                r'income[:\s]*\$?([\d,]+\.?\d*)\s*(million|billion|thousand|k|m|b)?'
            ]
            
            for pattern in revenue_patterns:
                matches = re.finditer(pattern, transcript, re.IGNORECASE)
                for match in matches:
                    value = match.group(1).replace(',', '')
                    unit = match.group(2) or ''
                    insights['revenue_mentions'].append({
                        'value': value,
                        'unit': unit,
                        'context': match.group(0),
                        'position': match.start()
                    })
            
            # Extract profit mentions
            profit_patterns = [
                r'profit[:\s]*\$?([\d,]+\.?\d*)\s*(million|billion|thousand|k|m|b)?',
                r'earnings[:\s]*\$?([\d,]+\.?\d*)\s*(million|billion|thousand|k|m|b)?',
                r'net\s+income[:\s]*\$?([\d,]+\.?\d*)\s*(million|billion|thousand|k|m|b)?'
            ]
            
            for pattern in profit_patterns:
                matches = re.finditer(pattern, transcript, re.IGNORECASE)
                for match in matches:
                    value = match.group(1).replace(',', '')
                    unit = match.group(2) or ''
                    insights['profit_mentions'].append({
                        'value': value,
                        'unit': unit,
                        'context': match.group(0),
                        'position': match.start()
                    })
            
            # Extract growth mentions
            growth_patterns = [
                r'growth[:\s]*([\d,]+\.?\d*)%',
                r'increase[:\s]*([\d,]+\.?\d*)%',
                r'up[:\s]*([\d,]+\.?\d*)%'
            ]
            
            for pattern in growth_patterns:
                matches = re.finditer(pattern, transcript, re.IGNORECASE)
                for match in matches:
                    value = match.group(1).replace(',', '')
                    insights['growth_mentions'].append({
                        'value': value,
                        'context': match.group(0),
                        'position': match.start()
                    })
            
            # Extract risk mentions
            risk_keywords = ['risk', 'challenge', 'concern', 'uncertainty', 'volatility', 'headwind']
            for keyword in risk_keywords:
                pattern = rf'\b{keyword}\b'
                matches = re.finditer(pattern, transcript, re.IGNORECASE)
                for match in matches:
                    insights['risk_mentions'].append({
                        'keyword': keyword,
                        'context': transcript[max(0, match.start()-50):match.end()+50],
                        'position': match.start()
                    })
            
            # Extract opportunity mentions
            opportunity_keywords = ['opportunity', 'potential', 'growth', 'expansion', 'market']
            for keyword in opportunity_keywords:
                pattern = rf'\b{keyword}\b'
                matches = re.finditer(pattern, transcript, re.IGNORECASE)
                for match in matches:
                    insights['opportunity_mentions'].append({
                        'keyword': keyword,
                        'context': transcript[max(0, match.start()-50):match.end()+50],
                        'position': match.start()
                    })
            
            # Extract forward-looking statements
            forward_looking_patterns = [
                r'we\s+expect',
                r'we\s+anticipate',
                r'we\s+believe',
                r'we\s+project',
                r'we\s+forecast',
                r'going\s+forward',
                r'in\s+the\s+future'
            ]
            
            for pattern in forward_looking_patterns:
                matches = re.finditer(pattern, transcript, re.IGNORECASE)
                for match in matches:
                    # Extract the sentence containing the forward-looking statement
                    start = max(0, match.start()-100)
                    end = min(len(transcript), match.end()+200)
                    sentence = transcript[start:end]
                    insights['forward_looking_statements'].append({
                        'statement': sentence,
                        'position': match.start()
                    })
            
        except Exception as e:
            self.logger.error(f"Error extracting financial insights: {str(e)}")
            insights['error'] = str(e)
        
        return insights
    
    async def _extract_key_metrics(self, transcript: str) -> Dict[str, Any]:
        """Extract key financial metrics from transcript."""
        metrics = {
            'revenue': None,
            'profit': None,
            'growth_rate': None,
            'margins': {},
            'ratios': {},
            'forecasts': {}
        }
        
        try:
            # Extract revenue
            revenue_pattern = r'revenue[:\s]*\$?([\d,]+\.?\d*)\s*(million|billion|thousand|k|m|b)?'
            revenue_match = re.search(revenue_pattern, transcript, re.IGNORECASE)
            if revenue_match:
                value = float(revenue_match.group(1).replace(',', ''))
                unit = revenue_match.group(2) or ''
                metrics['revenue'] = self._convert_to_millions(value, unit)
            
            # Extract profit
            profit_pattern = r'profit[:\s]*\$?([\d,]+\.?\d*)\s*(million|billion|thousand|k|m|b)?'
            profit_match = re.search(profit_pattern, transcript, re.IGNORECASE)
            if profit_match:
                value = float(profit_match.group(1).replace(',', ''))
                unit = profit_match.group(2) or ''
                metrics['profit'] = self._convert_to_millions(value, unit)
            
            # Extract growth rate
            growth_pattern = r'growth[:\s]*([\d,]+\.?\d*)%'
            growth_match = re.search(growth_pattern, transcript, re.IGNORECASE)
            if growth_match:
                metrics['growth_rate'] = float(growth_match.group(1).replace(',', ''))
            
            # Extract margins
            margin_patterns = {
                'gross_margin': r'gross\s+margin[:\s]*([\d,]+\.?\d*)%',
                'net_margin': r'net\s+margin[:\s]*([\d,]+\.?\d*)%',
                'operating_margin': r'operating\s+margin[:\s]*([\d,]+\.?\d*)%'
            }
            
            for margin_name, pattern in margin_patterns.items():
                match = re.search(pattern, transcript, re.IGNORECASE)
                if match:
                    metrics['margins'][margin_name] = float(match.group(1).replace(',', ''))
            
            # Extract ratios
            ratio_patterns = {
                'current_ratio': r'current\s+ratio[:\s]*([\d,]+\.?\d*)',
                'debt_to_equity': r'debt[:\s]*to[:\s]*equity[:\s]*([\d,]+\.?\d*)',
                'roe': r'return\s+on\s+equity[:\s]*([\d,]+\.?\d*)%'
            }
            
            for ratio_name, pattern in ratio_patterns.items():
                match = re.search(pattern, transcript, re.IGNORECASE)
                if match:
                    metrics['ratios'][ratio_name] = float(match.group(1).replace(',', ''))
            
        except Exception as e:
            self.logger.error(f"Error extracting key metrics: {str(e)}")
            metrics['error'] = str(e)
        
        return metrics
    
    def _convert_to_millions(self, value: float, unit: str) -> float:
        """Convert value to millions."""
        unit_lower = unit.lower()
        if unit_lower in ['billion', 'b']:
            return value * 1000
        elif unit_lower in ['thousand', 'k']:
            return value / 1000
        else:
            return value
    
    async def _analyze_speakers(self, transcript: str) -> Dict[str, Any]:
        """Analyze speakers in the transcript."""
        speaker_analysis = {
            'total_speakers': 0,
            'speaker_mentions': {},
            'speaker_sentiment': {},
            'key_speakers': []
        }
        
        try:
            # Identify speaker patterns
            speaker_patterns = [
                r'([A-Z][a-z]+\s+[A-Z][a-z]+):',  # Name: format
                r'([A-Z][a-z]+):',  # First name: format
                r'CEO:', r'CFO:', r'CTO:', r'President:', r'Chairman:'
            ]
            
            speakers = set()
            for pattern in speaker_patterns:
                matches = re.finditer(pattern, transcript)
                for match in matches:
                    speaker = match.group(1)
                    speakers.add(speaker)
            
            speaker_analysis['total_speakers'] = len(speakers)
            
            # Count speaker mentions
            for speaker in speakers:
                count = len(re.findall(rf'\b{speaker}\b', transcript, re.IGNORECASE))
                speaker_analysis['speaker_mentions'][speaker] = count
            
            # Analyze sentiment by speaker
            for speaker in speakers:
                # Extract text spoken by this speaker
                speaker_text = self._extract_speaker_text(transcript, speaker)
                if speaker_text:
                    sentiment = self._analyze_section_sentiment(speaker_text)
                    speaker_analysis['speaker_sentiment'][speaker] = sentiment
            
            # Identify key speakers (those with most mentions)
            sorted_speakers = sorted(
                speaker_analysis['speaker_mentions'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            speaker_analysis['key_speakers'] = sorted_speakers[:5]
        
        except Exception as e:
            self.logger.error(f"Error analyzing speakers: {str(e)}")
            speaker_analysis['error'] = str(e)
        
        return speaker_analysis
    
    def _extract_speaker_text(self, transcript: str, speaker: str) -> str:
        """Extract text spoken by a specific speaker."""
        pattern = rf'{speaker}:(.*?)(?=\n[A-Z][a-z]+:|$)'
        matches = re.findall(pattern, transcript, re.DOTALL | re.IGNORECASE)
        return ' '.join(matches)
    
    def _calculate_confidence_score(
        self, 
        transcript: str, 
        sentiment: Dict[str, Any], 
        financial_insights: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for the analysis."""
        confidence = 0.0
        
        try:
            # Base confidence on transcript length
            if len(transcript) > 1000:
                confidence += 0.3
            elif len(transcript) > 500:
                confidence += 0.2
            else:
                confidence += 0.1
            
            # Confidence based on financial insights
            if financial_insights.get('revenue_mentions'):
                confidence += 0.2
            if financial_insights.get('profit_mentions'):
                confidence += 0.2
            if financial_insights.get('growth_mentions'):
                confidence += 0.1
            
            # Confidence based on sentiment analysis
            if sentiment.get('sentiment_score') is not None:
                confidence += 0.1
            
            # Confidence based on forward-looking statements
            if financial_insights.get('forward_looking_statements'):
                confidence += 0.1
            
            # Cap confidence at 1.0
            confidence = min(confidence, 1.0)
        
        except Exception as e:
            self.logger.error(f"Error calculating confidence score: {str(e)}")
            confidence = 0.0
        
        return confidence
    
    async def connect_to_financial_data(
        self, 
        audio_analysis: Dict[str, Any], 
        financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Connect audio analysis to financial data."""
        
        connection = {
            'audio_analysis': audio_analysis,
            'financial_data': financial_data,
            'connections': {},
            'consistency_score': 0.0,
            'insights': []
        }
        
        try:
            # Connect revenue mentions to financial data
            if audio_analysis.get('key_metrics', {}).get('revenue') and financial_data.get('revenue'):
                audio_revenue = audio_analysis['key_metrics']['revenue']
                financial_revenue = financial_data['revenue']
                
                if abs(audio_revenue - financial_revenue) / financial_revenue < 0.1:  # Within 10%
                    connection['connections']['revenue'] = {
                        'audio_value': audio_revenue,
                        'financial_value': financial_revenue,
                        'consistency': 'high'
                    }
                    connection['consistency_score'] += 0.3
                else:
                    connection['connections']['revenue'] = {
                        'audio_value': audio_revenue,
                        'financial_value': financial_revenue,
                        'consistency': 'low'
                    }
            
            # Connect profit mentions to financial data
            if audio_analysis.get('key_metrics', {}).get('profit') and financial_data.get('net_income'):
                audio_profit = audio_analysis['key_metrics']['profit']
                financial_profit = financial_data['net_income']
                
                if abs(audio_profit - financial_profit) / financial_profit < 0.1:  # Within 10%
                    connection['connections']['profit'] = {
                        'audio_value': audio_profit,
                        'financial_value': financial_profit,
                        'consistency': 'high'
                    }
                    connection['consistency_score'] += 0.3
                else:
                    connection['connections']['profit'] = {
                        'audio_value': audio_profit,
                        'financial_value': financial_profit,
                        'consistency': 'low'
                    }
            
            # Generate insights based on connections
            if connection['consistency_score'] > 0.5:
                connection['insights'].append("Audio analysis is consistent with financial data")
            else:
                connection['insights'].append("Audio analysis shows discrepancies with financial data")
            
            # Add sentiment insights
            sentiment = audio_analysis.get('sentiment_analysis', {})
            if sentiment.get('overall_sentiment') == 'positive':
                connection['insights'].append("Positive sentiment in audio aligns with strong financial performance")
            elif sentiment.get('overall_sentiment') == 'negative':
                connection['insights'].append("Negative sentiment in audio may indicate financial challenges")
        
        except Exception as e:
            self.logger.error(f"Error connecting audio to financial data: {str(e)}")
            connection['error'] = str(e)
        
        return connection
