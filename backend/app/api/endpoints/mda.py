"""
MD&A (Management Discussion & Analysis) generation endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import json
import pandas as pd
from datetime import datetime

from app.database import get_db
from app.models import Document
from app.schemas import ChatQueryResponse
from app.services.md_a_generator import MDAGenerator
from app.services.financial_analyzer import FinancialAnalyzer
from app.services.document_processor import DocumentProcessor

router = APIRouter()


@router.post("/generate", response_model=Dict[str, Any])
async def generate_mda_report(
    document_id: Optional[int] = None,
    period: str = "Q3 2024",
    db: Session = Depends(get_db)
):
    """
    Generate a complete MD&A report from financial data.
    
    This endpoint:
    1. Extracts financial data from uploaded documents
    2. Computes KPIs and ratios
    3. Calculates YoY/QoQ changes
    4. Generates sectioned MD&A narrative
    5. Provides citations to source data
    """
    
    try:
        # Initialize services
        mda_generator = MDAGenerator()
        financial_analyzer = FinancialAnalyzer()
        
        # Get financial data
        if document_id:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            
            # Extract financial data from document
            financial_data = await _extract_financial_data_from_document(document)
        else:
            # Use sample data for demo
            financial_data = _get_sample_financial_data()
        
        # Prepare company info
        company_info = {
            "name": "Sample Corporation",
            "industry": "Technology",
            "period": period
        }
        
        # Generate MD&A draft
        result = await mda_generator.generate_md_a_draft(
            financial_data=financial_data,
            company_info=company_info,
            period=period
        )
        
        return {
            "success": result.get("success", False),
            "md_a_draft": result.get("md_a_draft", ""),
            "sections": result.get("sections", []),
            "key_metrics": result.get("key_metrics", []),
            "citations": result.get("citations", []),
            "confidence": result.get("confidence", 0.0),
            "generation_time": result.get("generation_time", 0.0),
            "period": period
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating MD&A: {str(e)}")


@router.post("/generate-section", response_model=Dict[str, Any])
async def generate_mda_section(
    section_type: str,
    document_id: Optional[int] = None,
    period: str = "Q3 2024",
    db: Session = Depends(get_db)
):
    """
    Generate a specific MD&A section.
    
    Section types:
    - executive_summary
    - results_of_operations
    - liquidity
    - risks
    """
    
    valid_sections = ["executive_summary", "results_of_operations", "liquidity", "risks"]
    if section_type not in valid_sections:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid section type. Must be one of: {', '.join(valid_sections)}"
        )
    
    try:
        # Initialize services
        mda_generator = MDAGenerator()
        
        # Get financial data
        if document_id:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            financial_data = await _extract_financial_data_from_document(document)
        else:
            financial_data = _get_sample_financial_data()
        
        company_info = {
            "name": "Sample Corporation",
            "industry": "Technology",
            "period": period
        }
        
        # Generate specific section
        from app.services.agent_system import AgentSystem
        agent_system = AgentSystem()
        
        section_result = await agent_system.generate_md_a_section(
            section_type=section_type,
            financial_data=financial_data,
            context=json.dumps(financial_data, indent=2)
        )
        
        return {
            "success": section_result.get("success", False),
            "section_type": section_type,
            "content": section_result.get("content", ""),
            "period": period
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating section: {str(e)}")


@router.post("/analyze-financials", response_model=Dict[str, Any])
async def analyze_financial_data(
    document_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Analyze financial data and compute KPIs.
    
    Returns:
    - Financial ratios (liquidity, profitability, leverage)
    - YoY/QoQ changes
    - Trend analysis
    - Key insights
    """
    
    try:
        financial_analyzer = FinancialAnalyzer()
        
        # Get financial data
        if document_id:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            financial_data = await _extract_financial_data_from_document(document)
        else:
            financial_data = _get_sample_financial_data()
        
        # Calculate ratios
        ratios = await financial_analyzer.calculate_ratios(financial_data)
        
        # Calculate trends
        trends = _calculate_trends(financial_data)
        
        return {
            "success": True,
            "ratios": ratios,
            "trends": trends,
            "key_metrics": _extract_key_metrics(financial_data),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing financials: {str(e)}")


async def _extract_financial_data_from_document(document: Document) -> Dict[str, Any]:
    """Extract financial data from a processed document."""
    # This would typically parse the document content
    # For now, return sample data
    return _get_sample_financial_data()


def _get_sample_financial_data() -> Dict[str, Any]:
    """Generate sample financial data for demonstration."""
    return {
        "revenue": [
            {"period": "Q1 2024", "value": 1200000},
            {"period": "Q2 2024", "value": 1350000},
            {"period": "Q3 2024", "value": 1500000}
        ],
        "net_income": [
            {"period": "Q1 2024", "value": 180000},
            {"period": "Q2 2024", "value": 210000},
            {"period": "Q3 2024", "value": 240000}
        ],
        "expenses": [
            {"period": "Q1 2024", "value": 900000},
            {"period": "Q2 2024", "value": 980000},
            {"period": "Q3 2024", "value": 1050000}
        ],
        "assets": [
            {"period": "Q1 2024", "value": 5000000},
            {"period": "Q2 2024", "value": 5200000},
            {"period": "Q3 2024", "value": 5500000}
        ],
        "liabilities": [
            {"period": "Q1 2024", "value": 2000000},
            {"period": "Q2 2024", "value": 2100000},
            {"period": "Q3 2024", "value": 2200000}
        ],
        "cash_flow": [
            {"period": "Q1 2024", "value": 300000},
            {"period": "Q2 2024", "value": 350000},
            {"period": "Q3 2024", "value": 400000}
        ]
    }


def _calculate_trends(financial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate financial trends."""
    trends = {}
    
    for metric, data in financial_data.items():
        if len(data) >= 2:
            current = data[-1]["value"]
            previous = data[-2]["value"]
            change = ((current - previous) / previous) * 100
            
            trends[metric] = {
                "current": current,
                "previous": previous,
                "change_percent": round(change, 2),
                "trend": "increasing" if change > 0 else "decreasing"
            }
    
    return trends


def _extract_key_metrics(financial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key financial metrics."""
    metrics = {}
    
    # Get latest values
    for metric, data in financial_data.items():
        if data:
            metrics[f"latest_{metric}"] = data[-1]["value"]
    
    # Calculate derived metrics
    if "revenue" in financial_data and "net_income" in financial_data:
        revenue = financial_data["revenue"][-1]["value"]
        net_income = financial_data["net_income"][-1]["value"]
        metrics["profit_margin"] = round((net_income / revenue) * 100, 2)
    
    if "assets" in financial_data and "liabilities" in financial_data:
        assets = financial_data["assets"][-1]["value"]
        liabilities = financial_data["liabilities"][-1]["value"]
        metrics["equity"] = assets - liabilities
        metrics["debt_to_equity"] = round(liabilities / (assets - liabilities), 2)
    
    return metrics



