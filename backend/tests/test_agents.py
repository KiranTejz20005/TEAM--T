"""
Tests for multi-agent system functionality.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.services.agent_system import AgentSystem
from app.services.rag_service import RAGService
from app.services.financial_analyzer import FinancialAnalyzer


class TestAgentSystem:
    """Test multi-agent system functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.agent_system = AgentSystem()
    
    def test_agent_system_initialization(self):
        """Test agent system initialization."""
        assert hasattr(self.agent_system, 'planning_agent')
        assert hasattr(self.agent_system, 'document_analyst')
        assert hasattr(self.agent_system, 'calculator_agent')
        assert hasattr(self.agent_system, 'synthesis_agent')
        
        # Check agent configurations
        assert self.agent_system.planning_agent['name'] == 'Planning Agent'
        assert self.agent_system.document_analyst['name'] == 'Document Analyst'
        assert self.agent_system.calculator_agent['name'] == 'Calculator Agent'
        assert self.agent_system.synthesis_agent['name'] == 'Synthesis Agent'
    
    def test_create_planning_agent(self):
        """Test planning agent creation."""
        planning_agent = self.agent_system._create_planning_agent()
        
        assert planning_agent['name'] == 'Planning Agent'
        assert 'system_prompt' in planning_agent
        assert 'model' in planning_agent
        assert 'financial' in planning_agent['system_prompt'].lower()
    
    def test_create_document_analyst(self):
        """Test document analyst creation."""
        document_analyst = self.agent_system._create_document_analyst()
        
        assert document_analyst['name'] == 'Document Analyst'
        assert 'system_prompt' in document_analyst
        assert 'model' in document_analyst
        assert 'extract' in document_analyst['system_prompt'].lower()
    
    def test_create_calculator_agent(self):
        """Test calculator agent creation."""
        calculator_agent = self.agent_system._create_calculator_agent()
        
        assert calculator_agent['name'] == 'Calculator Agent'
        assert 'system_prompt' in calculator_agent
        assert 'model' in calculator_agent
        assert 'calculation' in calculator_agent['system_prompt'].lower()
    
    def test_create_synthesis_agent(self):
        """Test synthesis agent creation."""
        synthesis_agent = self.agent_system._create_synthesis_agent()
        
        assert synthesis_agent['name'] == 'Synthesis Agent'
        assert 'system_prompt' in synthesis_agent
        assert 'model' in synthesis_agent
        assert 'synthes' in synthesis_agent['system_prompt'].lower()
    
    @pytest.mark.asyncio
    async def test_process_query_success(self):
        """Test successful query processing."""
        # Mock the agent execution methods
        with patch.object(self.agent_system, '_execute_planning_agent') as mock_planning, \
             patch.object(self.agent_system, '_execute_document_analyst') as mock_analyst, \
             patch.object(self.agent_system, '_execute_calculator_agent') as mock_calculator, \
             patch.object(self.agent_system, '_execute_synthesis_agent') as mock_synthesis:
            
            # Setup mock returns
            mock_planning.return_value = {
                'agent': 'Planning Agent',
                'result': 'Plan to analyze revenue data',
                'status': 'completed'
            }
            mock_analyst.return_value = {
                'agent': 'Document Analyst',
                'result': 'Extracted revenue: $1,000,000',
                'status': 'completed'
            }
            mock_calculator.return_value = {
                'agent': 'Calculator Agent',
                'result': 'Calculated ratios and margins',
                'status': 'completed'
            }
            mock_synthesis.return_value = {
                'agent': 'Synthesis Agent',
                'response': 'Based on the analysis, revenue is $1,000,000 with strong growth',
                'confidence_score': 0.9,
                'citations': [],
                'status': 'completed'
            }
            
            # Test query processing
            result = await self.agent_system.process_query(
                query="What is the revenue trend?",
                context="Revenue data: $1,000,000",
                session_id=1,
                document_id=1
            )
            
            # Verify result structure
            assert 'response' in result
            assert 'confidence_score' in result
            assert 'citations' in result
            assert 'model_used' in result
            assert 'agent_workflow' in result
            
            # Verify agent workflow
            workflow = result['agent_workflow']
            assert 'planning' in workflow
            assert 'analysis' in workflow
            assert 'calculation' in workflow
            assert 'synthesis' in workflow
    
    @pytest.mark.asyncio
    async def test_process_query_error(self):
        """Test query processing with error."""
        # Mock agent execution to raise exception
        with patch.object(self.agent_system, '_execute_planning_agent') as mock_planning:
            mock_planning.side_effect = Exception("Planning agent failed")
            
            result = await self.agent_system.process_query(
                query="What is the revenue?",
                context="",
                session_id=1,
                document_id=1
            )
            
            # Verify error handling
            assert 'error' in result
            assert 'Planning agent failed' in result['response']
            assert result['confidence_score'] == 0.0
    
    @pytest.mark.asyncio
    async def test_execute_planning_agent(self):
        """Test planning agent execution."""
        with patch.object(self.agent_system.llm, 'agenerate') as mock_generate:
            # Mock LLM response
            mock_response = Mock()
            mock_response.generations = [[Mock()]]
            mock_response.generations[0][0].text = "Plan: Analyze revenue data and calculate trends"
            mock_generate.return_value = mock_response
            
            result = await self.agent_system._execute_planning_agent(
                query="What is the revenue trend?",
                context="Revenue data available"
            )
            
            assert result['agent'] == 'Planning Agent'
            assert 'result' in result
            assert result['status'] == 'completed'
    
    @pytest.mark.asyncio
    async def test_execute_document_analyst(self):
        """Test document analyst execution."""
        with patch.object(self.agent_system.llm, 'agenerate') as mock_generate:
            # Mock LLM response
            mock_response = Mock()
            mock_response.generations = [[Mock()]]
            mock_response.generations[0][0].text = "Extracted: Revenue $1,000,000, Expenses $800,000"
            mock_generate.return_value = mock_response
            
            result = await self.agent_system._execute_document_analyst(
                query="Extract financial data",
                context="Document content",
                planning_result={'result': 'Plan to extract data'}
            )
            
            assert result['agent'] == 'Document Analyst'
            assert 'result' in result
            assert result['status'] == 'completed'
    
    @pytest.mark.asyncio
    async def test_execute_calculator_agent(self):
        """Test calculator agent execution."""
        with patch.object(self.agent_system.llm, 'agenerate') as mock_generate:
            # Mock LLM response
            mock_response = Mock()
            mock_response.generations = [[Mock()]]
            mock_response.generations[0][0].text = "Calculated: Current Ratio = 2.5, Net Margin = 20%"
            mock_generate.return_value = mock_response
            
            result = await self.agent_system._execute_calculator_agent(
                query="Calculate financial ratios",
                analysis_result={'result': 'Revenue: $1,000,000'},
                planning_result={'result': 'Plan to calculate ratios'}
            )
            
            assert result['agent'] == 'Calculator Agent'
            assert 'result' in result
            assert result['status'] == 'completed'
    
    @pytest.mark.asyncio
    async def test_execute_synthesis_agent(self):
        """Test synthesis agent execution."""
        with patch.object(self.agent_system.llm, 'agenerate') as mock_generate:
            # Mock LLM response
            mock_response = Mock()
            mock_response.generations = [[Mock()]]
            mock_response.generations[0][0].text = "Comprehensive analysis shows strong financial performance"
            mock_generate.return_value = mock_response
            
            result = await self.agent_system._execute_synthesis_agent(
                query="Synthesize all insights",
                planning_result={'result': 'Planning complete'},
                document_analysis={'result': 'Data extracted'},
                calculation_result={'result': 'Ratios calculated'}
            )
            
            assert result['agent'] == 'Synthesis Agent'
            assert 'response' in result
            assert result['status'] == 'completed'
    
    @pytest.mark.asyncio
    async def test_get_agent_status(self):
        """Test agent status retrieval."""
        status = await self.agent_system.get_agent_status()
        
        assert 'planning_agent' in status
        assert 'document_analyst' in status
        assert 'calculator_agent' in status
        assert 'synthesis_agent' in status
        
        for agent_name, agent_info in status.items():
            assert 'name' in agent_info
            assert 'status' in agent_info
            assert agent_info['status'] == 'active'


class TestRAGService:
    """Test RAG service functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        # Mock ChromaDB to avoid actual database operations in tests
        with patch('app.services.rag_service.chromadb.PersistentClient'):
            with patch('app.services.rag_service.SentenceTransformer'):
                self.rag_service = RAGService()
    
    def test_rag_service_initialization(self):
        """Test RAG service initialization."""
        assert hasattr(self.rag_service, 'client')
        assert hasattr(self.rag_service, 'embedding_model')
        assert hasattr(self.rag_service, 'collection')
    
    def test_chunk_text(self):
        """Test text chunking functionality."""
        # Test short text
        short_text = "This is a short text."
        chunks = self.rag_service._chunk_text(short_text)
        assert len(chunks) == 1
        assert chunks[0] == short_text
        
        # Test long text
        long_text = "This is a very long text. " * 100  # Create long text
        chunks = self.rag_service._chunk_text(long_text, chunk_size=100, overlap=20)
        assert len(chunks) > 1
        
        # Verify chunks don't exceed size limit
        for chunk in chunks:
            assert len(chunk) <= 100
    
    @pytest.mark.asyncio
    async def test_index_document(self):
        """Test document indexing."""
        with patch.object(self.rag_service.collection, 'add') as mock_add:
            result = await self.rag_service.index_document(
                document_id=1,
                content="Sample financial content with revenue data",
                metadata={"type": "financial_statement"}
            )
            
            assert result is True
            mock_add.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_retrieve_context(self):
        """Test context retrieval."""
        with patch.object(self.rag_service.collection, 'query') as mock_query:
            # Mock query response
            mock_query.return_value = {
                'documents': [['Revenue was $1,000,000', 'Expenses were $800,000']],
                'metadatas': [[{'document_id': 1, 'chunk_index': 0}, {'document_id': 1, 'chunk_index': 1}]],
                'distances': [[0.1, 0.2]]
            }
            
            context = await self.rag_service.retrieve_context(
                query="What is the revenue?",
                document_id=1,
                top_k=2
            )
            
            assert isinstance(context, str)
            assert "Revenue was $1,000,000" in context
            assert "Expenses were $800,000" in context
    
    @pytest.mark.asyncio
    async def test_retrieve_with_citations(self):
        """Test context retrieval with citations."""
        with patch.object(self.rag_service.collection, 'query') as mock_query:
            # Mock query response
            mock_query.return_value = {
                'documents': [['Revenue was $1,000,000']],
                'metadatas': [[{'document_id': 1, 'chunk_index': 0}]],
                'distances': [[0.1]]
            }
            
            result = await self.rag_service.retrieve_with_citations(
                query="What is the revenue?",
                document_id=1,
                top_k=1
            )
            
            assert 'context' in result
            assert 'citations' in result
            assert 'total_results' in result
            assert 'query' in result
            
            assert len(result['citations']) == 1
            assert result['citations'][0]['document_id'] == 1
            assert result['citations'][0]['relevance_score'] == 0.9  # 1 - 0.1
    
    @pytest.mark.asyncio
    async def test_search_similar_documents(self):
        """Test similar document search."""
        with patch.object(self.rag_service.collection, 'query') as mock_query:
            # Mock query response
            mock_query.return_value = {
                'documents': [['Revenue data', 'Financial statements']],
                'metadatas': [[{'document_id': 1, 'chunk_index': 0}, {'document_id': 2, 'chunk_index': 0}]],
                'distances': [[0.1, 0.3]]
            }
            
            results = await self.rag_service.search_similar_documents(
                query="financial data",
                top_k=2
            )
            
            assert len(results) == 2
            assert results[0]['document_id'] == 1
            assert results[0]['max_relevance'] == 0.9  # 1 - 0.1
            assert results[1]['document_id'] == 2
            assert results[1]['max_relevance'] == 0.7  # 1 - 0.3
    
    @pytest.mark.asyncio
    async def test_delete_document(self):
        """Test document deletion."""
        with patch.object(self.rag_service.collection, 'get') as mock_get, \
             patch.object(self.rag_service.collection, 'delete') as mock_delete:
            
            # Mock get response
            mock_get.return_value = {
                'ids': ['doc_1_chunk_0', 'doc_1_chunk_1']
            }
            
            result = await self.rag_service.delete_document(document_id=1)
            
            assert result is True
            mock_delete.assert_called_once_with(ids=['doc_1_chunk_0', 'doc_1_chunk_1'])
    
    def test_get_collection_stats(self):
        """Test collection statistics."""
        with patch.object(self.rag_service.collection, 'count') as mock_count:
            mock_count.return_value = 100
            
            stats = self.rag_service.get_collection_stats()
            
            assert 'total_chunks' in stats
            assert 'collection_name' in stats
            assert 'embedding_model' in stats
            assert stats['total_chunks'] == 100


class TestFinancialAnalyzer:
    """Test financial analyzer functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.analyzer = FinancialAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test financial analyzer initialization."""
        assert hasattr(self.analyzer, 'ratio_calculators')
        assert len(self.analyzer.ratio_calculators) == 5
        
        expected_calculators = ['liquidity', 'profitability', 'leverage', 'efficiency', 'valuation']
        for calculator in expected_calculators:
            assert calculator in self.analyzer.ratio_calculators
    
    @pytest.mark.asyncio
    async def test_calculate_ratios(self):
        """Test ratio calculation."""
        result = await self.analyzer.calculate_ratios(
            document_id=1,
            ratio_types=['liquidity', 'profitability'],
            period='current'
        )
        
        assert 'ratios' in result
        assert 'confidence_score' in result
        assert 'calculation_date' in result
        assert 'document_id' in result
        
        assert 'liquidity' in result['ratios']
        assert 'profitability' in result['ratios']
    
    @pytest.mark.asyncio
    async def test_generate_forecast(self):
        """Test forecast generation."""
        result = await self.analyzer.generate_forecast(
            document_id=1,
            metric='revenue',
            periods=12,
            method='prophet'
        )
        
        assert 'metric' in result
        assert 'forecast_data' in result
        assert 'confidence_intervals' in result
        assert 'method' in result
        assert 'periods' in result
        assert 'document_id' in result
        
        assert result['metric'] == 'revenue'
        assert result['method'] == 'prophet'
        assert result['periods'] == 12
    
    @pytest.mark.asyncio
    async def test_analyze_trends(self):
        """Test trend analysis."""
        result = await self.analyzer.analyze_trends(
            document_id=1,
            metrics=['revenue', 'expenses'],
            time_period='24_months'
        )
        
        assert 'trends' in result
        assert 'analysis_date' in result
        assert 'time_period' in result
        assert 'confidence_score' in result
        assert 'document_id' in result
        
        assert 'revenue' in result['trends']
        assert 'expenses' in result['trends']
        
        # Check trend structure
        revenue_trend = result['trends']['revenue']
        assert 'trend_direction' in revenue_trend
        assert 'trend_strength' in revenue_trend
        assert 'slope' in revenue_trend
        assert 'r_squared' in revenue_trend
        assert 'forecast_next_period' in revenue_trend
        assert 'volatility' in revenue_trend


if __name__ == "__main__":
    pytest.main([__file__])
