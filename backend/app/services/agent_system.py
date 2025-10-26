"""
Multi-agent system for financial analysis and conversation.
"""
from typing import Dict, Any, Optional, List
import google.generativeai as genai
import json
from datetime import datetime

from app.config import settings


class AgentSystem:
    """Lightweight agent that queries Gemini with optional context."""

    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

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
        """Build prompt for Gemini with system instructions and context."""
        system_instruction = (
            "You are FinMDA-Bot, an expert financial AI assistant specializing in:\n"
            "- Financial statement analysis\n"
            "- MD&A (Management Discussion & Analysis) generation\n"
            "- KPI calculation and interpretation\n"
            "- Financial ratio analysis\n"
            "- Trend identification and forecasting\n\n"
            "Provide clear, accurate, and professional responses. "
            "Always cite specific numbers when available. "
            "If information is insufficient, ask for clarification."
        )

        if context:
            return (
                f"{system_instruction}\n\n"
                f"Context from documents:\n{context}\n\n"
                f"User Question: {query}\n\n"
                f"Answer using only the provided context when possible. "
                f"Cite specific figures and provide clear explanations."
            )
        return f"{system_instruction}\n\nUser Question: {query}"

    def _extract_citations(self, context: str) -> List[Dict[str, Any]]:
        """Extract citations from context."""
        if context:
            return [{"source": "document_context", "relevance_score": 0.9}]
        return []
    
    async def generate_md_a_section(
        self,
        section_type: str,
        financial_data: Dict[str, Any],
        context: str = ""
    ) -> Dict[str, Any]:
        """Generate a specific MD&A section."""
        
        prompts = {
            "executive_summary": (
                "Generate an executive summary for the MD&A report based on the following financial data:\n"
                f"{json.dumps(financial_data, indent=2)}\n\n"
                "Include: Overall performance, key drivers, major challenges, strategic outlook.\n"
                "Keep it concise (2-3 paragraphs) and professional."
            ),
            "results_of_operations": (
                "Generate a 'Results of Operations' section based on:\n"
                f"{json.dumps(financial_data, indent=2)}\n\n"
                "Focus on: Revenue analysis, cost structure, profitability trends, operational performance.\n"
                "Provide specific numbers and percentages."
            ),
            "liquidity": (
                "Generate a 'Liquidity and Capital Resources' section based on:\n"
                f"{json.dumps(financial_data, indent=2)}\n\n"
                "Cover: Liquidity position, cash generation, debt levels, capital allocation."
            ),
            "risks": (
                "Generate a 'Risk Factors' section based on:\n"
                f"{json.dumps(financial_data, indent=2)}\n\n"
                "Identify: Financial risks, operational risks, regulatory risks, market risks."
            )
        }
        
        prompt = prompts.get(section_type, prompts["executive_summary"])
        
        try:
            response = self.model.generate_content(prompt)
            text = getattr(response, "text", "")
            
            return {
                "section_type": section_type,
                "content": text,
                "success": True
            }
        except Exception as e:
            return {
                "section_type": section_type,
                "content": f"Error generating section: {str(e)}",
                "success": False
            }
