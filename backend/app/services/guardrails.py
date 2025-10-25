"""
Guardrails service for input/output validation and safety.
"""
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

from app.config import settings


class GuardrailsService:
    """Service for implementing guardrails and safety measures."""
    
    def __init__(self):
        """Initialize guardrails service."""
        self.logger = logging.getLogger(__name__)
        
        # Financial domain keywords for relevance checking
        self.financial_keywords = [
            'revenue', 'profit', 'loss', 'income', 'expense', 'asset', 'liability',
            'debt', 'equity', 'cash', 'flow', 'ratio', 'margin', 'return',
            'investment', 'portfolio', 'valuation', 'forecast', 'budget',
            'financial', 'accounting', 'audit', 'compliance', 'risk'
        ]
        
        # Potentially sensitive patterns
        self.sensitive_patterns = [
            r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # Credit card numbers
            r'\b\d{3}-\d{2}-\d{4}\b',       # SSN patterns
            r'\b[A-Z]{2}\d{6}\b',            # Account numbers
            r'\b\d{9,}\b'                    # Long numeric sequences
        ]
    
    async def validate_input(self, input_data: Any, input_type: str) -> Dict[str, Any]:
        """Validate input data for safety and relevance."""
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'confidence_score': 1.0
        }
        
        try:
            # File upload validation
            if input_type == 'file_upload':
                validation_result = await self._validate_file_upload(input_data)
            
            # Chat query validation
            elif input_type == 'chat_query':
                validation_result = await self._validate_chat_query(input_data)
            
            # Financial data validation
            elif input_type == 'financial_data':
                validation_result = await self._validate_financial_data(input_data)
            
            # API request validation
            elif input_type == 'api_request':
                validation_result = await self._validate_api_request(input_data)
            
            else:
                validation_result['errors'].append(f"Unknown input type: {input_type}")
                validation_result['is_valid'] = False
        
        except Exception as e:
            validation_result['errors'].append(f"Validation error: {str(e)}")
            validation_result['is_valid'] = False
            validation_result['confidence_score'] = 0.0
        
        return validation_result
    
    async def _validate_file_upload(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate file upload data."""
        result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'confidence_score': 1.0
        }
        
        # Check file type
        if 'file_type' not in file_data:
            result['errors'].append("File type not specified")
            result['is_valid'] = False
        elif file_data['file_type'] not in settings.allowed_file_types:
            result['errors'].append(f"File type {file_data['file_type']} not allowed")
            result['is_valid'] = False
        
        # Check file size
        if 'file_size' in file_data:
            max_size = settings.max_file_size_mb * 1024 * 1024
            if file_data['file_size'] > max_size:
                result['errors'].append(f"File size exceeds limit of {settings.max_file_size_mb}MB")
                result['is_valid'] = False
        
        # Check for suspicious content
        if 'filename' in file_data:
            if self._contains_suspicious_patterns(file_data['filename']):
                result['warnings'].append("Filename contains suspicious patterns")
                result['confidence_score'] *= 0.8
        
        return result
    
    async def _validate_chat_query(self, query: str) -> Dict[str, Any]:
        """Validate chat query for relevance and safety."""
        result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'confidence_score': 1.0
        }
        
        # Check query length
        if len(query) > 1000:
            result['warnings'].append("Query is very long, may impact performance")
            result['confidence_score'] *= 0.9
        
        # Check for financial relevance
        if not self._is_financially_relevant(query):
            result['warnings'].append("Query may not be financially relevant")
            result['confidence_score'] *= 0.7
        
        # Check for sensitive information
        if self._contains_sensitive_patterns(query):
            result['errors'].append("Query contains potentially sensitive information")
            result['is_valid'] = False
            result['confidence_score'] = 0.0
        
        # Check for malicious content
        if self._contains_malicious_content(query):
            result['errors'].append("Query contains potentially malicious content")
            result['is_valid'] = False
            result['confidence_score'] = 0.0
        
        return result
    
    async def _validate_financial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate financial data for accuracy and consistency."""
        result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'confidence_score': 1.0
        }
        
        # Check for required fields
        required_fields = ['revenue', 'expenses', 'assets']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            result['warnings'].append(f"Missing recommended fields: {missing_fields}")
            result['confidence_score'] *= 0.8
        
        # Check for data consistency
        if 'revenue' in data and 'expenses' in data:
            if data['expenses'] > data['revenue'] * 3:  # Expenses > 3x revenue
                result['warnings'].append("Expenses seem unusually high relative to revenue")
                result['confidence_score'] *= 0.7
        
        # Check for negative values where they shouldn't be
        positive_fields = ['revenue', 'assets']
        for field in positive_fields:
            if field in data and data[field] < 0:
                result['warnings'].append(f"{field} is negative, which may indicate data error")
                result['confidence_score'] *= 0.6
        
        return result
    
    async def _validate_api_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate API request data."""
        result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'confidence_score': 1.0
        }
        
        # Check for required fields
        if 'endpoint' not in request_data:
            result['errors'].append("API endpoint not specified")
            result['is_valid'] = False
        
        # Check for rate limiting
        if 'user_id' in request_data:
            # This would integrate with rate limiting service
            pass
        
        return result
    
    async def validate_output(self, output: str, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate AI output for accuracy and safety."""
        result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'confidence_score': 1.0,
            'hallucination_risk': 0.0
        }
        
        try:
            # Check for hallucination indicators
            hallucination_risk = await self._assess_hallucination_risk(output, source_data)
            result['hallucination_risk'] = hallucination_risk
            
            if hallucination_risk > 0.7:
                result['warnings'].append("High risk of hallucination detected")
                result['confidence_score'] *= 0.5
            
            # Check for factual consistency
            if not await self._check_factual_consistency(output, source_data):
                result['warnings'].append("Output may contain factual inconsistencies")
                result['confidence_score'] *= 0.7
            
            # Check for appropriate disclaimers
            if not self._has_appropriate_disclaimers(output):
                result['warnings'].append("Output lacks appropriate disclaimers")
                result['confidence_score'] *= 0.9
            
            # Check for sensitive information leakage
            if self._contains_sensitive_patterns(output):
                result['errors'].append("Output contains potentially sensitive information")
                result['is_valid'] = False
                result['confidence_score'] = 0.0
        
        except Exception as e:
            result['errors'].append(f"Output validation error: {str(e)}")
            result['is_valid'] = False
            result['confidence_score'] = 0.0
        
        return result
    
    async def _assess_hallucination_risk(self, output: str, source_data: Dict[str, Any]) -> float:
        """Assess risk of hallucination in AI output."""
        risk_score = 0.0
        
        # Check for specific financial claims without citations
        specific_claims = re.findall(r'\b\d+(?:\.\d+)?%?\b', output)
        if len(specific_claims) > 3 and 'source' not in output.lower():
            risk_score += 0.3
        
        # Check for definitive statements without qualifiers
        definitive_patterns = [
            r'\b(?:always|never|all|none|every|definitely|certainly)\b',
            r'\b(?:guaranteed|assured|promised)\b'
        ]
        
        for pattern in definitive_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                risk_score += 0.2
        
        # Check for claims about future performance
        future_claims = re.findall(r'\b(?:will|shall|going to)\b', output)
        if len(future_claims) > 2:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    async def _check_factual_consistency(self, output: str, source_data: Dict[str, Any]) -> bool:
        """Check if output is factually consistent with source data."""
        # Extract numbers from output
        output_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', output)
        
        # Extract numbers from source data
        source_numbers = []
        for value in source_data.values():
            if isinstance(value, (int, float)):
                source_numbers.append(str(value))
            elif isinstance(value, str):
                numbers = re.findall(r'\b\d+(?:\.\d+)?\b', value)
                source_numbers.extend(numbers)
        
        # Check for major discrepancies
        if output_numbers and source_numbers:
            # Simple consistency check - can be enhanced
            return True  # Placeholder for more sophisticated checking
        
        return True
    
    def _has_appropriate_disclaimers(self, output: str) -> bool:
        """Check if output has appropriate disclaimers."""
        disclaimer_indicators = [
            'disclaimer', 'note', 'important', 'caution', 'warning',
            'based on', 'according to', 'as shown in', 'refer to'
        ]
        
        output_lower = output.lower()
        return any(indicator in output_lower for indicator in disclaimer_indicators)
    
    def _is_financially_relevant(self, text: str) -> bool:
        """Check if text is financially relevant."""
        text_lower = text.lower()
        financial_score = sum(1 for keyword in self.financial_keywords if keyword in text_lower)
        
        # Consider relevant if contains at least 2 financial keywords
        return financial_score >= 2
    
    def _contains_sensitive_patterns(self, text: str) -> bool:
        """Check if text contains sensitive patterns."""
        for pattern in self.sensitive_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _contains_suspicious_patterns(self, filename: str) -> bool:
        """Check if filename contains suspicious patterns."""
        suspicious_patterns = [
            r'\.exe$', r'\.bat$', r'\.cmd$', r'\.scr$', r'\.pif$',
            r'javascript:', r'vbscript:', r'data:'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return True
        return False
    
    def _contains_malicious_content(self, text: str) -> bool:
        """Check if text contains potentially malicious content."""
        malicious_patterns = [
            r'<script', r'javascript:', r'vbscript:', r'data:',
            r'eval\s*\(', r'exec\s*\(', r'system\s*\('
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    async def generate_safety_report(self, validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive safety report."""
        total_validations = len(validation_results)
        valid_count = sum(1 for result in validation_results if result['is_valid'])
        
        all_warnings = []
        all_errors = []
        confidence_scores = []
        
        for result in validation_results:
            all_warnings.extend(result.get('warnings', []))
            all_errors.extend(result.get('errors', []))
            confidence_scores.append(result.get('confidence_score', 0.0))
        
        return {
            'total_validations': total_validations,
            'valid_count': valid_count,
            'success_rate': valid_count / total_validations if total_validations > 0 else 0,
            'total_warnings': len(all_warnings),
            'total_errors': len(all_errors),
            'average_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            'warnings': all_warnings,
            'errors': all_errors,
            'recommendations': self._generate_recommendations(all_warnings, all_errors),
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _generate_recommendations(self, warnings: List[str], errors: List[str]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if errors:
            recommendations.append("Address all errors before proceeding")
        
        if 'High risk of hallucination detected' in warnings:
            recommendations.append("Review AI output for accuracy and add citations")
        
        if 'Output lacks appropriate disclaimers' in warnings:
            recommendations.append("Add appropriate disclaimers to financial advice")
        
        if 'Query may not be financially relevant' in warnings:
            recommendations.append("Consider redirecting to financial topics")
        
        return recommendations
