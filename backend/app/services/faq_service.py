"""
FAQ service for common financial questions and answers.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json
import re
from dataclasses import dataclass
from enum import Enum

from app.config import settings


class FAQCategory(Enum):
    """FAQ categories."""
    GENERAL = "general"
    FINANCIAL_RATIOS = "financial_ratios"
    DOCUMENT_PROCESSING = "document_processing"
    INVESTMENT = "investment"
    PERSONAL_FINANCE = "personal_finance"
    CORPORATE_FINANCE = "corporate_finance"
    TECHNICAL = "technical"


@dataclass
class FAQItem:
    """FAQ item structure."""
    id: str
    question: str
    answer: str
    category: FAQCategory
    keywords: List[str]
    related_questions: List[str]
    examples: List[str]
    difficulty: str  # beginner, intermediate, advanced
    last_updated: datetime


class FAQService:
    """FAQ service for managing common questions and answers."""
    
    def __init__(self):
        """Initialize FAQ service."""
        self.logger = logging.getLogger(__name__)
        self.faq_items: Dict[str, FAQItem] = {}
        self._initialize_default_faqs()
    
    def _initialize_default_faqs(self):
        """Initialize with default FAQ items."""
        default_faqs = [
            FAQItem(
                id="what_is_finmda_bot",
                question="What is FinMDA-Bot?",
                answer="FinMDA-Bot is an AI-powered financial assistant that helps you analyze financial documents, calculate ratios, and get insights from your financial data. It can process PDFs, Excel files, and CSV files to extract financial information and answer your questions.",
                category=FAQCategory.GENERAL,
                keywords=["what", "is", "finmda", "bot", "assistant", "ai"],
                related_questions=["how_does_finmda_work", "what_can_finmda_do"],
                examples=["What is FinMDA-Bot?", "Tell me about this AI assistant"],
                difficulty="beginner",
                last_updated=datetime.utcnow()
            ),
            FAQItem(
                id="how_to_upload_documents",
                question="How do I upload financial documents?",
                answer="You can upload financial documents by clicking the 'Upload' button and selecting PDF, Excel (.xlsx), or CSV files. Supported documents include income statements, balance sheets, cash flow statements, and other financial reports. The system will automatically extract and analyze the data.",
                category=FAQCategory.DOCUMENT_PROCESSING,
                keywords=["upload", "documents", "files", "pdf", "excel", "csv"],
                related_questions=["what_documents_supported", "file_size_limits"],
                examples=["How do I upload my financial statements?", "Can I upload Excel files?"],
                difficulty="beginner",
                last_updated=datetime.utcnow()
            ),
            FAQItem(
                id="what_financial_ratios",
                question="What financial ratios can FinMDA-Bot calculate?",
                answer="FinMDA-Bot can calculate various financial ratios including liquidity ratios (current ratio, quick ratio), profitability ratios (gross margin, net margin, ROE, ROA), leverage ratios (debt-to-equity, interest coverage), efficiency ratios (asset turnover, inventory turnover), and valuation ratios (P/E, P/B, EV/EBITDA).",
                category=FAQCategory.FINANCIAL_RATIOS,
                keywords=["ratios", "calculate", "liquidity", "profitability", "leverage", "efficiency"],
                related_questions=["how_to_calculate_ratios", "ratio_interpretation"],
                examples=["What ratios can you calculate?", "Show me profitability ratios"],
                difficulty="intermediate",
                last_updated=datetime.utcnow()
            ),
            FAQItem(
                id="how_to_ask_questions",
                question="How do I ask questions about my financial data?",
                answer="You can ask questions in natural language using the chat interface. For example: 'What's the profit margin trend?', 'Show me the cash flow analysis', 'Compare this quarter to last quarter', or 'What are the key financial metrics?'. The AI will analyze your documents and provide detailed answers.",
                category=FAQCategory.GENERAL,
                keywords=["ask", "questions", "chat", "query", "natural", "language"],
                related_questions=["example_questions", "chat_interface"],
                examples=["How do I ask about my revenue?", "Can I chat with the AI?"],
                difficulty="beginner",
                last_updated=datetime.utcnow()
            ),
            FAQItem(
                id="voice_assistant_usage",
                question="How do I use the voice assistant?",
                answer="The voice assistant allows you to speak your questions instead of typing. Click the microphone button, speak your question clearly, and the system will convert your speech to text, process your query, and provide both text and voice responses. This is especially useful for hands-free financial analysis.",
                category=FAQCategory.TECHNICAL,
                keywords=["voice", "assistant", "speech", "microphone", "audio"],
                related_questions=["voice_commands", "speech_recognition"],
                examples=["How do I use voice commands?", "Can I speak to the AI?"],
                difficulty="beginner",
                last_updated=datetime.utcnow()
            ),
            FAQItem(
                id="data_privacy_security",
                question="Is my financial data secure and private?",
                answer="Yes, FinMDA-Bot prioritizes data privacy and security. Your documents are processed locally when possible, and sensitive data is encrypted. We don't store your financial information permanently, and you can delete your data at any time. All communications are secured with industry-standard encryption.",
                category=FAQCategory.TECHNICAL,
                keywords=["privacy", "security", "data", "encryption", "safe"],
                related_questions=["data_storage", "encryption_details"],
                examples=["Is my data safe?", "How is privacy protected?"],
                difficulty="beginner",
                last_updated=datetime.utcnow()
            ),
            FAQItem(
                id="forecasting_capabilities",
                question="Can FinMDA-Bot predict future financial performance?",
                answer="Yes, FinMDA-Bot can generate financial forecasts using advanced machine learning models. It analyzes historical trends and patterns to predict future revenue, expenses, and key financial metrics. However, all forecasts should be used as guidance and not as absolute predictions, as they depend on historical data and assumptions.",
                category=FAQCategory.FINANCIAL_RATIOS,
                keywords=["forecast", "prediction", "future", "trends", "machine", "learning"],
                related_questions=["forecast_accuracy", "trend_analysis"],
                examples=["Can you predict my revenue?", "Show me future trends"],
                difficulty="advanced",
                last_updated=datetime.utcnow()
            ),
            FAQItem(
                id="supported_file_formats",
                question="What file formats are supported?",
                answer="FinMDA-Bot supports PDF files (including scanned documents), Excel files (.xlsx, .xls), CSV files, and Word documents (.docx). For PDFs, it can extract both text and tables. For Excel and CSV files, it can process multiple sheets and complex data structures.",
                category=FAQCategory.DOCUMENT_PROCESSING,
                keywords=["formats", "files", "pdf", "excel", "csv", "word"],
                related_questions=["file_size_limits", "scanning_documents"],
                examples=["What files can I upload?", "Do you support Excel?"],
                difficulty="beginner",
                last_updated=datetime.utcnow()
            ),
            FAQItem(
                id="investment_analysis",
                question="Can FinMDA-Bot help with investment analysis?",
                answer="Yes, FinMDA-Bot can assist with investment analysis by calculating key investment ratios (P/E, P/B, ROE, ROA), analyzing company financial health, comparing performance metrics, and providing insights on investment opportunities. It can also analyze portfolio performance and risk metrics.",
                category=FAQCategory.INVESTMENT,
                keywords=["investment", "analysis", "portfolio", "ratios", "performance"],
                related_questions=["portfolio_analysis", "investment_ratios"],
                examples=["Can you analyze my investments?", "Show investment metrics"],
                difficulty="intermediate",
                last_updated=datetime.utcnow()
            ),
            FAQItem(
                id="personal_finance_features",
                question="What personal finance features are available?",
                answer="FinMDA-Bot can help with personal finance by analyzing your income and expenses, calculating savings rates, tracking spending patterns, creating budgets, and providing financial health scores. It can process bank statements, credit card statements, and other personal financial documents.",
                category=FAQCategory.PERSONAL_FINANCE,
                keywords=["personal", "finance", "budget", "expenses", "savings"],
                related_questions=["budget_analysis", "expense_tracking"],
                examples=["Can you help with my budget?", "Analyze my expenses"],
                difficulty="beginner",
                last_updated=datetime.utcnow()
            )
        ]
        
        for faq in default_faqs:
            self.faq_items[faq.id] = faq
    
    def search_faqs(
        self, 
        query: str, 
        category: Optional[FAQCategory] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search FAQs based on query."""
        results = []
        query_lower = query.lower()
        
        for faq in self.faq_items.values():
            if category and faq.category != category:
                continue
            
            # Calculate relevance score
            score = 0
            
            # Check question match
            if query_lower in faq.question.lower():
                score += 3
            
            # Check answer match
            if query_lower in faq.answer.lower():
                score += 2
            
            # Check keyword matches
            keyword_matches = sum(1 for keyword in faq.keywords if keyword in query_lower)
            score += keyword_matches * 0.5
            
            # Check related questions
            for related in faq.related_questions:
                if query_lower in related.lower():
                    score += 1
            
            if score > 0:
                results.append({
                    'id': faq.id,
                    'question': faq.question,
                    'answer': faq.answer,
                    'category': faq.category.value,
                    'score': score,
                    'difficulty': faq.difficulty,
                    'examples': faq.examples
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def get_faq_by_id(self, faq_id: str) -> Optional[Dict[str, Any]]:
        """Get FAQ by ID."""
        if faq_id in self.faq_items:
            faq = self.faq_items[faq_id]
            return {
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'category': faq.category.value,
                'keywords': faq.keywords,
                'related_questions': faq.related_questions,
                'examples': faq.examples,
                'difficulty': faq.difficulty,
                'last_updated': faq.last_updated.isoformat()
            }
        return None
    
    def get_faqs_by_category(self, category: FAQCategory) -> List[Dict[str, Any]]:
        """Get FAQs by category."""
        results = []
        for faq in self.faq_items.values():
            if faq.category == category:
                results.append({
                    'id': faq.id,
                    'question': faq.question,
                    'answer': faq.answer,
                    'category': faq.category.value,
                    'difficulty': faq.difficulty
                })
        return results
    
    def get_all_categories(self) -> List[Dict[str, str]]:
        """Get all FAQ categories."""
        return [
            {'value': cat.value, 'name': cat.value.replace('_', ' ').title()}
            for cat in FAQCategory
        ]
    
    def add_faq(
        self,
        question: str,
        answer: str,
        category: FAQCategory,
        keywords: List[str],
        related_questions: List[str] = None,
        examples: List[str] = None,
        difficulty: str = "beginner"
    ) -> str:
        """Add a new FAQ item."""
        faq_id = self._generate_faq_id(question)
        
        faq = FAQItem(
            id=faq_id,
            question=question,
            answer=answer,
            category=category,
            keywords=keywords,
            related_questions=related_questions or [],
            examples=examples or [],
            difficulty=difficulty,
            last_updated=datetime.utcnow()
        )
        
        self.faq_items[faq_id] = faq
        return faq_id
    
    def update_faq(
        self,
        faq_id: str,
        question: str = None,
        answer: str = None,
        keywords: List[str] = None,
        related_questions: List[str] = None,
        examples: List[str] = None,
        difficulty: str = None
    ) -> bool:
        """Update an existing FAQ item."""
        if faq_id not in self.faq_items:
            return False
        
        faq = self.faq_items[faq_id]
        
        if question is not None:
            faq.question = question
        if answer is not None:
            faq.answer = answer
        if keywords is not None:
            faq.keywords = keywords
        if related_questions is not None:
            faq.related_questions = related_questions
        if examples is not None:
            faq.examples = examples
        if difficulty is not None:
            faq.difficulty = difficulty
        
        faq.last_updated = datetime.utcnow()
        return True
    
    def delete_faq(self, faq_id: str) -> bool:
        """Delete an FAQ item."""
        if faq_id in self.faq_items:
            del self.faq_items[faq_id]
            return True
        return False
    
    def get_suggested_questions(self, context: str = "") -> List[str]:
        """Get suggested questions based on context."""
        suggestions = []
        
        if "ratio" in context.lower() or "financial" in context.lower():
            suggestions.extend([
                "What financial ratios can you calculate?",
                "Show me the current ratio",
                "Calculate the debt-to-equity ratio"
            ])
        
        if "upload" in context.lower() or "document" in context.lower():
            suggestions.extend([
                "How do I upload documents?",
                "What file formats are supported?",
                "Can I upload Excel files?"
            ])
        
        if "voice" in context.lower() or "speech" in context.lower():
            suggestions.extend([
                "How do I use the voice assistant?",
                "Can I speak my questions?",
                "What voice commands are available?"
            ])
        
        if "forecast" in context.lower() or "prediction" in context.lower():
            suggestions.extend([
                "Can you predict future performance?",
                "Show me revenue forecasts",
                "What are the trend predictions?"
            ])
        
        # Add general suggestions if no specific context
        if not suggestions:
            suggestions = [
                "What is FinMDA-Bot?",
                "How do I upload my financial documents?",
                "What financial ratios can you calculate?",
                "Can you help with investment analysis?",
                "How do I use the voice assistant?"
            ]
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _generate_faq_id(self, question: str) -> str:
        """Generate a unique FAQ ID from question."""
        # Convert question to lowercase, replace spaces with underscores, remove special chars
        faq_id = re.sub(r'[^a-z0-9\s]', '', question.lower())
        faq_id = re.sub(r'\s+', '_', faq_id)
        faq_id = faq_id[:50]  # Limit length
        
        # Ensure uniqueness
        original_id = faq_id
        counter = 1
        while faq_id in self.faq_items:
            faq_id = f"{original_id}_{counter}"
            counter += 1
        
        return faq_id
    
    def export_faqs(self) -> Dict[str, Any]:
        """Export all FAQs to JSON format."""
        return {
            'faqs': [
                {
                    'id': faq.id,
                    'question': faq.question,
                    'answer': faq.answer,
                    'category': faq.category.value,
                    'keywords': faq.keywords,
                    'related_questions': faq.related_questions,
                    'examples': faq.examples,
                    'difficulty': faq.difficulty,
                    'last_updated': faq.last_updated.isoformat()
                }
                for faq in self.faq_items.values()
            ],
            'categories': [cat.value for cat in FAQCategory],
            'total_count': len(self.faq_items),
            'exported_at': datetime.utcnow().isoformat()
        }
    
    def import_faqs(self, faq_data: Dict[str, Any]) -> int:
        """Import FAQs from JSON format."""
        imported_count = 0
        
        for faq_dict in faq_data.get('faqs', []):
            try:
                category = FAQCategory(faq_dict['category'])
                faq = FAQItem(
                    id=faq_dict['id'],
                    question=faq_dict['question'],
                    answer=faq_dict['answer'],
                    category=category,
                    keywords=faq_dict.get('keywords', []),
                    related_questions=faq_dict.get('related_questions', []),
                    examples=faq_dict.get('examples', []),
                    difficulty=faq_dict.get('difficulty', 'beginner'),
                    last_updated=datetime.fromisoformat(faq_dict.get('last_updated', datetime.utcnow().isoformat()))
                )
                
                self.faq_items[faq.id] = faq
                imported_count += 1
                
            except Exception as e:
                self.logger.error(f"Error importing FAQ {faq_dict.get('id', 'unknown')}: {str(e)}")
        
        return imported_count
