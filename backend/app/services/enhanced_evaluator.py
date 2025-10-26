"""
Enhanced Evaluation service for FinMDA-Bot.
Implements comprehensive evaluation metrics, accuracy assessment, and performance monitoring.
"""
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import asyncio
import aiofiles
from pathlib import Path

class EvaluationMetrics:
    """Comprehensive evaluation metrics for different aspects of the system."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history = []
        
    async def calculate_accuracy_metrics(self, predictions: List[Any], ground_truth: List[Any], 
                                       metric_type: str = 'classification') -> Dict[str, float]:
        """Calculate accuracy metrics for predictions vs ground truth."""
        try:
            if metric_type == 'classification':
                return {
                    'accuracy': accuracy_score(ground_truth, predictions),
                    'precision': precision_score(ground_truth, predictions, average='weighted', zero_division=0),
                    'recall': recall_score(ground_truth, predictions, average='weighted', zero_division=0),
                    'f1_score': f1_score(ground_truth, predictions, average='weighted', zero_division=0)
                }
            elif metric_type == 'regression':
                return {
                    'mse': mean_squared_error(ground_truth, predictions),
                    'mae': mean_absolute_error(ground_truth, predictions),
                    'r2_score': r2_score(ground_truth, predictions)
                }
            else:
                raise ValueError(f"Unsupported metric type: {metric_type}")
                
        except Exception as e:
            self.logger.error(f"Error calculating accuracy metrics: {str(e)}")
            return {}
    
    async def calculate_rag_metrics(self, retrieved_docs: List[Dict], relevant_docs: List[Dict], 
                                   k_values: List[int] = [1, 3, 5, 10]) -> Dict[str, float]:
        """Calculate RAG-specific metrics."""
        try:
            metrics = {}
            
            for k in k_values:
                # Precision@K
                precision_k = self._calculate_precision_at_k(retrieved_docs[:k], relevant_docs)
                metrics[f'precision@{k}'] = precision_k
                
                # Recall@K
                recall_k = self._calculate_recall_at_k(retrieved_docs[:k], relevant_docs)
                metrics[f'recall@{k}'] = recall_k
                
                # F1@K
                if precision_k + recall_k > 0:
                    f1_k = 2 * (precision_k * recall_k) / (precision_k + recall_k)
                else:
                    f1_k = 0.0
                metrics[f'f1@{k}'] = f1_k
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating RAG metrics: {str(e)}")
            return {}
    
    def _calculate_precision_at_k(self, retrieved: List[Dict], relevant: List[Dict]) -> float:
        """Calculate precision at K."""
        if not retrieved:
            return 0.0
        
        relevant_ids = {doc.get('id', doc.get('source', '')) for doc in relevant}
        retrieved_ids = [doc.get('id', doc.get('source', '')) for doc in retrieved]
        
        relevant_retrieved = sum(1 for doc_id in retrieved_ids if doc_id in relevant_ids)
        return relevant_retrieved / len(retrieved)
    
    def _calculate_recall_at_k(self, retrieved: List[Dict], relevant: List[Dict]) -> float:
        """Calculate recall at K."""
        if not relevant:
            return 0.0
        
        relevant_ids = {doc.get('id', doc.get('source', '')) for doc in relevant}
        retrieved_ids = [doc.get('id', doc.get('source', '')) for doc in retrieved]
        
        relevant_retrieved = sum(1 for doc_id in retrieved_ids if doc_id in relevant_ids)
        return relevant_retrieved / len(relevant)
    
    async def calculate_response_quality_metrics(self, responses: List[Dict]) -> Dict[str, float]:
        """Calculate response quality metrics."""
        try:
            metrics = {
                'average_length': 0.0,
                'completeness_score': 0.0,
                'clarity_score': 0.0,
                'relevance_score': 0.0,
                'citation_score': 0.0
            }
            
            if not responses:
                return metrics
            
            total_length = sum(len(response.get('content', '')) for response in responses)
            metrics['average_length'] = total_length / len(responses)
            
            # Calculate completeness (based on expected fields)
            completeness_scores = []
            for response in responses:
                completeness = self._calculate_completeness(response)
                completeness_scores.append(completeness)
            metrics['completeness_score'] = np.mean(completeness_scores)
            
            # Calculate clarity (based on readability indicators)
            clarity_scores = []
            for response in responses:
                clarity = self._calculate_clarity(response)
                clarity_scores.append(clarity)
            metrics['clarity_score'] = np.mean(clarity_scores)
            
            # Calculate relevance (based on financial domain keywords)
            relevance_scores = []
            for response in responses:
                relevance = self._calculate_relevance(response)
                relevance_scores.append(relevance)
            metrics['relevance_score'] = np.mean(relevance_scores)
            
            # Calculate citation score
            citation_scores = []
            for response in responses:
                citation = self._calculate_citation_score(response)
                citation_scores.append(citation)
            metrics['citation_score'] = np.mean(citation_scores)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating response quality metrics: {str(e)}")
            return {}
    
    def _calculate_completeness(self, response: Dict) -> float:
        """Calculate completeness score for a response."""
        content = response.get('content', '')
        expected_elements = ['analysis', 'conclusion', 'data', 'recommendation']
        
        score = 0.0
        for element in expected_elements:
            if element in content.lower():
                score += 0.25
        
        return min(score, 1.0)
    
    def _calculate_clarity(self, response: Dict) -> float:
        """Calculate clarity score for a response."""
        content = response.get('content', '')
        
        # Simple clarity indicators
        clarity_indicators = [
            'clearly', 'specifically', 'in detail', 'precisely',
            'exactly', 'specifically', 'concretely'
        ]
        
        score = 0.0
        for indicator in clarity_indicators:
            if indicator in content.lower():
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_relevance(self, response: Dict) -> float:
        """Calculate relevance score for a response."""
        content = response.get('content', '')
        financial_keywords = [
            'revenue', 'profit', 'loss', 'asset', 'liability', 'equity',
            'cash', 'debt', 'ratio', 'margin', 'return', 'investment'
        ]
        
        score = 0.0
        for keyword in financial_keywords:
            if keyword in content.lower():
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_citation_score(self, response: Dict) -> float:
        """Calculate citation score for a response."""
        content = response.get('content', '')
        
        citation_patterns = [
            r'\[.*?\]',  # [source]
            r'\(.*?\)',  # (source)
            r'according to',  # according to source
            r'based on',  # based on source
            r'source:',  # source: reference
        ]
        
        import re
        citation_count = 0
        for pattern in citation_patterns:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            citation_count += matches
        
        # Normalize citation score
        return min(citation_count * 0.1, 1.0)

class PerformanceMonitor:
    """Performance monitoring and metrics collection."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.performance_data = []
        
    async def record_latency(self, operation: str, latency_ms: float, 
                           metadata: Dict[str, Any] = None):
        """Record operation latency."""
        try:
            record = {
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'latency_ms': latency_ms,
                'metadata': metadata or {}
            }
            self.performance_data.append(record)
            
            # Keep only last 10000 records
            if len(self.performance_data) > 10000:
                self.performance_data = self.performance_data[-10000:]
                
        except Exception as e:
            self.logger.error(f"Error recording latency: {str(e)}")
    
    async def record_throughput(self, operation: str, count: int, 
                              time_window_seconds: int = 60):
        """Record operation throughput."""
        try:
            current_time = datetime.now()
            window_start = current_time - timedelta(seconds=time_window_seconds)
            
            # Count operations in time window
            recent_operations = [
                record for record in self.performance_data
                if record['operation'] == operation and
                datetime.fromisoformat(record['timestamp']) >= window_start
            ]
            
            throughput = len(recent_operations) / time_window_seconds
            
            return {
                'operation': operation,
                'throughput_per_second': throughput,
                'time_window_seconds': time_window_seconds,
                'total_operations': len(recent_operations)
            }
            
        except Exception as e:
            self.logger.error(f"Error recording throughput: {str(e)}")
            return {}
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        try:
            if not self.performance_data:
                return {"message": "No performance data available"}
            
            # Group by operation
            operations = {}
            for record in self.performance_data:
                op = record['operation']
                if op not in operations:
                    operations[op] = []
                operations[op].append(record['latency_ms'])
            
            summary = {}
            for op, latencies in operations.items():
                summary[op] = {
                    'count': len(latencies),
                    'avg_latency_ms': np.mean(latencies),
                    'median_latency_ms': np.median(latencies),
                    'p95_latency_ms': np.percentile(latencies, 95),
                    'p99_latency_ms': np.percentile(latencies, 99),
                    'min_latency_ms': np.min(latencies),
                    'max_latency_ms': np.max(latencies)
                }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {str(e)}")
            return {}

class FinancialAccuracyEvaluator:
    """Specialized evaluator for financial calculations and accuracy."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def evaluate_financial_ratios(self, calculated_ratios: Dict[str, float], 
                                      expected_ratios: Dict[str, float], 
                                      tolerance: float = 0.05) -> Dict[str, Any]:
        """Evaluate accuracy of financial ratio calculations."""
        try:
            results = {
                'total_ratios': len(calculated_ratios),
                'accurate_ratios': 0,
                'inaccurate_ratios': 0,
                'accuracy_percentage': 0.0,
                'ratio_errors': {},
                'overall_accuracy': 0.0
            }
            
            for ratio_name, calculated_value in calculated_ratios.items():
                if ratio_name in expected_ratios:
                    expected_value = expected_ratios[ratio_name]
                    
                    # Calculate relative error
                    if expected_value != 0:
                        relative_error = abs(calculated_value - expected_value) / abs(expected_value)
                    else:
                        relative_error = abs(calculated_value - expected_value)
                    
                    if relative_error <= tolerance:
                        results['accurate_ratios'] += 1
                    else:
                        results['inaccurate_ratios'] += 1
                        results['ratio_errors'][ratio_name] = {
                            'calculated': calculated_value,
                            'expected': expected_value,
                            'relative_error': relative_error
                        }
            
            if results['total_ratios'] > 0:
                results['accuracy_percentage'] = (results['accurate_ratios'] / results['total_ratios']) * 100
                results['overall_accuracy'] = results['accurate_ratios'] / results['total_ratios']
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error evaluating financial ratios: {str(e)}")
            return {}
    
    async def evaluate_forecasting_accuracy(self, predictions: List[float], 
                                           actual_values: List[float]) -> Dict[str, float]:
        """Evaluate forecasting accuracy."""
        try:
            if len(predictions) != len(actual_values):
                raise ValueError("Predictions and actual values must have same length")
            
            # Calculate various accuracy metrics
            mse = mean_squared_error(actual_values, predictions)
            mae = mean_absolute_error(actual_values, predictions)
            rmse = np.sqrt(mse)
            
            # Calculate MAPE (Mean Absolute Percentage Error)
            mape = np.mean(np.abs((np.array(actual_values) - np.array(predictions)) / np.array(actual_values))) * 100
            
            # Calculate directional accuracy (for trend prediction)
            directional_accuracy = 0.0
            if len(predictions) > 1:
                pred_directions = np.diff(predictions)
                actual_directions = np.diff(actual_values)
                directional_accuracy = np.mean((pred_directions * actual_directions) > 0)
            
            return {
                'mse': mse,
                'mae': mae,
                'rmse': rmse,
                'mape': mape,
                'directional_accuracy': directional_accuracy,
                'r2_score': r2_score(actual_values, predictions)
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating forecasting accuracy: {str(e)}")
            return {}

class EnhancedEvaluator:
    """Enhanced main evaluation service."""
    
    def __init__(self):
        self.metrics = EvaluationMetrics()
        self.performance_monitor = PerformanceMonitor()
        self.financial_evaluator = FinancialAccuracyEvaluator()
        self.logger = logging.getLogger(__name__)
        self.evaluation_results = []
        
    async def run_comprehensive_evaluation(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive evaluation on test data."""
        try:
            evaluation_results = {
                'timestamp': datetime.now().isoformat(),
                'test_data_size': len(test_data),
                'metrics': {},
                'performance': {},
                'financial_accuracy': {},
                'overall_score': 0.0
            }
            
            # Evaluate accuracy metrics
            if 'predictions' in test_data and 'ground_truth' in test_data:
                accuracy_metrics = await self.metrics.calculate_accuracy_metrics(
                    test_data['predictions'], 
                    test_data['ground_truth'],
                    test_data.get('metric_type', 'classification')
                )
                evaluation_results['metrics']['accuracy'] = accuracy_metrics
            
            # Evaluate RAG metrics
            if 'retrieved_docs' in test_data and 'relevant_docs' in test_data:
                rag_metrics = await self.metrics.calculate_rag_metrics(
                    test_data['retrieved_docs'],
                    test_data['relevant_docs']
                )
                evaluation_results['metrics']['rag'] = rag_metrics
            
            # Evaluate response quality
            if 'responses' in test_data:
                quality_metrics = await self.metrics.calculate_response_quality_metrics(
                    test_data['responses']
                )
                evaluation_results['metrics']['quality'] = quality_metrics
            
            # Evaluate financial accuracy
            if 'calculated_ratios' in test_data and 'expected_ratios' in test_data:
                financial_accuracy = await self.financial_evaluator.evaluate_financial_ratios(
                    test_data['calculated_ratios'],
                    test_data['expected_ratios']
                )
                evaluation_results['financial_accuracy'] = financial_accuracy
            
            # Get performance summary
            performance_summary = await self.performance_monitor.get_performance_summary()
            evaluation_results['performance'] = performance_summary
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(evaluation_results)
            evaluation_results['overall_score'] = overall_score
            
            # Store results
            self.evaluation_results.append(evaluation_results)
            
            return evaluation_results
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive evaluation: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_overall_score(self, evaluation_results: Dict[str, Any]) -> float:
        """Calculate overall evaluation score."""
        try:
            score_components = []
            
            # Accuracy score (40% weight)
            if 'accuracy' in evaluation_results.get('metrics', {}):
                accuracy_metrics = evaluation_results['metrics']['accuracy']
                if 'accuracy' in accuracy_metrics:
                    score_components.append(('accuracy', accuracy_metrics['accuracy'], 0.4))
            
            # RAG score (30% weight)
            if 'rag' in evaluation_results.get('metrics', {}):
                rag_metrics = evaluation_results['metrics']['rag']
                if 'precision@5' in rag_metrics:
                    score_components.append(('rag', rag_metrics['precision@5'], 0.3))
            
            # Quality score (20% weight)
            if 'quality' in evaluation_results.get('metrics', {}):
                quality_metrics = evaluation_results['metrics']['quality']
                if 'completeness_score' in quality_metrics:
                    score_components.append(('quality', quality_metrics['completeness_score'], 0.2))
            
            # Financial accuracy score (10% weight)
            if 'financial_accuracy' in evaluation_results:
                financial_accuracy = evaluation_results['financial_accuracy']
                if 'overall_accuracy' in financial_accuracy:
                    score_components.append(('financial', financial_accuracy['overall_accuracy'], 0.1))
            
            # Calculate weighted average
            if score_components:
                total_weight = sum(weight for _, _, weight in score_components)
                weighted_score = sum(score * weight for _, score, weight in score_components)
                return weighted_score / total_weight if total_weight > 0 else 0.0
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating overall score: {str(e)}")
            return 0.0
    
    async def generate_evaluation_report(self) -> Dict[str, Any]:
        """Generate comprehensive evaluation report."""
        try:
            if not self.evaluation_results:
                return {"message": "No evaluation results available"}
            
            # Aggregate results
            total_evaluations = len(self.evaluation_results)
            overall_scores = [result.get('overall_score', 0.0) for result in self.evaluation_results]
            
            report = {
                'report_timestamp': datetime.now().isoformat(),
                'total_evaluations': total_evaluations,
                'average_overall_score': np.mean(overall_scores) if overall_scores else 0.0,
                'score_distribution': {
                    'min': np.min(overall_scores) if overall_scores else 0.0,
                    'max': np.max(overall_scores) if overall_scores else 0.0,
                    'median': np.median(overall_scores) if overall_scores else 0.0,
                    'std': np.std(overall_scores) if overall_scores else 0.0
                },
                'recent_evaluations': self.evaluation_results[-5:],  # Last 5 evaluations
                'recommendations': self._generate_recommendations(overall_scores)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating evaluation report: {str(e)}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, scores: List[float]) -> List[str]:
        """Generate recommendations based on evaluation scores."""
        recommendations = []
        
        if not scores:
            return ["No evaluation data available for recommendations"]
        
        avg_score = np.mean(scores)
        
        if avg_score < 0.6:
            recommendations.append("Overall performance is below acceptable threshold")
            recommendations.append("Review and improve core algorithms")
        
        if avg_score < 0.8:
            recommendations.append("Consider enhancing accuracy metrics")
            recommendations.append("Improve data quality and preprocessing")
        
        if np.std(scores) > 0.2:
            recommendations.append("High variance in performance - investigate consistency issues")
        
        if avg_score >= 0.9:
            recommendations.append("Excellent performance - consider optimization for efficiency")
        
        return recommendations
