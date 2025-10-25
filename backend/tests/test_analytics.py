"""
Tests for financial analytics functionality.
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.services.financial_analyzer import FinancialAnalyzer
from app.services.guardrails import GuardrailsService
from app.services.evaluator import EvaluatorService


class TestFinancialAnalyzer:
    """Test financial analyzer functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.analyzer = FinancialAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test financial analyzer initialization."""
        assert hasattr(self.analyzer, 'ratio_calculators')
        assert 'liquidity' in self.analyzer.ratio_calculators
        assert 'profitability' in self.analyzer.ratio_calculators
        assert 'leverage' in self.analyzer.ratio_calculators
        assert 'efficiency' in self.analyzer.ratio_calculators
        assert 'valuation' in self.analyzer.ratio_calculators
    
    def test_calculate_liquidity_ratios(self):
        """Test liquidity ratio calculations."""
        sample_data = {
            "current_assets": 500000,
            "current_liabilities": 200000,
            "inventory": 100000,
            "cash": 200000
        }
        
        ratios = self.analyzer._calculate_liquidity_ratios(sample_data)
        
        assert "current_ratio" in ratios
        assert "quick_ratio" in ratios
        assert "cash_ratio" in ratios
        
        # Test calculations
        expected_current_ratio = 500000 / 200000  # 2.5
        assert abs(ratios["current_ratio"] - expected_current_ratio) < 0.01
        
        expected_quick_ratio = (500000 - 100000) / 200000  # 2.0
        assert abs(ratios["quick_ratio"] - expected_quick_ratio) < 0.01
        
        expected_cash_ratio = 200000 / 200000  # 1.0
        assert abs(ratios["cash_ratio"] - expected_cash_ratio) < 0.01
    
    def test_calculate_profitability_ratios(self):
        """Test profitability ratio calculations."""
        sample_data = {
            "revenue": 1000000,
            "gross_profit": 400000,
            "net_income": 150000,
            "total_assets": 2000000,
            "shareholders_equity": 1200000
        }
        
        ratios = self.analyzer._calculate_profitability_ratios(sample_data)
        
        assert "gross_margin" in ratios
        assert "net_margin" in ratios
        assert "return_on_assets" in ratios
        assert "return_on_equity" in ratios
        
        # Test calculations
        expected_gross_margin = 400000 / 1000000  # 0.4
        assert abs(ratios["gross_margin"] - expected_gross_margin) < 0.01
        
        expected_net_margin = 150000 / 1000000  # 0.15
        assert abs(ratios["net_margin"] - expected_net_margin) < 0.01
    
    def test_calculate_leverage_ratios(self):
        """Test leverage ratio calculations."""
        sample_data = {
            "total_debt": 800000,
            "total_assets": 2000000,
            "shareholders_equity": 1200000,
            "ebit": 200000,
            "interest_expense": 50000
        }
        
        ratios = self.analyzer._calculate_leverage_ratios(sample_data)
        
        assert "debt_ratio" in ratios
        assert "debt_to_equity" in ratios
        assert "interest_coverage" in ratios
        
        # Test calculations
        expected_debt_ratio = 800000 / 2000000  # 0.4
        assert abs(ratios["debt_ratio"] - expected_debt_ratio) < 0.01
        
        expected_debt_to_equity = 800000 / 1200000  # 0.67
        assert abs(ratios["debt_to_equity"] - expected_debt_to_equity) < 0.01
    
    def test_calculate_efficiency_ratios(self):
        """Test efficiency ratio calculations."""
        sample_data = {
            "revenue": 1000000,
            "total_assets": 2000000,
            "inventory": 100000,
            "accounts_receivable": 150000,
            "cost_of_goods_sold": 600000
        }
        
        ratios = self.analyzer._calculate_efficiency_ratios(sample_data)
        
        assert "asset_turnover" in ratios
        assert "inventory_turnover" in ratios
        assert "receivables_turnover" in ratios
        
        # Test calculations
        expected_asset_turnover = 1000000 / 2000000  # 0.5
        assert abs(ratios["asset_turnover"] - expected_asset_turnover) < 0.01
    
    def test_calculate_valuation_ratios(self):
        """Test valuation ratio calculations."""
        sample_data = {
            "market_cap": 5000000,
            "net_income": 150000,
            "book_value": 1200000,
            "ebitda": 250000,
            "enterprise_value": 6000000
        }
        
        ratios = self.analyzer._calculate_valuation_ratios(sample_data)
        
        assert "price_to_earnings" in ratios
        assert "price_to_book" in ratios
        assert "ev_to_ebitda" in ratios
        
        # Test calculations
        expected_pe = 5000000 / 150000  # 33.33
        assert abs(ratios["price_to_earnings"] - expected_pe) < 0.01
    
    def test_get_sample_financial_data(self):
        """Test sample financial data generation."""
        data = self.analyzer._get_sample_financial_data()
        
        assert "revenue" in data
        assert "gross_profit" in data
        assert "net_income" in data
        assert "total_assets" in data
        assert "current_assets" in data
        assert "current_liabilities" in data
        
        # Check that values are reasonable
        assert data["revenue"] > 0
        assert data["total_assets"] > 0
        assert data["current_assets"] > 0
    
    def test_generate_sample_time_series(self):
        """Test time series data generation."""
        data = self.analyzer._generate_sample_time_series("revenue", 12)
        
        assert len(data) == 12
        assert "date" in data.columns
        assert "value" in data.columns
        
        # Check that dates are properly formatted
        assert isinstance(data["date"].iloc[0], datetime)
        
        # Check that values are reasonable
        assert data["value"].min() > 0
        assert data["value"].max() > data["value"].min()
    
    def test_calculate_trend(self):
        """Test trend calculation."""
        # Create sample time series data
        dates = [datetime.now() - timedelta(days=30*i) for i in range(12, 0, -1)]
        values = [100 + i*10 for i in range(12)]  # Increasing trend
        
        data = pd.DataFrame({"date": dates, "value": values})
        
        trend = self.analyzer._calculate_trend(data)
        
        assert "direction" in trend
        assert "strength" in trend
        assert "slope" in trend
        assert "r_squared" in trend
        assert "forecast" in trend
        
        # Check that trend is detected correctly
        assert trend["direction"] == "increasing"
        assert trend["slope"] > 0
        assert trend["r_squared"] > 0.5  # Should have good correlation


class TestGuardrailsService:
    """Test guardrails service functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.guardrails = GuardrailsService()
    
    def test_guardrails_initialization(self):
        """Test guardrails service initialization."""
        assert hasattr(self.guardrails, 'financial_keywords')
        assert hasattr(self.guardrails, 'sensitive_patterns')
        assert len(self.guardrails.financial_keywords) > 0
        assert len(self.guardrails.sensitive_patterns) > 0
    
    def test_is_financially_relevant(self):
        """Test financial relevance checking."""
        # Relevant queries
        relevant_queries = [
            "What is the revenue for this quarter?",
            "Calculate the profit margin",
            "Show me the balance sheet",
            "What are the current assets?"
        ]
        
        for query in relevant_queries:
            assert self.guardrails._is_financially_relevant(query)
        
        # Non-relevant queries
        non_relevant_queries = [
            "What's the weather like?",
            "Tell me a joke",
            "How do I cook pasta?"
        ]
        
        for query in non_relevant_queries:
            assert not self.guardrails._is_financially_relevant(query)
    
    def test_contains_sensitive_patterns(self):
        """Test sensitive pattern detection."""
        # Test credit card pattern
        assert self.guardrails._contains_sensitive_patterns("1234-5678-9012-3456")
        
        # Test SSN pattern
        assert self.guardrails._contains_sensitive_patterns("123-45-6789")
        
        # Test account number pattern
        assert self.guardrails._contains_sensitive_patterns("AB123456")
        
        # Test long numeric sequence
        assert self.guardrails._contains_sensitive_patterns("123456789012345")
        
        # Test non-sensitive text
        assert not self.guardrails._contains_sensitive_patterns("This is normal financial text")
    
    def test_contains_malicious_content(self):
        """Test malicious content detection."""
        # Test script injection
        assert self.guardrails._contains_malicious_content("<script>alert('xss')</script>")
        
        # Test JavaScript
        assert self.guardrails._contains_malicious_content("javascript:alert('xss')")
        
        # Test VBScript
        assert self.guardrails._contains_malicious_content("vbscript:msgbox('xss')")
        
        # Test data URI
        assert self.guardrails._contains_malicious_content("data:text/html,<script>alert('xss')</script>")
        
        # Test normal content
        assert not self.guardrails._contains_malicious_content("This is normal financial analysis")
    
    def test_contains_suspicious_patterns(self):
        """Test suspicious filename pattern detection."""
        # Test executable files
        assert self.guardrails._contains_suspicious_patterns("document.exe")
        assert self.guardrails._contains_suspicious_patterns("script.bat")
        assert self.guardrails._contains_suspicious_patterns("malware.scr")
        
        # Test JavaScript in filename
        assert self.guardrails._contains_suspicious_patterns("filejavascript:alert('xss')")
        
        # Test normal filenames
        assert not self.guardrails._contains_suspicious_patterns("financial_report.pdf")
        assert not self.guardrails._contains_suspicious_patterns("balance_sheet.xlsx")
    
    @pytest.mark.asyncio
    async def test_validate_chat_query(self):
        """Test chat query validation."""
        # Valid query
        result = await self.guardrails._validate_chat_query("What is the revenue for Q1?")
        assert result["is_valid"] is True
        assert result["confidence_score"] > 0.5
        
        # Query with sensitive information
        result = await self.guardrails._validate_chat_query("My SSN is 123-45-6789")
        assert result["is_valid"] is False
        assert result["confidence_score"] == 0.0
        
        # Non-financial query
        result = await self.guardrails._validate_chat_query("What's the weather like?")
        assert result["is_valid"] is True
        assert result["confidence_score"] < 0.8  # Lower confidence for non-financial
    
    @pytest.mark.asyncio
    async def test_validate_financial_data(self):
        """Test financial data validation."""
        # Valid data
        valid_data = {
            "revenue": 1000000,
            "expenses": 800000,
            "assets": 2000000,
            "liabilities": 1000000
        }
        
        result = await self.guardrails._validate_financial_data(valid_data)
        assert result["is_valid"] is True
        assert result["confidence_score"] > 0.8
        
        # Data with missing fields
        incomplete_data = {"revenue": 1000000}
        result = await self.guardrails._validate_financial_data(incomplete_data)
        assert result["is_valid"] is True  # Missing fields are warnings, not errors
        assert result["confidence_score"] < 1.0
        
        # Data with negative revenue
        invalid_data = {
            "revenue": -1000000,
            "expenses": 800000,
            "assets": 2000000
        }
        result = await self.guardrails._validate_financial_data(invalid_data)
        assert result["is_valid"] is True  # Negative values are warnings
        assert result["confidence_score"] < 1.0


class TestEvaluatorService:
    """Test evaluator service functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.evaluator = EvaluatorService()
    
    def test_evaluator_initialization(self):
        """Test evaluator service initialization."""
        assert hasattr(self.evaluator, 'metrics_history')
        assert isinstance(self.evaluator.metrics_history, list)
    
    def test_calculate_text_accuracy(self):
        """Test text accuracy calculation."""
        extracted_text = "Revenue was $1,000,000 and expenses were $800,000"
        ground_truth_text = "Revenue was $1,000,000 and expenses were $800,000"
        
        accuracy = self.evaluator._calculate_text_accuracy(extracted_text, ground_truth_text)
        assert accuracy == 1.0  # Perfect match
        
        # Test partial match
        extracted_text = "Revenue was $1,000,000"
        ground_truth_text = "Revenue was $1,000,000 and expenses were $800,000"
        
        accuracy = self.evaluator._calculate_text_accuracy(extracted_text, ground_truth_text)
        assert 0 < accuracy < 1.0  # Partial match
        
        # Test no match
        extracted_text = "Completely different text"
        ground_truth_text = "Revenue was $1,000,000"
        
        accuracy = self.evaluator._calculate_text_accuracy(extracted_text, ground_truth_text)
        assert accuracy == 0.0  # No match
    
    def test_calculate_relevance_score(self):
        """Test relevance score calculation."""
        query = "What is the revenue?"
        retrieved_context = "The revenue for Q1 was $1,000,000"
        ground_truth_context = "Revenue for Q1 was $1,000,000 and expenses were $800,000"
        
        score = self.evaluator._calculate_relevance_score(query, retrieved_context, ground_truth_context)
        assert 0 <= score <= 1.0
        
        # Test with irrelevant context
        irrelevant_context = "The weather is sunny today"
        score = self.evaluator._calculate_relevance_score(query, irrelevant_context, ground_truth_context)
        assert score < 0.5
    
    def test_calculate_precision_recall(self):
        """Test precision and recall calculation."""
        retrieved_context = "Revenue was $1,000,000 and profit was $200,000"
        ground_truth_context = "Revenue was $1,000,000 and expenses were $800,000"
        
        precision, recall = self.evaluator._calculate_precision_recall(retrieved_context, ground_truth_context)
        
        assert 0 <= precision <= 1.0
        assert 0 <= recall <= 1.0
        
        # Test perfect match
        precision, recall = self.evaluator._calculate_precision_recall(
            ground_truth_context, ground_truth_context
        )
        assert precision == 1.0
        assert recall == 1.0
    
    def test_assess_response_quality(self):
        """Test response quality assessment."""
        # High quality response
        good_response = """
        Based on the financial data provided, I can calculate the following ratios:
        1. Current Ratio: 2.5 (Current Assets / Current Liabilities)
        2. Gross Margin: 40% (Gross Profit / Revenue)
        3. Net Margin: 15% (Net Income / Revenue)
        
        These ratios indicate strong liquidity and profitability.
        """
        
        quality = self.evaluator._assess_response_quality(good_response)
        assert quality > 0.7
        
        # Low quality response
        poor_response = "Yes"
        quality = self.evaluator._assess_response_quality(poor_response)
        assert quality < 0.5
        
        # Empty response
        empty_response = ""
        quality = self.evaluator._assess_response_quality(empty_response)
        assert quality == 0.0
    
    @pytest.mark.asyncio
    async def test_evaluate_financial_calculations(self):
        """Test financial calculation evaluation."""
        calculated_values = {
            "current_ratio": 2.5,
            "gross_margin": 0.4,
            "net_margin": 0.15
        }
        
        ground_truth_values = {
            "current_ratio": 2.5,
            "gross_margin": 0.4,
            "net_margin": 0.15
        }
        
        result = await self.evaluator.evaluate_financial_calculations(
            calculated_values, ground_truth_values
        )
        
        assert result["evaluation_type"] == "financial_calculations"
        assert result["overall_score"] == 1.0  # Perfect match
        assert result["metrics"]["average_accuracy"] == 1.0
        assert result["metrics"]["perfect_matches"] == 3
        
        # Test with some errors
        calculated_values_with_errors = {
            "current_ratio": 2.0,  # Error
            "gross_margin": 0.4,   # Correct
            "net_margin": 0.12    # Error
        }
        
        result = await self.evaluator.evaluate_financial_calculations(
            calculated_values_with_errors, ground_truth_values
        )
        
        assert result["overall_score"] < 1.0
        assert result["metrics"]["perfect_matches"] == 1
    
    @pytest.mark.asyncio
    async def test_evaluate_system_performance(self):
        """Test system performance evaluation."""
        start_time = time.time()
        time.sleep(0.1)  # Simulate processing time
        end_time = time.time()
        
        result = await self.evaluator.evaluate_system_performance(
            start_time, end_time, "document_processing"
        )
        
        assert result["evaluation_type"] == "system_performance"
        assert result["metrics"]["response_time"] > 0
        assert result["metrics"]["operation_type"] == "document_processing"
        assert "performance_score" in result["metrics"]
        assert "performance_category" in result["metrics"]


if __name__ == "__main__":
    pytest.main([__file__])
