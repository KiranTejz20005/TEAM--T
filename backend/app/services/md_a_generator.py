"""
Automated MD&A (Management Discussion & Analysis) draft generation from financial statements.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import json
import re
from dataclasses import dataclass
from enum import Enum

import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.services.rag_service import RAGService
from app.services.financial_analyzer import FinancialAnalyzer
from app.config import settings


class MDASection(Enum):
    """MD&A section types."""
    EXECUTIVE_SUMMARY = "executive_summary"
    BUSINESS_OVERVIEW = "business_overview"
    RESULTS_OF_OPERATIONS = "results_of_operations"
    LIQUIDITY_AND_CAPITAL_RESOURCES = "liquidity_and_capital_resources"
    MARKET_RISKS = "market_risks"
    CRITICAL_ACCOUNTING_POLICIES = "critical_accounting_policies"
    FORWARD_LOOKING_STATEMENTS = "forward_looking_statements"


@dataclass
class FinancialMetric:
    """Financial metric structure."""
    name: str
    current_value: float
    previous_value: float
    change_percent: float
    trend: str  # 'increasing', 'decreasing', 'stable'
    significance: str  # 'high', 'medium', 'low'
    period: str


@dataclass
class MDASection:
    """MD&A section structure."""
    section_type: MDASection
    title: str
    content: str
    key_metrics: List[FinancialMetric]
    citations: List[str]
    confidence: float


class MDAGenerator:
    """Automated MD&A draft generator."""
    
    def __init__(self):
        """Initialize MD&A generator."""
        self.logger = logging.getLogger(__name__)
        genai.configure(api_key=settings.gemini_api_key)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=settings.gemini_api_key
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.gemini_api_key
        )
        self.rag_service = RAGService()
        self.financial_analyzer = FinancialAnalyzer()
        
        # Initialize prompt templates
        self._initialize_prompts()
    
    def _initialize_prompts(self):
        """Initialize prompt templates for MD&A generation."""
        self.prompts = {
            'executive_summary': PromptTemplate(
                input_variables=["financial_data", "key_metrics", "period"],
                template="""
                Generate an executive summary for the {period} period based on the following financial data:
                
                Key Metrics:
                {key_metrics}
                
                Financial Data:
                {financial_data}
                
                Write a concise executive summary (2-3 paragraphs) highlighting:
                1. Overall financial performance
                2. Key revenue drivers
                3. Major challenges or opportunities
                4. Strategic outlook
                
                Use professional, SEC-compliant language.
                """
            ),
            
            'results_of_operations': PromptTemplate(
                input_variables=["income_statement", "metrics", "period"],
                template="""
                Generate a "Results of Operations" section for the {period} period:
                
                Income Statement Data:
                {income_statement}
                
                Key Metrics:
                {metrics}
                
                Focus on:
                1. Revenue analysis and drivers
                2. Cost structure and efficiency
                3. Profitability trends
                4. Operational performance
                
                Provide specific numbers and percentages where available.
                """
            ),
            
            'liquidity_analysis': PromptTemplate(
                input_variables=["balance_sheet", "cash_flow", "ratios", "period"],
                template="""
                Generate a "Liquidity and Capital Resources" section for the {period} period:
                
                Balance Sheet:
                {balance_sheet}
                
                Cash Flow:
                {cash_flow}
                
                Financial Ratios:
                {ratios}
                
                Cover:
                1. Liquidity position
                2. Cash generation and usage
                3. Debt levels and coverage
                4. Capital allocation strategy
                """
            ),
            
            'risk_factors': PromptTemplate(
                input_variables=["financial_data", "industry_context", "period"],
                template="""
                Generate risk factors based on the financial data for {period}:
                
                Financial Data:
                {financial_data}
                
                Industry Context:
                {industry_context}
                
                Identify and discuss:
                1. Financial risks (liquidity, credit, market)
                2. Operational risks
                3. Regulatory risks
                4. Market risks
                
                Use standard risk factor language.
                """
            )
        }
    
    async def generate_md_a_draft(
        self, 
        financial_data: Dict[str, Any],
        company_info: Dict[str, Any],
        period: str = "Q3 2024"
    ) -> Dict[str, Any]:
        """Generate complete MD&A draft."""
        
        result = {
            'md_a_draft': '',
            'sections': [],
            'key_metrics': [],
            'citations': [],
            'confidence': 0.0,
            'generation_time': 0.0,
            'success': False
        }
        
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Extract and analyze financial metrics
            metrics = await self._extract_financial_metrics(financial_data)
            result['key_metrics'] = metrics
            
            # Step 2: Generate each MD&A section
            sections = []
            
            # Executive Summary
            exec_summary = await self._generate_executive_summary(
                financial_data, metrics, period
            )
            sections.append(exec_summary)
            
            # Results of Operations
            results_ops = await self._generate_results_of_operations(
                financial_data, metrics, period
            )
            sections.append(results_ops)
            
            # Liquidity and Capital Resources
            liquidity = await self._generate_liquidity_analysis(
                financial_data, metrics, period
            )
            sections.append(liquidity)
            
            # Risk Factors
            risks = await self._generate_risk_factors(
                financial_data, company_info, period
            )
            sections.append(risks)
            
            # Step 3: Combine sections into complete draft
            md_a_draft = self._combine_sections(sections)
            result['md_a_draft'] = md_a_draft
            result['sections'] = sections
            
            # Step 4: Extract citations
            citations = self._extract_citations(sections)
            result['citations'] = citations
            
            # Step 5: Calculate confidence
            confidence = self._calculate_confidence(sections, metrics)
            result['confidence'] = confidence
            
            result['success'] = True
            
        except Exception as e:
            self.logger.error(f"Error generating MD&A draft: {str(e)}")
            result['error'] = str(e)
        
        finally:
            end_time = datetime.utcnow()
            result['generation_time'] = (end_time - start_time).total_seconds()
        
        return result
    
    async def _extract_financial_metrics(self, financial_data: Dict[str, Any]) -> List[FinancialMetric]:
        """Extract and analyze financial metrics."""
        metrics = []
        
        try:
            # Revenue metrics
            if 'revenue' in financial_data:
                revenue_data = financial_data['revenue']
                if len(revenue_data) >= 2:
                    current = revenue_data[-1]['value']
                    previous = revenue_data[-2]['value']
                    change_pct = ((current - previous) / previous) * 100
                    
                    metrics.append(FinancialMetric(
                        name='Revenue',
                        current_value=current,
                        previous_value=previous,
                        change_percent=change_pct,
                        trend='increasing' if change_pct > 0 else 'decreasing',
                        significance='high',
                        period='quarterly'
                    ))
            
            # Profitability metrics
            if 'net_income' in financial_data:
                income_data = financial_data['net_income']
                if len(income_data) >= 2:
                    current = income_data[-1]['value']
                    previous = income_data[-2]['value']
                    change_pct = ((current - previous) / previous) * 100
                    
                    metrics.append(FinancialMetric(
                        name='Net Income',
                        current_value=current,
                        previous_value=previous,
                        change_percent=change_pct,
                        trend='increasing' if change_pct > 0 else 'decreasing',
                        significance='high',
                        period='quarterly'
                    ))
            
            # Calculate financial ratios
            ratios = await self.financial_analyzer.calculate_ratios(financial_data)
            
            for ratio_name, ratio_value in ratios.items():
                metrics.append(FinancialMetric(
                    name=ratio_name,
                    current_value=ratio_value,
                    previous_value=0,  # Would need historical data
                    change_percent=0,
                    trend='stable',
                    significance='medium',
                    period='current'
                ))
        
        except Exception as e:
            self.logger.error(f"Error extracting financial metrics: {str(e)}")
        
        return metrics
    
    async def _generate_executive_summary(
        self, 
        financial_data: Dict[str, Any], 
        metrics: List[FinancialMetric],
        period: str
    ) -> MDASection:
        """Generate executive summary section."""
        
        # Prepare data for prompt
        key_metrics_text = self._format_metrics_for_prompt(metrics)
        financial_data_text = self._format_financial_data_for_prompt(financial_data)
        
        # Generate content using LLM
        chain = LLMChain(llm=self.llm, prompt=self.prompts['executive_summary'])
        content = await chain.arun(
            financial_data=financial_data_text,
            key_metrics=key_metrics_text,
            period=period
        )
        
        return MDASection(
            section_type=MDASection.EXECUTIVE_SUMMARY,
            title="Executive Summary",
            content=content,
            key_metrics=metrics,
            citations=[],
            confidence=0.8
        )
    
    async def _generate_results_of_operations(
        self, 
        financial_data: Dict[str, Any], 
        metrics: List[FinancialMetric],
        period: str
    ) -> MDASection:
        """Generate results of operations section."""
        
        # Extract income statement data
        income_statement = self._extract_income_statement_data(financial_data)
        metrics_text = self._format_metrics_for_prompt(metrics)
        
        # Generate content
        chain = LLMChain(llm=self.llm, prompt=self.prompts['results_of_operations'])
        content = await chain.arun(
            income_statement=income_statement,
            metrics=metrics_text,
            period=period
        )
        
        return MDASection(
            section_type=MDASection.RESULTS_OF_OPERATIONS,
            title="Results of Operations",
            content=content,
            key_metrics=metrics,
            citations=[],
            confidence=0.8
        )
    
    async def _generate_liquidity_analysis(
        self, 
        financial_data: Dict[str, Any], 
        metrics: List[FinancialMetric],
        period: str
    ) -> MDASection:
        """Generate liquidity and capital resources section."""
        
        # Extract balance sheet and cash flow data
        balance_sheet = self._extract_balance_sheet_data(financial_data)
        cash_flow = self._extract_cash_flow_data(financial_data)
        ratios = self._extract_ratios_data(metrics)
        
        # Generate content
        chain = LLMChain(llm=self.llm, prompt=self.prompts['liquidity_analysis'])
        content = await chain.arun(
            balance_sheet=balance_sheet,
            cash_flow=cash_flow,
            ratios=ratios,
            period=period
        )
        
        return MDASection(
            section_type=MDASection.LIQUIDITY_AND_CAPITAL_RESOURCES,
            title="Liquidity and Capital Resources",
            content=content,
            key_metrics=metrics,
            citations=[],
            confidence=0.8
        )
    
    async def _generate_risk_factors(
        self, 
        financial_data: Dict[str, Any], 
        company_info: Dict[str, Any],
        period: str
    ) -> MDASection:
        """Generate risk factors section."""
        
        # Prepare data
        financial_data_text = self._format_financial_data_for_prompt(financial_data)
        industry_context = self._get_industry_context(company_info)
        
        # Generate content
        chain = LLMChain(llm=self.llm, prompt=self.prompts['risk_factors'])
        content = await chain.arun(
            financial_data=financial_data_text,
            industry_context=industry_context,
            period=period
        )
        
        return MDASection(
            section_type=MDASection.MARKET_RISKS,
            title="Risk Factors",
            content=content,
            key_metrics=[],
            citations=[],
            confidence=0.7
        )
    
    def _format_metrics_for_prompt(self, metrics: List[FinancialMetric]) -> str:
        """Format metrics for prompt."""
        formatted = []
        for metric in metrics:
            formatted.append(
                f"- {metric.name}: {metric.current_value:,.2f} "
                f"({metric.change_percent:+.1f}% change, {metric.trend} trend)"
            )
        return "\n".join(formatted)
    
    def _format_financial_data_for_prompt(self, financial_data: Dict[str, Any]) -> str:
        """Format financial data for prompt."""
        formatted = []
        
        for category, data in financial_data.items():
            if isinstance(data, list) and data:
                formatted.append(f"{category.title()}:")
                for item in data[-3:]:  # Last 3 periods
                    if isinstance(item, dict) and 'value' in item:
                        formatted.append(f"  - {item.get('period', 'N/A')}: ${item['value']:,.2f}")
        
        return "\n".join(formatted)
    
    def _extract_income_statement_data(self, financial_data: Dict[str, Any]) -> str:
        """Extract income statement data."""
        income_data = []
        
        # Revenue
        if 'revenue' in financial_data:
            revenue_data = financial_data['revenue']
            for item in revenue_data[-3:]:
                income_data.append(f"Revenue: ${item['value']:,.2f}")
        
        # Expenses
        if 'expenses' in financial_data:
            expense_data = financial_data['expenses']
            for item in expense_data[-3:]:
                income_data.append(f"Expenses: ${item['value']:,.2f}")
        
        return "\n".join(income_data)
    
    def _extract_balance_sheet_data(self, financial_data: Dict[str, Any]) -> str:
        """Extract balance sheet data."""
        balance_data = []
        
        # Assets
        if 'assets' in financial_data:
            assets_data = financial_data['assets']
            for item in assets_data[-3:]:
                balance_data.append(f"Total Assets: ${item['value']:,.2f}")
        
        # Liabilities
        if 'liabilities' in financial_data:
            liabilities_data = financial_data['liabilities']
            for item in liabilities_data[-3:]:
                balance_data.append(f"Total Liabilities: ${item['value']:,.2f}")
        
        return "\n".join(balance_data)
    
    def _extract_cash_flow_data(self, financial_data: Dict[str, Any]) -> str:
        """Extract cash flow data."""
        cash_flow_data = []
        
        if 'cash_flow' in financial_data:
            cash_data = financial_data['cash_flow']
            for item in cash_data[-3:]:
                cash_flow_data.append(f"Cash Flow: ${item['value']:,.2f}")
        
        return "\n".join(cash_flow_data)
    
    def _extract_ratios_data(self, metrics: List[FinancialMetric]) -> str:
        """Extract ratios data."""
        ratios_data = []
        
        for metric in metrics:
            if 'ratio' in metric.name.lower():
                ratios_data.append(f"{metric.name}: {metric.current_value:.2f}")
        
        return "\n".join(ratios_data)
    
    def _get_industry_context(self, company_info: Dict[str, Any]) -> str:
        """Get industry context for risk analysis."""
        # This would typically come from external data sources
        return "Technology sector with high growth potential and competitive dynamics."
    
    def _combine_sections(self, sections: List[MDASection]) -> str:
        """Combine sections into complete MD&A draft."""
        md_a_draft = []
        
        # Add header
        md_a_draft.append("# Management's Discussion and Analysis of Financial Condition and Results of Operations")
        md_a_draft.append("")
        md_a_draft.append("## Overview")
        md_a_draft.append("")
        
        # Add each section
        for section in sections:
            md_a_draft.append(f"## {section.title}")
            md_a_draft.append("")
            md_a_draft.append(section.content)
            md_a_draft.append("")
        
        # Add footer
        md_a_draft.append("## Forward-Looking Statements")
        md_a_draft.append("")
        md_a_draft.append("This discussion contains forward-looking statements that involve risks and uncertainties. Actual results may differ materially from those projected.")
        
        return "\n".join(md_a_draft)
    
    def _extract_citations(self, sections: List[MDASection]) -> List[str]:
        """Extract citations from sections."""
        citations = []
        
        for section in sections:
            # Look for citation patterns in content
            citation_pattern = r'\[(\d+)\]'
            matches = re.findall(citation_pattern, section.content)
            citations.extend(matches)
        
        return list(set(citations))  # Remove duplicates
    
    def _calculate_confidence(self, sections: List[MDASection], metrics: List[FinancialMetric]) -> float:
        """Calculate overall confidence score."""
        if not sections:
            return 0.0
        
        # Average section confidence
        section_confidence = sum(section.confidence for section in sections) / len(sections)
        
        # Boost confidence based on metrics availability
        metrics_boost = min(0.2, len(metrics) * 0.02)
        
        return min(1.0, section_confidence + metrics_boost)
    
    async def generate_section_specific(
        self, 
        section_type: MDASection,
        financial_data: Dict[str, Any],
        company_info: Dict[str, Any],
        period: str
    ) -> MDASection:
        """Generate a specific MD&A section."""
        
        if section_type == MDASection.EXECUTIVE_SUMMARY:
            metrics = await self._extract_financial_metrics(financial_data)
            return await self._generate_executive_summary(financial_data, metrics, period)
        
        elif section_type == MDASection.RESULTS_OF_OPERATIONS:
            metrics = await self._extract_financial_metrics(financial_data)
            return await self._generate_results_of_operations(financial_data, metrics, period)
        
        elif section_type == MDASection.LIQUIDITY_AND_CAPITAL_RESOURCES:
            metrics = await self._extract_financial_metrics(financial_data)
            return await self._generate_liquidity_analysis(financial_data, metrics, period)
        
        elif section_type == MDASection.MARKET_RISKS:
            return await self._generate_risk_factors(financial_data, company_info, period)
        
        else:
            raise ValueError(f"Unsupported section type: {section_type}")
    
    async def validate_md_a(self, md_a_draft: str) -> Dict[str, Any]:
        """Validate MD&A draft for compliance and completeness."""
        
        validation_result = {
            'is_compliant': True,
            'issues': [],
            'suggestions': [],
            'completeness_score': 0.0
        }
        
        # Check for required sections
        required_sections = [
            'executive summary', 'results of operations', 
            'liquidity', 'risk factors'
        ]
        
        missing_sections = []
        for section in required_sections:
            if section.lower() not in md_a_draft.lower():
                missing_sections.append(section)
        
        if missing_sections:
            validation_result['issues'].append(f"Missing sections: {', '.join(missing_sections)}")
            validation_result['is_compliant'] = False
        
        # Check for financial data citations
        if not re.search(r'\$[\d,]+', md_a_draft):
            validation_result['issues'].append("Missing specific financial figures")
            validation_result['is_compliant'] = False
        
        # Check for forward-looking statements disclaimer
        if 'forward-looking' not in md_a_draft.lower():
            validation_result['suggestions'].append("Consider adding forward-looking statements disclaimer")
        
        # Calculate completeness score
        total_checks = len(required_sections) + 2  # +2 for financial data and disclaimer
        passed_checks = total_checks - len(validation_result['issues'])
        validation_result['completeness_score'] = passed_checks / total_checks
        
        return validation_result
