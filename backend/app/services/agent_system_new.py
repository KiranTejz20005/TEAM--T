"""
Multi-agent system for financial analysis and conversation.
"""
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
import google.generativeai as genai

from app.config import settings


class AgentSystem:
    """Multi-agent system for financial analysis."""
    
    def __init__(self):
        """Initialize the agent system."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def process_query(
        self,
        query: str,
        context: str = "",
        session_id: Optional[int] = None,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Process a user query through the multi-agent system."""
        
        try:
            # Build the prompt with context
            prompt = self._build_prompt(query, context)
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            
            return {
                "response": response.text,
                "model_used": "gemini-pro",
                "confidence_score": 0.85,
                "citations": self._extract_citations(context),
                "tokens_used": len(response.text.split())
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question.",
                "model_used": "gemini-pro",
                "confidence_score": 0.0,
                "citations": [],
                "tokens_used": 0
            }
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Build a comprehensive prompt for the LLM."""
        
        system_instruction = """You are FinMDA-Bot, an expert financial AI assistant specializing in:
- Financial document analysis
- Financial ratio calculations
- Trend analysis and forecasting
- MD&A (Management Discussion & Analysis) generation
- Financial data interpretation

Provide clear, accurate, and professional responses. When analyzing financial data:
1. Always cite specific numbers and sources
2. Explain financial concepts clearly
3. Provide actionable insights
4. Use proper financial terminology

If you don't have enough information to answer accurately, ask for clarification."""
        
        if context:
            full_prompt = f"""{system_instruction}

Context from documents:
{context}

User Question: {query}

Please provide a comprehensive answer based on the context above."""
        else:
            full_prompt = f"""{system_instruction}

User Question: {query}

Please provide a helpful response."""
        
        return full_prompt
    
    def _extract_citations(self, context: str) -> List[Dict[str, Any]]:
        """Extract citation information from context."""
        citations = []
        if context:
            # Simple citation extraction - can be enhanced
            citations.append({
                "source": "Document Context",
                "relevance_score": 0.9
            })
        return citations
