"""
Evaluation service for measuring system performance and accuracy.
"""
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
import logging

from app.config import settings


class EvaluatorService:
    """Service for evaluating system performance and accuracy."""
    
    def __init__(self):
        """Initialize evaluator service."""
        self.logger = logging.getLogger(__name__)
        self.metrics_history = []
    
    async def evaluate_document_processing(
        self, 
        extracted_data: Dict[str, Any], 
        ground_truth: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate document processing accuracy."""
        evaluation = {
            'timestamp': datetime.utcnow().isoformat(),
            'evaluation_type': 'document_processing',
            'metrics': {},
            'overall_score': 0.0
        }
        
        try:
            # Text extraction accuracy
            if 'extracted_text' in extracted_data and 'text' in ground_truth:
                text_accuracy = self._calculate_text_accuracy(
                    extracted_data['extracted_text'],
                    ground_truth['text']
                )
                evaluation['metrics']['text_accuracy'] = text_accuracy
            
            # Table extraction accuracy
            if 'extracted_tables' in extracted_data and 'tables' in ground_truth:
                table_accuracy = self._calculate_table_accuracy(
                    extracted_data['extracted_tables'],
                    ground_truth['tables']
                )
                evaluation['metrics']['table_accuracy'] = table_accuracy
            
            # Metadata extraction accuracy
            if 'metadata' in extracted_data and 'metadata' in ground_truth:
                metadata_accuracy = self._calculate_metadata_accuracy(
                    extracted_data['metadata'],
                    ground_truth['metadata']
                )
                evaluation['metrics']['metadata_accuracy'] = metadata_accuracy
            
            # Calculate overall score
            scores = [v for v in evaluation['metrics'].values() if isinstance(v, (int, float))]
            evaluation['overall_score'] = np.mean(scores) if scores else 0.0
            
        except Exception as e:
            evaluation['error'] = str(e)
            evaluation['overall_score'] = 0.0
        
        return evaluation
    
    async def evaluate_rag_system(
        self, 
        query: str, 
        retrieved_context: str, 
        ground_truth_context: str
    ) -> Dict[str, Any]:
        """Evaluate RAG system performance."""
        evaluation = {
            'timestamp': datetime.utcnow().isoformat(),
            'evaluation_type': 'rag_system',
            'metrics': {},
            'overall_score': 0.0
        }
        
        try:
            # Relevance score
            relevance_score = self._calculate_relevance_score(
                query, retrieved_context, ground_truth_context
            )
            evaluation['metrics']['relevance_score'] = relevance_score
            
            # Precision and recall
            precision, recall = self._calculate_precision_recall(
                retrieved_context, ground_truth_context
            )
            evaluation['metrics']['precision'] = precision
            evaluation['metrics']['recall'] = recall
            evaluation['metrics']['f1_score'] = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            # Context completeness
            completeness_score = self._calculate_context_completeness(
                retrieved_context, ground_truth_context
            )
            evaluation['metrics']['completeness_score'] = completeness_score
            
            # Calculate overall score
            scores = [v for v in evaluation['metrics'].values() if isinstance(v, (int, float))]
            evaluation['overall_score'] = np.mean(scores) if scores else 0.0
            
        except Exception as e:
            evaluation['error'] = str(e)
            evaluation['overall_score'] = 0.0
        
        return evaluation
    
    async def evaluate_financial_calculations(
        self, 
        calculated_values: Dict[str, float], 
        ground_truth_values: Dict[str, float]
    ) -> Dict[str, Any]:
        """Evaluate financial calculation accuracy."""
        evaluation = {
            'timestamp': datetime.utcnow().isoformat(),
            'evaluation_type': 'financial_calculations',
            'metrics': {},
            'overall_score': 0.0
        }
        
        try:
            # Calculate accuracy for each metric
            accuracy_scores = {}
            for metric, calculated_value in calculated_values.items():
                if metric in ground_truth_values:
                    ground_truth_value = ground_truth_values[metric]
                    if ground_truth_value != 0:
                        accuracy = 1 - abs(calculated_value - ground_truth_value) / abs(ground_truth_value)
                        accuracy_scores[metric] = max(0, accuracy)  # Ensure non-negative
                    else:
                        accuracy_scores[metric] = 1.0 if calculated_value == 0 else 0.0
            
            evaluation['metrics']['individual_accuracies'] = accuracy_scores
            evaluation['metrics']['average_accuracy'] = np.mean(list(accuracy_scores.values()))
            evaluation['metrics']['perfect_matches'] = sum(1 for acc in accuracy_scores.values() if acc == 1.0)
            evaluation['metrics']['total_metrics'] = len(accuracy_scores)
            
            # Calculate overall score
            evaluation['overall_score'] = evaluation['metrics']['average_accuracy']
            
        except Exception as e:
            evaluation['error'] = str(e)
            evaluation['overall_score'] = 0.0
        
        return evaluation
    
    async def evaluate_agent_performance(
        self, 
        agent_results: Dict[str, Any], 
        expected_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate multi-agent system performance."""
        evaluation = {
            'timestamp': datetime.utcnow().isoformat(),
            'evaluation_type': 'agent_performance',
            'metrics': {},
            'overall_score': 0.0
        }
        
        try:
            # Agent completion rates
            completion_rates = {}
            for agent_name, result in agent_results.items():
                if isinstance(result, dict):
                    completion_rates[agent_name] = 1.0 if result.get('status') == 'completed' else 0.0
            
            evaluation['metrics']['completion_rates'] = completion_rates
            evaluation['metrics']['average_completion'] = np.mean(list(completion_rates.values()))
            
            # Response quality scores
            quality_scores = {}
            for agent_name, result in agent_results.items():
                if isinstance(result, dict) and 'result' in result:
                    quality_score = self._assess_response_quality(result['result'])
                    quality_scores[agent_name] = quality_score
            
            evaluation['metrics']['quality_scores'] = quality_scores
            evaluation['metrics']['average_quality'] = np.mean(list(quality_scores.values()))
            
            # Calculate overall score
            evaluation['overall_score'] = (
                evaluation['metrics']['average_completion'] * 0.6 +
                evaluation['metrics']['average_quality'] * 0.4
            )
            
        except Exception as e:
            evaluation['error'] = str(e)
            evaluation['overall_score'] = 0.0
        
        return evaluation
    
    async def evaluate_system_performance(
        self, 
        start_time: float, 
        end_time: float, 
        operation_type: str
    ) -> Dict[str, Any]:
        """Evaluate system performance metrics."""
        evaluation = {
            'timestamp': datetime.utcnow().isoformat(),
            'evaluation_type': 'system_performance',
            'metrics': {},
            'overall_score': 0.0
        }
        
        try:
            # Calculate response time
            response_time = end_time - start_time
            evaluation['metrics']['response_time'] = response_time
            evaluation['metrics']['operation_type'] = operation_type
            
            # Performance benchmarks (in seconds)
            benchmarks = {
                'document_processing': 5.0,
                'chat_query': 2.0,
                'financial_analysis': 3.0,
                'rag_retrieval': 1.0
            }
            
            benchmark = benchmarks.get(operation_type, 5.0)
            performance_score = max(0, 1 - (response_time / benchmark))
            evaluation['metrics']['performance_score'] = performance_score
            
            # Categorize performance
            if response_time <= benchmark * 0.5:
                evaluation['metrics']['performance_category'] = 'excellent'
            elif response_time <= benchmark:
                evaluation['metrics']['performance_category'] = 'good'
            elif response_time <= benchmark * 2:
                evaluation['metrics']['performance_category'] = 'acceptable'
            else:
                evaluation['metrics']['performance_category'] = 'poor'
            
            evaluation['overall_score'] = performance_score
            
        except Exception as e:
            evaluation['error'] = str(e)
            evaluation['overall_score'] = 0.0
        
        return evaluation
    
    def _calculate_text_accuracy(self, extracted_text: str, ground_truth_text: str) -> float:
        """Calculate text extraction accuracy."""
        if not extracted_text or not ground_truth_text:
            return 0.0
        
        # Simple character-level accuracy
        extracted_words = set(extracted_text.lower().split())
        ground_truth_words = set(ground_truth_text.lower().split())
        
        if not ground_truth_words:
            return 0.0
        
        intersection = extracted_words.intersection(ground_truth_words)
        return len(intersection) / len(ground_truth_words)
    
    def _calculate_table_accuracy(self, extracted_tables: List[Dict], ground_truth_tables: List[Dict]) -> float:
        """Calculate table extraction accuracy."""
        if not extracted_tables or not ground_truth_tables:
            return 0.0
        
        # Simple table structure comparison
        extracted_count = len(extracted_tables)
        ground_truth_count = len(ground_truth_tables)
        
        # Accuracy based on table count and structure
        count_accuracy = 1 - abs(extracted_count - ground_truth_count) / max(ground_truth_count, 1)
        
        return max(0, count_accuracy)
    
    def _calculate_metadata_accuracy(self, extracted_metadata: Dict, ground_truth_metadata: Dict) -> float:
        """Calculate metadata extraction accuracy."""
        if not extracted_metadata or not ground_truth_metadata:
            return 0.0
        
        # Compare metadata fields
        extracted_keys = set(extracted_metadata.keys())
        ground_truth_keys = set(ground_truth_metadata.keys())
        
        if not ground_truth_keys:
            return 0.0
        
        # Calculate field accuracy
        field_accuracy = len(extracted_keys.intersection(ground_truth_keys)) / len(ground_truth_keys)
        
        # Calculate value accuracy for common fields
        value_accuracy = 0.0
        common_fields = extracted_keys.intersection(ground_truth_keys)
        
        if common_fields:
            value_matches = 0
            for field in common_fields:
                if extracted_metadata[field] == ground_truth_metadata[field]:
                    value_matches += 1
            
            value_accuracy = value_matches / len(common_fields)
        
        return (field_accuracy + value_accuracy) / 2
    
    def _calculate_relevance_score(self, query: str, retrieved_context: str, ground_truth_context: str) -> float:
        """Calculate relevance score for retrieved context."""
        if not retrieved_context or not ground_truth_context:
            return 0.0
        
        # Simple keyword-based relevance
        query_words = set(query.lower().split())
        retrieved_words = set(retrieved_context.lower().split())
        ground_truth_words = set(ground_truth_context.lower().split())
        
        # Calculate overlap with query
        query_relevance = len(query_words.intersection(retrieved_words)) / max(len(query_words), 1)
        
        # Calculate overlap with ground truth
        ground_truth_relevance = len(ground_truth_words.intersection(retrieved_words)) / max(len(ground_truth_words), 1)
        
        return (query_relevance + ground_truth_relevance) / 2
    
    def _calculate_precision_recall(self, retrieved_context: str, ground_truth_context: str) -> Tuple[float, float]:
        """Calculate precision and recall for retrieved context."""
        if not retrieved_context or not ground_truth_context:
            return 0.0, 0.0
        
        retrieved_words = set(retrieved_context.lower().split())
        ground_truth_words = set(ground_truth_context.lower().split())
        
        if not retrieved_words or not ground_truth_words:
            return 0.0, 0.0
        
        intersection = retrieved_words.intersection(ground_truth_words)
        
        precision = len(intersection) / len(retrieved_words) if retrieved_words else 0.0
        recall = len(intersection) / len(ground_truth_words) if ground_truth_words else 0.0
        
        return precision, recall
    
    def _calculate_context_completeness(self, retrieved_context: str, ground_truth_context: str) -> float:
        """Calculate completeness of retrieved context."""
        if not retrieved_context or not ground_truth_context:
            return 0.0
        
        retrieved_words = set(retrieved_context.lower().split())
        ground_truth_words = set(ground_truth_context.lower().split())
        
        if not ground_truth_words:
            return 0.0
        
        intersection = retrieved_words.intersection(ground_truth_words)
        return len(intersection) / len(ground_truth_words)
    
    def _assess_response_quality(self, response: str) -> float:
        """Assess the quality of an agent response."""
        if not response:
            return 0.0
        
        quality_score = 0.0
        
        # Length appropriateness (not too short, not too long)
        word_count = len(response.split())
        if 10 <= word_count <= 500:
            quality_score += 0.3
        elif 5 <= word_count < 10 or 500 < word_count <= 1000:
            quality_score += 0.2
        
        # Presence of specific financial terms
        financial_terms = ['ratio', 'margin', 'revenue', 'profit', 'asset', 'liability', 'cash', 'flow']
        financial_term_count = sum(1 for term in financial_terms if term in response.lower())
        quality_score += min(0.3, financial_term_count * 0.05)
        
        # Presence of numbers (indicating specific analysis)
        number_count = len([word for word in response.split() if word.replace('.', '').replace('%', '').isdigit()])
        if number_count > 0:
            quality_score += min(0.2, number_count * 0.02)
        
        # Presence of structured elements
        if any(marker in response for marker in ['1.', '2.', '•', '-', '*']):
            quality_score += 0.2
        
        return min(1.0, quality_score)
    
    async def generate_evaluation_report(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive evaluation report."""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_evaluations': len(evaluations),
            'summary': {},
            'detailed_results': evaluations,
            'recommendations': []
        }
        
        try:
            # Calculate summary statistics
            overall_scores = [eval_result.get('overall_score', 0) for eval_result in evaluations]
            report['summary']['average_score'] = np.mean(overall_scores) if overall_scores else 0.0
            report['summary']['min_score'] = np.min(overall_scores) if overall_scores else 0.0
            report['summary']['max_score'] = np.max(overall_scores) if overall_scores else 0.0
            
            # Categorize performance
            if report['summary']['average_score'] >= 0.9:
                report['summary']['performance_level'] = 'excellent'
            elif report['summary']['average_score'] >= 0.8:
                report['summary']['performance_level'] = 'good'
            elif report['summary']['average_score'] >= 0.7:
                report['summary']['performance_level'] = 'acceptable'
            else:
                report['summary']['performance_level'] = 'needs_improvement'
            
            # Generate recommendations
            report['recommendations'] = self._generate_improvement_recommendations(evaluations)
            
        except Exception as e:
            report['error'] = str(e)
        
        return report
    
    def _generate_improvement_recommendations(self, evaluations: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement recommendations based on evaluation results."""
        recommendations = []
        
        # Analyze evaluation types and scores
        evaluation_types = {}
        for eval_result in evaluations:
            eval_type = eval_result.get('evaluation_type', 'unknown')
            score = eval_result.get('overall_score', 0)
            
            if eval_type not in evaluation_types:
                evaluation_types[eval_type] = []
            evaluation_types[eval_type].append(score)
        
        # Generate specific recommendations
        for eval_type, scores in evaluation_types.items():
            avg_score = np.mean(scores)
            
            if eval_type == 'document_processing' and avg_score < 0.8:
                recommendations.append("Improve document processing accuracy by enhancing OCR and text extraction algorithms")
            
            elif eval_type == 'rag_system' and avg_score < 0.8:
                recommendations.append("Enhance RAG system by improving embedding quality and retrieval algorithms")
            
            elif eval_type == 'financial_calculations' and avg_score < 0.9:
                recommendations.append("Improve financial calculation accuracy by adding validation and error checking")
            
            elif eval_type == 'agent_performance' and avg_score < 0.8:
                recommendations.append("Optimize agent workflows and improve response quality")
            
            elif eval_type == 'system_performance' and avg_score < 0.7:
                recommendations.append("Optimize system performance by improving response times and resource utilization")
        
        return recommendations
