"""
Multi-agent system for financial analysis and conversation.
"""
from typing import Dict, Any, Optional, List
import google.generativeai as genai

from app.config import settings


class AgentSystem:
    """Lightweight agent that queries Gemini with optional context."""

    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        # Use a broadly supported model name for the Python client.
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    async def process_query(
        self,
        query: str,
        context: str = "",
        session_id: Optional[int] = None,
        document_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Return a structured response for the chat endpoint.

        Always returns a dict with keys: response, model_used, confidence_score, citations, tokens_used.
        """
        try:
            prompt = self._build_prompt(query, context)
            response = self.model.generate_content(prompt)
            text = getattr(response, "text", None) or "I couldn't generate a response."
            return {
                "response": text,
                "model_used": "gemini-1.5-flash",
                "confidence_score": 0.85 if text else 0.0,
                "citations": self._extract_citations(context),
                "tokens_used": len(text.split()) if text else 0,
            }
        except Exception as e:
            # Return a graceful error string instead of raising
            return {
                "response": f"I encountered an error processing your request: {str(e)}",
                "model_used": "gemini-1.5-flash",
                "confidence_score": 0.0,
                "citations": [],
                "tokens_used": 0,
            }

    def _build_prompt(self, query: str, context: str) -> str:
        system_instruction = (
            "You are FinMDA-Bot, an expert financial AI assistant. "
            "Provide clear, accurate, and professional responses. "
            "If information is insufficient, ask for clarification."
        )

        if context:
            return (
                f"{system_instruction}\n\n"
                f"Context from documents:\n{context}\n\n"
                f"User Question: {query}\n\n"
                f"Answer using only the provided context when possible."
            )
        return f"{system_instruction}\n\nUser Question: {query}"

    def _extract_citations(self, context: str) -> List[Dict[str, Any]]:
        if context:
            return [{"source": "document_context", "relevance_score": 0.9}]
        return []
