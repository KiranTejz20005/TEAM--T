"""
Multi-agent system for financial analysis and conversation.
"""
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType

from app.config import settings
from app.services.rag_service import RAGService
from app.services.financial_analyzer import FinancialAnalyzer


class AgentSystem:
    """Multi-agent system for financial analysis."""
    
    def __init__(self):
        """Initialize the agent system."""
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=settings.openai_api_key
        )
        
        # Initialize services
        self.rag_service = RAGService()
        self.financial_analyzer = FinancialAnalyzer()
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize specialized agents."""
        
        # Planning Agent - Breaks down complex queries
        self.planning_agent = self._create_planning_agent()
        
        # Document Analyst Agent - Extracts and interprets data
        self.document_analyst = self._create_document_analyst()
        
        # Financial Calculator Agent - Performs calculations
        self.calculator_agent = self._create_calculator_agent()
        
        # Synthesis Agent - Combines insights
        self.synthesis_agent = self._create_synthesis_agent()
    
    def _create_planning_agent(self):
        """Create planning agent for query decomposition."""
        system_prompt = """You are a Financial Planning Agent. Your role is to:
1. Analyze user queries and break them down into specific analytical tasks
2. Identify what type of financial analysis is needed
3. Determine what data sources are required
4. Create a step-by-step plan for answering the query

Focus on:
- Financial ratio calculations
- Trend analysis
- Forecasting
- Document interpretation
- Data extraction tasks

Always provide a clear, structured plan with specific steps."""
        
        return {
            "name": "Planning Agent",
            "system_prompt": system_prompt,
            "model": self.llm
        }
    
    def _create_document_analyst(self):
        """Create document analyst agent."""
        system_prompt = """You are a Financial Document Analyst. Your role is to:
1. Extract and interpret financial data from documents
2. Identify key financial metrics and KPIs
3. Understand financial statement structures
4. Provide context for financial data

Focus on:
- Income statements
- Balance sheets
- Cash flow statements
- Financial ratios
- Key performance indicators

Always cite specific data points and provide context for your interpretations."""
        
        return {
            "name": "Document Analyst",
            "system_prompt": system_prompt,
            "model": self.llm
        }
    
    def _create_calculator_agent(self):
        """Create financial calculator agent."""
        system_prompt = """You are a Financial Calculator Agent. Your role is to:
1. Perform accurate financial calculations
2. Calculate ratios, margins, and other metrics
3. Generate forecasts and projections
4. Validate numerical accuracy

Focus on:
- Liquidity ratios (current ratio, quick ratio)
- Profitability ratios (gross margin, net margin, ROE, ROA)
- Leverage ratios (debt-to-equity, debt ratio)
- Efficiency ratios (asset turnover, inventory turnover)
- Valuation ratios (P/E, P/B, EV/EBITDA)

Always show your calculations and explain the significance of results."""
        
        return {
            "name": "Calculator Agent",
            "system_prompt": system_prompt,
            "model": self.llm
        }
    
    def _create_synthesis_agent(self):
        """Create synthesis agent for combining insights."""
        system_prompt = """You are a Financial Synthesis Agent. Your role is to:
1. Combine insights from multiple agents
2. Provide comprehensive financial analysis
3. Generate actionable recommendations
4. Ensure consistency and accuracy

Focus on:
- Integrating multiple perspectives
- Providing clear, actionable insights
- Highlighting key findings
- Suggesting next steps

Always provide a balanced, comprehensive view that addresses the user's query completely."""
        
        return {
            "name": "Synthesis Agent",
            "system_prompt": system_prompt,
            "model": self.llm
        }
    
    async def process_query(
        self, 
        query: str, 
        context: str = "", 
        session_id: int = None,
        document_id: int = None
    ) -> Dict[str, Any]:
        """Process a query through the multi-agent system."""
        
        try:
            # Step 1: Planning - Break down the query
            planning_result = await self._execute_planning_agent(query, context)
            
            # Step 2: Document Analysis - Extract relevant data
            analysis_result = await self._execute_document_analyst(
                query, context, planning_result
            )
            
            # Step 3: Financial Calculations - Perform calculations
            calculation_result = await self._execute_calculator_agent(
                query, analysis_result, planning_result
            )
            
            # Step 4: Synthesis - Combine all insights
            synthesis_result = await self._execute_synthesis_agent(
                query, planning_result, analysis_result, calculation_result
            )
            
            return {
                "response": synthesis_result["response"],
                "confidence_score": synthesis_result.get("confidence_score", 0.85),
                "citations": synthesis_result.get("citations", []),
                "model_used": "gpt-4",
                "tokens_used": synthesis_result.get("tokens_used", 0),
                "agent_workflow": {
                    "planning": planning_result,
                    "analysis": analysis_result,
                    "calculation": calculation_result,
                    "synthesis": synthesis_result
                }
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error processing your request: {str(e)}",
                "confidence_score": 0.0,
                "citations": [],
                "model_used": "gpt-4",
                "tokens_used": 0,
                "error": str(e)
            }
    
    async def _execute_planning_agent(self, query: str, context: str) -> Dict[str, Any]:
        """Execute the planning agent."""
        try:
            prompt = f"""
            {self.planning_agent['system_prompt']}
            
            User Query: {query}
            Available Context: {context[:1000] if context else "No specific context available"}
            
            Please analyze this query and create a structured plan for answering it.
            """
            
            messages = [
                SystemMessage(content=self.planning_agent['system_prompt']),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.agenerate([messages])
            result = response.generations[0][0].text
            
            return {
                "agent": "Planning Agent",
                "result": result,
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "agent": "Planning Agent",
                "result": f"Error in planning: {str(e)}",
                "status": "failed"
            }
    
    async def _execute_document_analyst(
        self, 
        query: str, 
        context: str, 
        planning_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the document analyst agent."""
        try:
            prompt = f"""
            {self.document_analyst['system_prompt']}
            
            User Query: {query}
            Planning Analysis: {planning_result.get('result', '')}
            Document Context: {context}
            
            Please analyze the available data and extract relevant financial information.
            """
            
            messages = [
                SystemMessage(content=self.document_analyst['system_prompt']),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.agenerate([messages])
            result = response.generations[0][0].text
            
            return {
                "agent": "Document Analyst",
                "result": result,
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "agent": "Document Analyst",
                "result": f"Error in document analysis: {str(e)}",
                "status": "failed"
            }
    
    async def _execute_calculator_agent(
        self, 
        query: str, 
        analysis_result: Dict[str, Any],
        planning_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the calculator agent."""
        try:
            prompt = f"""
            {self.calculator_agent['system_prompt']}
            
            User Query: {query}
            Document Analysis: {analysis_result.get('result', '')}
            Planning Analysis: {planning_result.get('result', '')}
            
            Please perform any necessary financial calculations and provide numerical analysis.
            """
            
            messages = [
                SystemMessage(content=self.calculator_agent['system_prompt']),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.agenerate([messages])
            result = response.generations[0][0].text
            
            return {
                "agent": "Calculator Agent",
                "result": result,
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "agent": "Calculator Agent",
                "result": f"Error in calculations: {str(e)}",
                "status": "failed"
            }
    
    async def _execute_synthesis_agent(
        self, 
        query: str, 
        planning_result: Dict[str, Any],
        analysis_result: Dict[str, Any],
        calculation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the synthesis agent."""
        try:
            prompt = f"""
            {self.synthesis_agent['system_prompt']}
            
            User Query: {query}
            
            Planning Analysis: {planning_result.get('result', '')}
            Document Analysis: {analysis_result.get('result', '')}
            Calculation Results: {calculation_result.get('result', '')}
            
            Please synthesize all the information above into a comprehensive, actionable response.
            """
            
            messages = [
                SystemMessage(content=self.synthesis_agent['system_prompt']),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.agenerate([messages])
            result = response.generations[0][0].text
            
            return {
                "agent": "Synthesis Agent",
                "response": result,
                "confidence_score": 0.9,
                "citations": [],
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "agent": "Synthesis Agent",
                "response": f"Error in synthesis: {str(e)}",
                "confidence_score": 0.0,
                "citations": [],
                "status": "failed"
            }
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        return {
            "planning_agent": {
                "name": self.planning_agent["name"],
                "status": "active"
            },
            "document_analyst": {
                "name": self.document_analyst["name"],
                "status": "active"
            },
            "calculator_agent": {
                "name": self.calculator_agent["name"],
                "status": "active"
            },
            "synthesis_agent": {
                "name": self.synthesis_agent["name"],
                "status": "active"
            }
        }
