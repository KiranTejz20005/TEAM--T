"""
Utility functions for FinMDA-Bot.
"""
import re
import json
import hashlib
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """Validate file type against allowed types."""
    file_extension = filename.split('.')[-1].lower()
    return file_extension in allowed_types


def validate_file_size(file_size: int, max_size_mb: int) -> bool:
    """Validate file size against maximum allowed size."""
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes


def extract_financial_numbers(text: str) -> List[Dict[str, Any]]:
    """Extract financial numbers from text with context."""
    # Pattern to match currency amounts
    currency_pattern = r'\$?([\d,]+\.?\d*)\s*(million|billion|thousand|k|m|b)?'
    
    matches = []
    for match in re.finditer(currency_pattern, text, re.IGNORECASE):
        value = match.group(1).replace(',', '')
        unit = match.group(2) or ''
        
        # Convert to numeric value
        numeric_value = float(value)
        if unit.lower() in ['k', 'thousand']:
            numeric_value *= 1000
        elif unit.lower() in ['m', 'million']:
            numeric_value *= 1000000
        elif unit.lower() in ['b', 'billion']:
            numeric_value *= 1000000000
        
        matches.append({
            'value': numeric_value,
            'original_text': match.group(0),
            'context': text[max(0, match.start()-50):match.end()+50]
        })
    
    return matches


def clean_financial_text(text: str) -> str:
    """Clean and normalize financial text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize currency symbols
    text = re.sub(r'USD\s*\$', '$', text)
    text = re.sub(r'\$\s*USD', '$', text)
    
    # Normalize percentage symbols
    text = re.sub(r'percent', '%', text)
    text = re.sub(r'per\s*cent', '%', text)
    
    # Remove special characters that might interfere with analysis
    text = re.sub(r'[^\w\s\$\%\.\,\-\(\)]', '', text)
    
    return text.strip()


def calculate_confidence_score(
    data_quality: float,
    calculation_accuracy: float,
    source_reliability: float
) -> float:
    """Calculate overall confidence score for analysis."""
    weights = {
        'data_quality': 0.4,
        'calculation_accuracy': 0.4,
        'source_reliability': 0.2
    }
    
    return (
        data_quality * weights['data_quality'] +
        calculation_accuracy * weights['calculation_accuracy'] +
        source_reliability * weights['source_reliability']
    )


def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format currency amount for display."""
    if abs(amount) >= 1_000_000_000:
        return f"${amount/1_000_000_000:.2f}B"
    elif abs(amount) >= 1_000_000:
        return f"${amount/1_000_000:.2f}M"
    elif abs(amount) >= 1_000:
        return f"${amount/1_000:.2f}K"
    else:
        return f"${amount:.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage for display."""
    return f"{value * 100:.{decimals}f}%"


def generate_document_hash(content: str) -> str:
    """Generate hash for document content."""
    return hashlib.md5(content.encode()).hexdigest()


def validate_financial_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate financial data for completeness and consistency."""
    validation_results = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'missing_fields': [],
        'inconsistent_data': []
    }
    
    required_fields = ['revenue', 'expenses', 'assets', 'liabilities']
    
    # Check for missing required fields
    for field in required_fields:
        if field not in data or data[field] is None:
            validation_results['missing_fields'].append(field)
            validation_results['is_valid'] = False
    
    # Check for negative values where they shouldn't be
    positive_fields = ['revenue', 'assets']
    for field in positive_fields:
        if field in data and data[field] < 0:
            validation_results['warnings'].append(f"{field} is negative")
    
    # Check for logical consistency
    if 'revenue' in data and 'expenses' in data:
        if data['expenses'] > data['revenue'] * 2:  # Expenses more than 2x revenue
            validation_results['warnings'].append("Expenses seem unusually high relative to revenue")
    
    return validation_results


def create_citation(source: str, page: Optional[int] = None, section: Optional[str] = None) -> Dict[str, Any]:
    """Create a citation object."""
    citation = {
        'source': source,
        'timestamp': datetime.utcnow().isoformat(),
        'type': 'document'
    }
    
    if page:
        citation['page'] = page
    
    if section:
        citation['section'] = section
    
    return citation


def merge_financial_data(data_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge financial data from multiple sources."""
    merged_data = {}
    
    for source in data_sources:
        for key, value in source.items():
            if key in merged_data:
                # Handle conflicts by taking the most recent or most reliable
                if isinstance(value, (int, float)) and isinstance(merged_data[key], (int, float)):
                    # Take the average for numeric values
                    merged_data[key] = (merged_data[key] + value) / 2
                else:
                    # Keep the first value for non-numeric
                    pass
            else:
                merged_data[key] = value
    
    return merged_data


def calculate_compound_annual_growth_rate(
    initial_value: float,
    final_value: float,
    periods: int
) -> float:
    """Calculate CAGR (Compound Annual Growth Rate)."""
    if initial_value <= 0 or final_value <= 0 or periods <= 0:
        return 0.0
    
    return (final_value / initial_value) ** (1 / periods) - 1


def calculate_present_value(
    future_value: float,
    discount_rate: float,
    periods: int
) -> float:
    """Calculate present value of future cash flow."""
    if discount_rate < 0 or periods < 0:
        return 0.0
    
    return future_value / ((1 + discount_rate) ** periods)


def calculate_net_present_value(
    cash_flows: List[float],
    discount_rate: float
) -> float:
    """Calculate Net Present Value of cash flows."""
    if not cash_flows or discount_rate < 0:
        return 0.0
    
    npv = 0
    for i, cash_flow in enumerate(cash_flows):
        npv += cash_flow / ((1 + discount_rate) ** i)
    
    return npv


def detect_financial_statement_type(text: str) -> str:
    """Detect the type of financial statement from text content."""
    text_lower = text.lower()
    
    # Income Statement indicators
    income_indicators = ['revenue', 'income', 'profit', 'loss', 'earnings', 'sales']
    income_score = sum(1 for indicator in income_indicators if indicator in text_lower)
    
    # Balance Sheet indicators
    balance_indicators = ['assets', 'liabilities', 'equity', 'balance sheet', 'stockholders']
    balance_score = sum(1 for indicator in balance_indicators if indicator in text_lower)
    
    # Cash Flow indicators
    cash_flow_indicators = ['cash flow', 'operating activities', 'investing activities', 'financing activities']
    cash_flow_score = sum(1 for indicator in cash_flow_indicators if indicator in text_lower)
    
    # Determine type based on highest score
    scores = {
        'income_statement': income_score,
        'balance_sheet': balance_score,
        'cash_flow_statement': cash_flow_score
    }
    
    return max(scores, key=scores.get) if max(scores.values()) > 0 else 'unknown'


def extract_time_periods(text: str) -> List[str]:
    """Extract time periods mentioned in financial text."""
    period_patterns = [
        r'(\d{4})',  # Years
        r'Q[1-4]\s*\d{4}',  # Quarters
        r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}',
        r'(\d{1,2}/\d{1,2}/\d{4})',  # Dates
        r'(year\s+ended|fiscal\s+year|annual)',
        r'(quarterly|monthly|weekly|daily)'
    ]
    
    periods = []
    for pattern in period_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        periods.extend(matches)
    
    return list(set(periods))  # Remove duplicates


def normalize_financial_terms(text: str) -> str:
    """Normalize financial terms for consistent analysis."""
    term_mappings = {
        'revenue': 'revenue',
        'sales': 'revenue',
        'income': 'revenue',
        'total revenue': 'revenue',
        'gross revenue': 'revenue',
        
        'expenses': 'expenses',
        'costs': 'expenses',
        'total expenses': 'expenses',
        'operating expenses': 'expenses',
        
        'profit': 'profit',
        'net income': 'profit',
        'earnings': 'profit',
        'net profit': 'profit',
        
        'assets': 'assets',
        'total assets': 'assets',
        'current assets': 'current_assets',
        'fixed assets': 'fixed_assets',
        
        'liabilities': 'liabilities',
        'total liabilities': 'liabilities',
        'current liabilities': 'current_liabilities',
        'long-term debt': 'long_term_debt'
    }
    
    normalized_text = text.lower()
    for original, normalized in term_mappings.items():
        normalized_text = normalized_text.replace(original, normalized)
    
    return normalized_text


def create_financial_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a summary of financial data."""
    summary = {
        'total_revenue': data.get('revenue', 0),
        'total_expenses': data.get('expenses', 0),
        'net_profit': data.get('profit', 0),
        'total_assets': data.get('assets', 0),
        'total_liabilities': data.get('liabilities', 0),
        'net_worth': data.get('assets', 0) - data.get('liabilities', 0),
        'profit_margin': (data.get('profit', 0) / data.get('revenue', 1)) if data.get('revenue', 0) > 0 else 0,
        'debt_to_asset_ratio': (data.get('liabilities', 0) / data.get('assets', 1)) if data.get('assets', 0) > 0 else 0
    }
    
    return summary
