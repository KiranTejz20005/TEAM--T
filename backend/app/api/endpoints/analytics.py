"""
Financial analytics endpoints for FinMDA-Bot.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Document, FinancialAnalysis
from app.schemas import (
    FinancialRatioRequest, FinancialRatioResponse,
    ForecastRequest, ForecastResponse,
    TrendAnalysisRequest, TrendAnalysisResponse
)
from app.services.financial_analyzer import FinancialAnalyzer

router = APIRouter()


@router.post("/ratios", response_model=FinancialRatioResponse)
async def calculate_financial_ratios(
    request: FinancialRatioRequest,
    db: Session = Depends(get_db)
):
    """Calculate financial ratios for a document."""
    
    # Verify document exists and is processed
    document = db.query(Document).filter(Document.id == request.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not document.is_processed:
        raise HTTPException(status_code=400, detail="Document not yet processed")
    
    try:
        # Initialize financial analyzer
        analyzer = FinancialAnalyzer()
        
        # Calculate requested ratios
        ratios = await analyzer.calculate_ratios(
            document_id=request.document_id,
            ratio_types=request.ratio_types,
            period=request.period
        )
        
        # Save analysis results
        analysis = FinancialAnalysis(
            document_id=request.document_id,
            analysis_type="ratios",
            results=ratios,
            model_version="1.0",
            confidence_score=ratios.get("confidence_score", 0.95)
        )
        db.add(analysis)
        db.commit()
        
        return FinancialRatioResponse(
            document_id=request.document_id,
            ratios=ratios,
            calculation_date=datetime.utcnow(),
            confidence_score=ratios.get("confidence_score")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating ratios: {str(e)}")


@router.post("/forecast", response_model=ForecastResponse)
async def generate_forecast(
    request: ForecastRequest,
    db: Session = Depends(get_db)
):
    """Generate financial forecasts for a document."""
    
    # Verify document exists and is processed
    document = db.query(Document).filter(Document.id == request.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not document.is_processed:
        raise HTTPException(status_code=400, detail="Document not yet processed")
    
    try:
        # Initialize financial analyzer
        analyzer = FinancialAnalyzer()
        
        # Generate forecast
        forecast_data = await analyzer.generate_forecast(
            document_id=request.document_id,
            metric=request.metric,
            periods=request.periods,
            method=request.method
        )
        
        # Save analysis results
        analysis = FinancialAnalysis(
            document_id=request.document_id,
            analysis_type="forecast",
            results=forecast_data,
            model_version="1.0",
            confidence_score=forecast_data.get("confidence_score", 0.85)
        )
        db.add(analysis)
        db.commit()
        
        return ForecastResponse(
            document_id=request.document_id,
            metric=request.metric,
            forecast_data=forecast_data["forecast_data"],
            confidence_intervals=forecast_data["confidence_intervals"],
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")


@router.post("/trends", response_model=TrendAnalysisResponse)
async def analyze_trends(
    request: TrendAnalysisRequest,
    db: Session = Depends(get_db)
):
    """Analyze trends in financial data."""
    
    # Verify document exists and is processed
    document = db.query(Document).filter(Document.id == request.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not document.is_processed:
        raise HTTPException(status_code=400, detail="Document not yet processed")
    
    try:
        # Initialize financial analyzer
        analyzer = FinancialAnalyzer()
        
        # Analyze trends
        trends = await analyzer.analyze_trends(
            document_id=request.document_id,
            metrics=request.metrics,
            time_period=request.time_period
        )
        
        # Save analysis results
        analysis = FinancialAnalysis(
            document_id=request.document_id,
            analysis_type="trends",
            results=trends,
            model_version="1.0",
            confidence_score=trends.get("confidence_score", 0.90)
        )
        db.add(analysis)
        db.commit()
        
        return TrendAnalysisResponse(
            document_id=request.document_id,
            trends=trends["trends"],
            analysis_date=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing trends: {str(e)}")


@router.get("/{document_id}/analyses", response_model=List[dict])
async def get_document_analyses(
    document_id: int,
    analysis_type: str = None,
    db: Session = Depends(get_db)
):
    """Get all analyses performed on a document."""
    
    # Verify document exists
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Query analyses
    query = db.query(FinancialAnalysis).filter(FinancialAnalysis.document_id == document_id)
    
    if analysis_type:
        query = query.filter(FinancialAnalysis.analysis_type == analysis_type)
    
    analyses = query.order_by(FinancialAnalysis.created_at.desc()).all()
    
    return [
        {
            "id": analysis.id,
            "analysis_type": analysis.analysis_type,
            "results": analysis.results,
            "created_at": analysis.created_at,
            "confidence_score": analysis.confidence_score,
            "validation_status": analysis.validation_status
        }
        for analysis in analyses
    ]
