"""
FAQ API endpoints.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
import logging

from app.services.faq_service import FAQService, FAQCategory
<<<<<<< HEAD
=======
from app.schemas import ChatRequest, ChatResponse
>>>>>>> 5c3a0a0f3539fc0d352cb6c8a94fa282129f33e9

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize FAQ service
faq_service = FAQService()


@router.get("/search")
async def search_faqs(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="FAQ category filter"),
    limit: int = Query(5, description="Maximum number of results")
) -> Dict[str, Any]:
    """Search FAQs based on query."""
    try:
        # Convert category string to enum if provided
        faq_category = None
        if category:
            try:
                faq_category = FAQCategory(category)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        
        # Search FAQs
        results = faq_service.search_faqs(
            query=query,
            category=faq_category,
            limit=limit
        )
        
        return {
            'query': query,
            'category': category,
            'results': results,
            'count': len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching FAQs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"FAQ search failed: {str(e)}")


@router.get("/{faq_id}")
async def get_faq(faq_id: str) -> Dict[str, Any]:
    """Get FAQ by ID."""
    try:
        faq = faq_service.get_faq_by_id(faq_id)
        if not faq:
            raise HTTPException(status_code=404, detail=f"FAQ not found: {faq_id}")
        
        return faq
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting FAQ {faq_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get FAQ: {str(e)}")


@router.get("/category/{category}")
async def get_faqs_by_category(category: str) -> Dict[str, Any]:
    """Get FAQs by category."""
    try:
        # Convert category string to enum
        try:
            faq_category = FAQCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        
        # Get FAQs by category
        results = faq_service.get_faqs_by_category(faq_category)
        
        return {
            'category': category,
            'faqs': results,
            'count': len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting FAQs by category {category}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get FAQs by category: {str(e)}")


@router.get("/")
async def get_all_faqs() -> Dict[str, Any]:
    """Get all FAQs."""
    try:
        all_faqs = []
        for faq in faq_service.faq_items.values():
            all_faqs.append({
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'category': faq.category.value,
                'difficulty': faq.difficulty
            })
        
        return {
            'faqs': all_faqs,
            'count': len(all_faqs)
        }
        
    except Exception as e:
        logger.error(f"Error getting all FAQs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get all FAQs: {str(e)}")


@router.get("/categories/list")
async def get_categories() -> Dict[str, Any]:
    """Get all FAQ categories."""
    try:
        categories = faq_service.get_all_categories()
        return {
            'categories': categories,
            'count': len(categories)
        }
        
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")


@router.get("/suggestions/questions")
async def get_suggested_questions(
    context: str = Query("", description="Context for suggestions")
) -> Dict[str, Any]:
    """Get suggested questions based on context."""
    try:
        suggestions = faq_service.get_suggested_questions(context)
        return {
            'context': context,
            'suggestions': suggestions,
            'count': len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"Error getting suggested questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get suggested questions: {str(e)}")


@router.post("/add")
async def add_faq(
    question: str,
    answer: str,
    category: str,
    keywords: List[str],
    related_questions: Optional[List[str]] = None,
    examples: Optional[List[str]] = None,
    difficulty: str = "beginner"
) -> Dict[str, Any]:
    """Add a new FAQ item."""
    try:
        # Convert category string to enum
        try:
            faq_category = FAQCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        
        # Add FAQ
        faq_id = faq_service.add_faq(
            question=question,
            answer=answer,
            category=faq_category,
            keywords=keywords,
            related_questions=related_questions,
            examples=examples,
            difficulty=difficulty
        )
        
        return {
            'id': faq_id,
            'message': 'FAQ added successfully',
            'status': 'success'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding FAQ: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add FAQ: {str(e)}")


@router.put("/{faq_id}")
async def update_faq(
    faq_id: str,
    question: Optional[str] = None,
    answer: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    related_questions: Optional[List[str]] = None,
    examples: Optional[List[str]] = None,
    difficulty: Optional[str] = None
) -> Dict[str, Any]:
    """Update an existing FAQ item."""
    try:
        # Update FAQ
        success = faq_service.update_faq(
            faq_id=faq_id,
            question=question,
            answer=answer,
            keywords=keywords,
            related_questions=related_questions,
            examples=examples,
            difficulty=difficulty
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"FAQ not found: {faq_id}")
        
        return {
            'id': faq_id,
            'message': 'FAQ updated successfully',
            'status': 'success'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating FAQ {faq_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update FAQ: {str(e)}")


@router.delete("/{faq_id}")
async def delete_faq(faq_id: str) -> Dict[str, Any]:
    """Delete an FAQ item."""
    try:
        # Delete FAQ
        success = faq_service.delete_faq(faq_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"FAQ not found: {faq_id}")
        
        return {
            'id': faq_id,
            'message': 'FAQ deleted successfully',
            'status': 'success'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting FAQ {faq_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete FAQ: {str(e)}")


@router.get("/export/json")
async def export_faqs() -> Dict[str, Any]:
    """Export all FAQs to JSON format."""
    try:
        export_data = faq_service.export_faqs()
        return export_data
        
    except Exception as e:
        logger.error(f"Error exporting FAQs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export FAQs: {str(e)}")


@router.post("/import/json")
async def import_faqs(faq_data: Dict[str, Any]) -> Dict[str, Any]:
    """Import FAQs from JSON format."""
    try:
        imported_count = faq_service.import_faqs(faq_data)
        return {
            'imported_count': imported_count,
            'message': f'Successfully imported {imported_count} FAQs',
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"Error importing FAQs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to import FAQs: {str(e)}")


@router.get("/help/quick-start")
async def get_quick_start_guide() -> Dict[str, Any]:
    """Get quick start guide for new users."""
    try:
        guide = {
            'title': 'FinMDA-Bot Quick Start Guide',
            'steps': [
                {
                    'step': 1,
                    'title': 'Upload Your Documents',
                    'description': 'Upload PDF, Excel, or CSV files containing your financial data',
                    'example': 'Upload your income statement or balance sheet'
                },
                {
                    'step': 2,
                    'title': 'Ask Questions',
                    'description': 'Use natural language to ask questions about your financial data',
                    'example': 'What is the profit margin trend?'
                },
                {
                    'step': 3,
                    'title': 'Get Insights',
                    'description': 'Receive detailed analysis, ratios, and forecasts',
                    'example': 'Show me the financial ratios and trends'
                },
                {
                    'step': 4,
                    'title': 'Use Voice Assistant',
                    'description': 'Speak your questions using the voice assistant feature',
                    'example': 'Click the microphone and ask: "What are the key financial metrics?"'
                }
            ],
            'common_questions': [
                'What is FinMDA-Bot?',
                'How do I upload documents?',
                'What financial ratios can you calculate?',
                'Can you predict future performance?',
                'How do I use the voice assistant?'
            ],
            'tips': [
                'Upload clear, high-quality documents for better results',
                'Ask specific questions for more accurate answers',
                'Use the voice assistant for hands-free analysis',
                'Check the FAQ section for common questions',
                'Explore different financial analysis features'
            ]
        }
        
        return guide
        
    except Exception as e:
        logger.error(f"Error getting quick start guide: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get quick start guide: {str(e)}")
