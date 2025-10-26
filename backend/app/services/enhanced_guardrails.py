"""
Enhanced Guardrails service for FinMDA-Bot.
Implements comprehensive input/output validation, safety measures, and financial domain validation.
"""
import re
import logging
import hashlib
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from pydantic import BaseModel, validator, Field
from enum import Enum
from datetime import datetime, timedelta

class ValidationLevel(str, Enum):
    """Validation levels for different types of content."""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"

class SecurityLevel(str, Enum):
    """Security levels for different operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FinancialDomain(str, Enum):
    """Financial domain categories."""
    CORPORATE = "corporate"
    PERSONAL = "personal"
    INVESTMENT = "investment"
    ACCOUNTING = "accounting"
    BANKING = "banking"
    INSURANCE = "insurance"

class InputGuardrails:
    """Enhanced input validation and sanitization."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.allowed_file_types = ['.pdf', '.xlsx', '.xls', '.csv', '.docx', '.txt']
        self.max_query_length = 2000
        self.max_files_per_request = 5
        
        # Enhanced security patterns
        self.suspicious_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__',
            r'os\.system',
            r'subprocess',
            r'pickle\.loads',
            r'yaml\.load'
        ]
        
        # Financial-specific validation patterns
        self.financial_patterns = {
            'ratios': r'\b(?:current ratio|quick ratio|debt ratio|roe|roa|gross margin|net margin)\b',
            'statements': r'\b(?:income statement|balance sheet|cash flow|profit loss|p&l)\b',
            'metrics': r'\b(?:revenue|profit|loss|assets|liabilities|equity|cash|debt)\b',
            'time_periods': r'\b(?:quarterly|annual|monthly|yoy|qoq|year over year|quarter over quarter)\b'
        }
        
        # Risk assessment patterns
        self.risk_indicators = [
            'high risk', 'speculative', 'volatile', 'uncertain', 'risky',
            'guaranteed return', 'no risk', 'sure thing', 'can\'t lose'
        ]
    
    def validate_file_upload(self, file_path: str, file_size: int, file_type: str, 
                           file_hash: str = None) -> Tuple[bool, str, Dict[str, Any]]:
        """Enhanced file validation with security checks."""
        try:
            validation_metadata = {
                'file_size': file_size,
                'file_type': file_type,
                'validation_timestamp': datetime.now().isoformat(),
                'security_checks': []
            }
            
            # Check file size
            if file_size > self.max_file_size:
                return False, f"File size {file_size} exceeds maximum allowed size {self.max_file_size}", validation_metadata
            
            # Check file type
            if not any(file_path.lower().endswith(ext) for ext in self.allowed_file_types):
                return False, f"File type {file_type} not allowed. Allowed types: {self.allowed_file_types}", validation_metadata
            
            # Check for suspicious content in filename
            if self._contains_suspicious_content(file_path):
                validation_metadata['security_checks'].append('suspicious_filename')
                return False, "File contains potentially malicious content in filename", validation_metadata
            
            # Hash validation (if provided)
            if file_hash and not self._validate_file_hash(file_path, file_hash):
                validation_metadata['security_checks'].append('hash_mismatch')
                return False, "File hash validation failed", validation_metadata
            
            validation_metadata['security_checks'].append('passed')
            return True, "File validation passed", validation_metadata
            
        except Exception as e:
            self.logger.error(f"File validation error: {str(e)}")
            return False, f"File validation failed: {str(e)}", validation_metadata
    
    def validate_query(self, query: str, domain: FinancialDomain = None) -> Tuple[bool, str, Dict[str, Any]]:
        """Enhanced query validation with financial domain checking."""
        try:
            validation_metadata = {
                'query_length': len(query),
                'domain': domain,
                'validation_timestamp': datetime.now().isoformat(),
                'financial_relevance_score': 0.0,
                'risk_indicators': []
            }
            
            # Check query length
            if len(query) > self.max_query_length:
                return False, f"Query length {len(query)} exceeds maximum allowed length {self.max_query_length}", validation_metadata
            
            # Check for suspicious patterns
            if self._contains_suspicious_content(query):
                return False, "Query contains potentially malicious content", validation_metadata
            
            # Financial relevance scoring
            relevance_score = self._calculate_financial_relevance(query)
            validation_metadata['financial_relevance_score'] = relevance_score
            
            if relevance_score < 0.3:
                return False, "Query is not financially relevant enough", validation_metadata
            
            # Risk indicator detection
            risk_indicators = self._detect_risk_indicators(query)
            validation_metadata['risk_indicators'] = risk_indicators
            
            if risk_indicators:
                validation_metadata['warnings'] = [f"Risk indicators detected: {', '.join(risk_indicators)}"]
            
            # Domain-specific validation
            if domain:
                domain_valid, domain_message = self._validate_domain_specific(query, domain)
                if not domain_valid:
                    return False, domain_message, validation_metadata
            
            return True, "Query validation passed", validation_metadata
            
        except Exception as e:
            self.logger.error(f"Query validation error: {str(e)}")
            return False, f"Query validation failed: {str(e)}", validation_metadata
    
    def _calculate_financial_relevance(self, query: str) -> float:
        """Calculate financial relevance score."""
        query_lower = query.lower()
        score = 0.0
        
        for category, pattern in self.financial_patterns.items():
            matches = len(re.findall(pattern, query_lower, re.IGNORECASE))
            score += matches * 0.1
        
        # Normalize score
        return min(score, 1.0)
    
    def _detect_risk_indicators(self, query: str) -> List[str]:
        """Detect risk-related language in query."""
        query_lower = query.lower()
        detected_risks = []
        
        for indicator in self.risk_indicators:
            if indicator in query_lower:
                detected_risks.append(indicator)
        
        return detected_risks
    
    def _validate_domain_specific(self, query: str, domain: FinancialDomain) -> Tuple[bool, str]:
        """Validate query against specific financial domain."""
        domain_keywords = {
            FinancialDomain.CORPORATE: ['corporate', 'company', 'business', 'enterprise', 'firm'],
            FinancialDomain.PERSONAL: ['personal', 'individual', 'household', 'family', 'budget'],
            FinancialDomain.INVESTMENT: ['investment', 'portfolio', 'stock', 'bond', 'trading'],
            FinancialDomain.ACCOUNTING: ['accounting', 'bookkeeping', 'audit', 'compliance'],
            FinancialDomain.BANKING: ['banking', 'loan', 'credit', 'mortgage', 'deposit'],
            FinancialDomain.INSURANCE: ['insurance', 'policy', 'premium', 'coverage', 'claim']
        }
        
        query_lower = query.lower()
        domain_keywords_list = domain_keywords.get(domain, [])
        
        if not any(keyword in query_lower for keyword in domain_keywords_list):
            return False, f"Query does not match {domain.value} domain requirements"
        
        return True, "Domain validation passed"
    
    def _validate_file_hash(self, file_path: str, expected_hash: str) -> bool:
        """Validate file hash for integrity."""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash == expected_hash
        except:
            return False
    
    def _contains_suspicious_content(self, content: str) -> bool:
        """Check for suspicious patterns in content."""
        content_lower = content.lower()
        for pattern in self.suspicious_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True
        return False

class OutputGuardrails:
    """Enhanced output validation and safety measures."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_response_length = 10000
        self.min_confidence_threshold = 0.3
        self.max_confidence_threshold = 1.0
        
        # Enhanced disclaimer templates
        self.disclaimer_templates = {
            'general': "This analysis is for informational purposes only and should not be considered as financial advice.",
            'investment': "Past performance does not guarantee future results. All investments carry risk.",
            'forecasting': "Forecasts are based on historical data and assumptions that may not hold true.",
            'regulatory': "This information is not intended to replace professional financial advice."
        }
        
        # Hallucination detection patterns
        self.hallucination_patterns = [
            r"I cannot find",
            r"Based on my knowledge",
            r"I don't have access to",
            r"I'm not sure",
            r"I cannot determine",
            r"Unable to find",
            r"According to my training",
            r"As an AI, I"
        ]
        
        # Confidence scoring factors
        self.confidence_factors = {
            'numerical_accuracy': 0.3,
            'source_citations': 0.2,
            'domain_expertise': 0.2,
            'response_completeness': 0.15,
            'factual_consistency': 0.15
        }
    
    def validate_response(self, response: str, confidence_score: float, 
                         response_type: str = 'general') -> Tuple[bool, str, str, Dict[str, Any]]:
        """Enhanced response validation with confidence scoring."""
        try:
            validation_metadata = {
                'response_length': len(response),
                'confidence_score': confidence_score,
                'response_type': response_type,
                'validation_timestamp': datetime.now().isoformat(),
                'quality_metrics': {}
            }
            
            # Check response length
            if len(response) > self.max_response_length:
                return False, "Response too long", response, validation_metadata
            
            # Check confidence score
            if confidence_score < self.min_confidence_threshold:
                return False, "Low confidence response", response, validation_metadata
            
            if confidence_score > self.max_confidence_threshold:
                return False, "Invalid confidence score", response, validation_metadata
            
            # Enhanced hallucination detection
            hallucination_score = self._detect_hallucination_enhanced(response)
            validation_metadata['quality_metrics']['hallucination_score'] = hallucination_score
            
            if hallucination_score > 0.7:
                return False, "High probability of hallucination detected", response, validation_metadata
            
            # Factual consistency check
            consistency_score = self._check_factual_consistency(response)
            validation_metadata['quality_metrics']['consistency_score'] = consistency_score
            
            # Source citation check
            citation_score = self._check_source_citations(response)
            validation_metadata['quality_metrics']['citation_score'] = citation_score
            
            # Add appropriate disclaimers
            if self._needs_disclaimer(response, response_type):
                response = self._add_disclaimers(response, response_type)
                validation_metadata['disclaimers_added'] = True
            
            # Quality assessment
            overall_quality = self._assess_response_quality(response, validation_metadata['quality_metrics'])
            validation_metadata['quality_metrics']['overall_quality'] = overall_quality
            
            return True, "Response validation passed", response, validation_metadata
            
        except Exception as e:
            self.logger.error(f"Response validation error: {str(e)}")
            return False, "Response validation failed", response, validation_metadata
    
    def _detect_hallucination_enhanced(self, response: str) -> float:
        """Enhanced hallucination detection with scoring."""
        response_lower = response.lower()
        hallucination_score = 0.0
        
        for pattern in self.hallucination_patterns:
            if re.search(pattern, response_lower, re.IGNORECASE):
                hallucination_score += 0.2
        
        # Check for contradictory statements
        contradictions = self._detect_contradictions(response)
        hallucination_score += contradictions * 0.1
        
        return min(hallucination_score, 1.0)
    
    def _detect_contradictions(self, response: str) -> int:
        """Detect contradictory statements in response."""
        contradiction_pairs = [
            ('increase', 'decrease'),
            ('profit', 'loss'),
            ('positive', 'negative'),
            ('high', 'low'),
            ('good', 'bad')
        ]
        
        contradictions = 0
        response_lower = response.lower()
        
        for pair in contradiction_pairs:
            if pair[0] in response_lower and pair[1] in response_lower:
                contradictions += 1
        
        return contradictions
    
    def _check_factual_consistency(self, response: str) -> float:
        """Check factual consistency in response."""
        consistency_indicators = [
            'according to', 'based on', 'data shows', 'statistics indicate',
            'research shows', 'studies suggest'
        ]
        
        response_lower = response.lower()
        consistency_score = 0.0
        
        for indicator in consistency_indicators:
            if indicator in response_lower:
                consistency_score += 0.2
        
        return min(consistency_score, 1.0)
    
    def _check_source_citations(self, response: str) -> float:
        """Check for source citations in response."""
        citation_patterns = [
            r'\[.*?\]',  # [source]
            r'\(.*?\)',  # (source)
            r'according to.*?',  # according to source
            r'based on.*?',  # based on source
            r'source:.*?',  # source: reference
        ]
        
        citation_score = 0.0
        for pattern in citation_patterns:
            matches = len(re.findall(pattern, response, re.IGNORECASE))
            citation_score += matches * 0.1
        
        return min(citation_score, 1.0)
    
    def _assess_response_quality(self, response: str, quality_metrics: Dict[str, float]) -> float:
        """Assess overall response quality."""
        weights = {
            'hallucination_score': -0.3,  # Negative weight
            'consistency_score': 0.3,
            'citation_score': 0.2,
            'numerical_accuracy': 0.2
        }
        
        quality_score = 0.5  # Base score
        
        for metric, weight in weights.items():
            if metric in quality_metrics:
                quality_score += quality_metrics[metric] * weight
        
        return max(0.0, min(1.0, quality_score))
    
    def _needs_disclaimer(self, response: str, response_type: str) -> bool:
        """Check if response needs disclaimer based on type and content."""
        disclaimer_triggers = [
            'recommend', 'suggest', 'advise', 'buy', 'sell', 'invest',
            'guarantee', 'promise', 'certain', 'definitely', 'sure',
            'will happen', 'guaranteed', 'risk-free'
        ]
        
        response_lower = response.lower()
        has_triggers = any(trigger in response_lower for trigger in disclaimer_triggers)
        
        # Type-specific disclaimer needs
        type_needs_disclaimer = response_type in ['investment', 'forecasting', 'advice']
        
        return has_triggers or type_needs_disclaimer
    
    def _add_disclaimers(self, response: str, response_type: str) -> str:
        """Add appropriate disclaimers to response."""
        disclaimers = []
        
        # General disclaimer
        disclaimers.append(self.disclaimer_templates['general'])
        
        # Type-specific disclaimers
        if response_type in ['investment', 'forecasting']:
            disclaimers.append(self.disclaimer_templates['investment'])
        
        if response_type == 'forecasting':
            disclaimers.append(self.disclaimer_templates['forecasting'])
        
        # Regulatory disclaimer
        disclaimers.append(self.disclaimer_templates['regulatory'])
        
        disclaimer_text = "\n\n**Disclaimer:** " + " ".join(disclaimers)
        return response + disclaimer_text

class EnhancedGuardrailsService:
    """Enhanced main guardrails service."""
    
    def __init__(self):
        self.input_guardrails = InputGuardrails()
        self.output_guardrails = OutputGuardrails()
        self.logger = logging.getLogger(__name__)
        self.validation_history = []
    
    def validate_input(self, file_path: str = None, file_size: int = None, 
                      file_type: str = None, query: str = None, 
                      domain: FinancialDomain = None, file_hash: str = None) -> Dict[str, Any]:
        """Enhanced input validation with comprehensive checks."""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {},
            "security_level": SecurityLevel.LOW,
            "validation_timestamp": datetime.now().isoformat()
        }
        
        try:
            # Validate file upload if provided
            if file_path and file_size and file_type:
                is_valid, message, metadata = self.input_guardrails.validate_file_upload(
                    file_path, file_size, file_type, file_hash
                )
                validation_results["metadata"]["file_validation"] = metadata
                
                if not is_valid:
                    validation_results["valid"] = False
                    validation_results["errors"].append(f"File validation: {message}")
                    validation_results["security_level"] = SecurityLevel.HIGH
                else:
                    validation_results["security_level"] = SecurityLevel.MEDIUM
            
            # Validate query if provided
            if query:
                is_valid, message, metadata = self.input_guardrails.validate_query(query, domain)
                validation_results["metadata"]["query_validation"] = metadata
                
                if not is_valid:
                    validation_results["valid"] = False
                    validation_results["errors"].append(f"Query validation: {message}")
                else:
                    # Check for risk indicators
                    if metadata.get('risk_indicators'):
                        validation_results["warnings"].extend(metadata.get('warnings', []))
                        validation_results["security_level"] = SecurityLevel.MEDIUM
            
            # Log validation attempt
            self._log_validation_attempt(validation_results)
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Input validation error: {str(e)}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "metadata": {},
                "security_level": SecurityLevel.CRITICAL
            }
    
    def validate_output(self, response: str, confidence_score: float, 
                       response_type: str = 'general') -> Dict[str, Any]:
        """Enhanced output validation with quality assessment."""
        try:
            is_valid, status, processed_response, metadata = self.output_guardrails.validate_response(
                response, confidence_score, response_type
            )
            
            validation_results = {
                "valid": is_valid,
                "status": status,
                "response": processed_response,
                "confidence_score": confidence_score,
                "quality_metrics": metadata.get('quality_metrics', {}),
                "validation_timestamp": datetime.now().isoformat()
            }
            
            # Log validation attempt
            self._log_validation_attempt(validation_results)
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Output validation error: {str(e)}")
            return {
                "valid": False,
                "status": "Validation failed",
                "response": response,
                "confidence_score": confidence_score,
                "error": str(e)
            }
    
    def _log_validation_attempt(self, validation_results: Dict[str, Any]):
        """Log validation attempt for audit trail."""
        self.validation_history.append(validation_results)
        
        # Keep only last 1000 validations
        if len(self.validation_history) > 1000:
            self.validation_history = self.validation_history[-1000:]
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        if not self.validation_history:
            return {"message": "No validation history available"}
        
        total_validations = len(self.validation_history)
        successful_validations = sum(1 for v in self.validation_history if v.get('valid', False))
        
        return {
            "total_validations": total_validations,
            "successful_validations": successful_validations,
            "success_rate": successful_validations / total_validations if total_validations > 0 else 0,
            "recent_validations": self.validation_history[-10:]  # Last 10 validations
        }
