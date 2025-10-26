"""
Test suite for enhanced guardrails and evaluation system.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime
import json

from app.services.enhanced_guardrails import (
    EnhancedGuardrailsService, 
    InputGuardrails, 
    OutputGuardrails,
    FinancialDomain,
    SecurityLevel
)
from app.services.enhanced_evaluator import (
    EnhancedEvaluator,
    EvaluationMetrics,
    PerformanceMonitor,
    FinancialAccuracyEvaluator
)
from app.services.sec_dataset_processor import SECDatasetProcessor
from app.services.financial_datasets import FinancialDatasetsManager

class TestEnhancedGuardrails:
    """Test enhanced guardrails functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.guardrails_service = EnhancedGuardrailsService()
        self.input_guardrails = InputGuardrails()
        self.output_guardrails = OutputGuardrails()
    
    def test_input_validation_file_upload(self):
        """Test file upload validation."""
        # Test valid file
        is_valid, message, metadata = self.input_guardrails.validate_file_upload(
            "test.pdf", 1024, ".pdf"
        )
        assert is_valid
        assert "File validation passed" in message
        
        # Test invalid file size
        is_valid, message, metadata = self.input_guardrails.validate_file_upload(
            "test.pdf", 100 * 1024 * 1024, ".pdf"  # 100MB
        )
        assert not is_valid
        assert "exceeds maximum allowed size" in message
        
        # Test invalid file type
        is_valid, message, metadata = self.input_guardrails.validate_file_upload(
            "test.exe", 1024, ".exe"
        )
        assert not is_valid
        assert "not allowed" in message
    
    def test_input_validation_query(self):
        """Test query validation."""
        # Test valid financial query
        is_valid, message, metadata = self.input_guardrails.validate_query(
            "What is the current ratio for Apple Inc?"
        )
        assert is_valid
        assert "Query validation passed" in message
        assert metadata['financial_relevance_score'] > 0
        
        # Test non-financial query
        is_valid, message, metadata = self.input_guardrails.validate_query(
            "What is the weather today?"
        )
        assert not is_valid
        assert "not financially relevant" in message
        
        # Test malicious query
        is_valid, message, metadata = self.input_guardrails.validate_query(
            "<script>alert('xss')</script>"
        )
        assert not is_valid
        assert "malicious content" in message
    
    def test_output_validation(self):
        """Test output validation."""
        # Test valid response
        is_valid, status, response, metadata = self.output_guardrails.validate_response(
            "Based on the financial data, the current ratio is 2.5.", 0.8
        )
        assert is_valid
        assert "Response validation passed" in status
        
        # Test low confidence response
        is_valid, status, response, metadata = self.output_guardrails.validate_response(
            "I'm not sure about this.", 0.2
        )
        assert not is_valid
        assert "Low confidence response" in status
        
        # Test response with disclaimers
        is_valid, status, response, metadata = self.output_guardrails.validate_response(
            "I recommend buying this stock.", 0.8, "investment"
        )
        assert is_valid
        assert "Disclaimer:" in response
    
    def test_guardrails_service_integration(self):
        """Test guardrails service integration."""
        # Test input validation
        result = self.guardrails_service.validate_input(
            query="What is the revenue trend for Microsoft?",
            domain=FinancialDomain.CORPORATE
        )
        assert result['valid']
        assert result['security_level'] == SecurityLevel.LOW
        
        # Test output validation
        result = self.guardrails_service.validate_output(
            "Microsoft's revenue has been growing steadily over the past 5 years.",
            0.9
        )
        assert result['valid']
        assert 'quality_metrics' in result

class TestEnhancedEvaluator:
    """Test enhanced evaluator functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.evaluator = EnhancedEvaluator()
        self.metrics = EvaluationMetrics()
        self.performance_monitor = PerformanceMonitor()
        self.financial_evaluator = FinancialAccuracyEvaluator()
    
    @pytest.mark.asyncio
    async def test_accuracy_metrics_calculation(self):
        """Test accuracy metrics calculation."""
        predictions = [1, 0, 1, 0, 1]
        ground_truth = [1, 0, 1, 1, 0]
        
        metrics = await self.metrics.calculate_accuracy_metrics(
            predictions, ground_truth, 'classification'
        )
        
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1_score' in metrics
        assert 0 <= metrics['accuracy'] <= 1
    
    @pytest.mark.asyncio
    async def test_rag_metrics_calculation(self):
        """Test RAG metrics calculation."""
        retrieved_docs = [
            {'id': 'doc1', 'content': 'Financial data'},
            {'id': 'doc2', 'content': 'Market analysis'},
            {'id': 'doc3', 'content': 'Economic indicators'}
        ]
        relevant_docs = [
            {'id': 'doc1', 'content': 'Financial data'},
            {'id': 'doc2', 'content': 'Market analysis'}
        ]
        
        metrics = await self.metrics.calculate_rag_metrics(retrieved_docs, relevant_docs)
        
        assert 'precision@1' in metrics
        assert 'recall@1' in metrics
        assert 'f1@1' in metrics
        assert 0 <= metrics['precision@1'] <= 1
    
    @pytest.mark.asyncio
    async def test_response_quality_metrics(self):
        """Test response quality metrics calculation."""
        responses = [
            {
                'content': 'Based on the financial analysis, the company shows strong revenue growth.',
                'metadata': {'source': 'financial_report.pdf'}
            },
            {
                'content': 'The current ratio indicates good liquidity position.',
                'metadata': {'source': 'balance_sheet.xlsx'}
            }
        ]
        
        metrics = await self.metrics.calculate_response_quality_metrics(responses)
        
        assert 'average_length' in metrics
        assert 'completeness_score' in metrics
        assert 'clarity_score' in metrics
        assert 'relevance_score' in metrics
        assert 'citation_score' in metrics
    
    @pytest.mark.asyncio
    async def test_financial_ratio_evaluation(self):
        """Test financial ratio evaluation."""
        calculated_ratios = {
            'current_ratio': 2.5,
            'debt_to_equity': 0.6,
            'roe': 0.15
        }
        expected_ratios = {
            'current_ratio': 2.4,
            'debt_to_equity': 0.65,
            'roe': 0.14
        }
        
        result = await self.financial_evaluator.evaluate_financial_ratios(
            calculated_ratios, expected_ratios
        )
        
        assert 'total_ratios' in result
        assert 'accurate_ratios' in result
        assert 'accuracy_percentage' in result
        assert result['total_ratios'] == 3
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self):
        """Test performance monitoring."""
        # Record some latency data
        await self.performance_monitor.record_latency('document_processing', 150.5)
        await self.performance_monitor.record_latency('document_processing', 200.3)
        await self.performance_monitor.record_latency('chat_response', 300.1)
        
        # Get performance summary
        summary = await self.performance_monitor.get_performance_summary()
        
        assert 'document_processing' in summary
        assert 'chat_response' in summary
        assert 'count' in summary['document_processing']
        assert 'avg_latency_ms' in summary['document_processing']
    
    @pytest.mark.asyncio
    async def test_comprehensive_evaluation(self):
        """Test comprehensive evaluation."""
        test_data = {
            'predictions': [1, 0, 1, 0, 1],
            'ground_truth': [1, 0, 1, 1, 0],
            'metric_type': 'classification',
            'retrieved_docs': [{'id': 'doc1'}, {'id': 'doc2'}],
            'relevant_docs': [{'id': 'doc1'}],
            'responses': [{'content': 'Test response'}],
            'calculated_ratios': {'current_ratio': 2.5},
            'expected_ratios': {'current_ratio': 2.4}
        }
        
        result = await self.evaluator.run_comprehensive_evaluation(test_data)
        
        assert 'timestamp' in result
        assert 'metrics' in result
        assert 'overall_score' in result
        assert 0 <= result['overall_score'] <= 1

class TestSECDatasetProcessor:
    """Test SEC dataset processor."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.processor = SECDatasetProcessor()
    
    @pytest.mark.asyncio
    async def test_dataset_loading(self):
        """Test dataset loading functionality."""
        # Create mock dataframe
        mock_df = pd.DataFrame({
            'company_name': ['Apple Inc', 'Microsoft Corp'],
            'ticker': ['AAPL', 'MSFT'],
            'sector': ['Technology', 'Technology'],
            'revenue': [1000000, 2000000],
            'net_income': [100000, 200000],
            'total_assets': [5000000, 10000000]
        })
        
        with patch('pandas.read_csv', return_value=mock_df):
            result = await self.processor.load_dataset()
            
            assert 'companies' in result
            assert 'statements' in result
            assert 'ratios' in result
            assert 'trends' in result
    
    @pytest.mark.asyncio
    async def test_company_analysis(self):
        """Test company analysis functionality."""
        # Mock processed data
        self.processor.processed_data = {
            'companies': {
                'Apple Inc': {
                    'name': 'Apple Inc',
                    'ticker': 'AAPL',
                    'sector': 'Technology',
                    'statements': {},
                    'ratios': {'current_ratio': 2.5},
                    'trends': {}
                }
            }
        }
        
        result = await self.processor.get_company_analysis('Apple Inc')
        
        assert 'company_info' in result
        assert 'ratios' in result
        assert result['company_info']['name'] == 'Apple Inc'

class TestFinancialDatasetsManager:
    """Test financial datasets manager."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.manager = FinancialDatasetsManager()
    
    @pytest.mark.asyncio
    async def test_dataset_loading(self):
        """Test dataset loading."""
        # Create mock dataframe
        mock_df = pd.DataFrame({
            'company_name': ['Apple Inc', 'Microsoft Corp'],
            'revenue': [1000000, 2000000],
            'net_income': [100000, 200000]
        })
        
        with patch('pandas.read_csv', return_value=mock_df):
            result = await self.manager.load_dataset('sec_financial_statements')
            
            assert 'name' in result
            assert 'total_records' in result
            assert 'statistics' in result
            assert 'insights' in result
    
    @pytest.mark.asyncio
    async def test_dataset_summary(self):
        """Test dataset summary generation."""
        # Mock loaded dataset
        self.manager.loaded_datasets['test_dataset'] = {
            'name': 'Test Dataset',
            'source': 'Test Source',
            'description': 'Test Description',
            'total_records': 100,
            'columns': ['col1', 'col2'],
            'statistics': {},
            'insights': {},
            'processed_at': datetime.now().isoformat()
        }
        
        result = await self.manager.get_dataset_summary('test_dataset')
        
        assert 'name' in result
        assert 'total_records' in result
        assert result['name'] == 'Test Dataset'
    
    @pytest.mark.asyncio
    async def test_dataset_comparison(self):
        """Test dataset comparison."""
        # Mock multiple datasets
        self.manager.loaded_datasets = {
            'dataset1': {'columns': ['col1', 'col2'], 'name': 'Dataset 1'},
            'dataset2': {'columns': ['col1', 'col3'], 'name': 'Dataset 2'}
        }
        
        result = await self.manager.compare_datasets(['dataset1', 'dataset2'])
        
        assert 'datasets' in result
        assert 'common_columns' in result
        assert 'recommendations' in result

class TestIntegration:
    """Test integration between components."""
    
    @pytest.mark.asyncio
    async def test_guardrails_evaluation_integration(self):
        """Test integration between guardrails and evaluation."""
        guardrails = EnhancedGuardrailsService()
        evaluator = EnhancedEvaluator()
        
        # Test input validation
        input_result = guardrails.validate_input(
            query="What is the current ratio for Apple?",
            domain=FinancialDomain.CORPORATE
        )
        
        # Test output validation
        output_result = guardrails.validate_output(
            "Apple's current ratio is 2.5, indicating strong liquidity.",
            0.9
        )
        
        # Test evaluation
        test_data = {
            'predictions': [1, 0, 1],
            'ground_truth': [1, 0, 1],
            'metric_type': 'classification'
        }
        
        evaluation_result = await evaluator.run_comprehensive_evaluation(test_data)
        
        assert input_result['valid']
        assert output_result['valid']
        assert 'overall_score' in evaluation_result
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test end-to-end workflow."""
        # Initialize components
        guardrails = EnhancedGuardrailsService()
        evaluator = EnhancedEvaluator()
        sec_processor = SECDatasetProcessor()
        datasets_manager = FinancialDatasetsManager()
        
        # Simulate workflow
        # 1. Input validation
        input_result = guardrails.validate_input(
            query="Analyze Apple's financial performance",
            domain=FinancialDomain.CORPORATE
        )
        
        # 2. Process data (mock)
        with patch.object(sec_processor, 'load_dataset') as mock_load:
            mock_load.return_value = {'companies': {}, 'statements': {}, 'ratios': {}, 'trends': {}}
            processed_data = await sec_processor.load_dataset()
        
        # 3. Generate response (mock)
        response = "Apple shows strong financial performance with revenue growth of 15%."
        
        # 4. Output validation
        output_result = guardrails.validate_output(response, 0.85)
        
        # 5. Evaluation
        test_data = {
            'predictions': [1, 1, 1],
            'ground_truth': [1, 1, 1],
            'metric_type': 'classification'
        }
        evaluation_result = await evaluator.run_comprehensive_evaluation(test_data)
        
        # Assertions
        assert input_result['valid']
        assert output_result['valid']
        assert evaluation_result['overall_score'] > 0

if __name__ == "__main__":
    pytest.main([__file__])
