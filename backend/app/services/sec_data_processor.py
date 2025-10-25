"""
SEC data processor for financial statement extracts and filings.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import json
import re
import requests
from dataclasses import dataclass
from enum import Enum

from app.services.enhanced_pdf_reader import EnhancedPDFReader
from app.services.md_a_generator import MDAGenerator
from app.config import settings


class FilingType(Enum):
    """SEC filing types."""
    FORM_10K = "10-K"
    FORM_10Q = "10-Q"
    FORM_8K = "8-K"
    FORM_20F = "20-F"
    FORM_6K = "6-K"


@dataclass
class SECFiling:
    """SEC filing structure."""
    cik: str
    company_name: str
    form_type: FilingType
    filing_date: datetime
    period_end: datetime
    accession_number: str
    file_url: str
    document_url: str
    size: int
    is_amendment: bool


@dataclass
class FinancialStatement:
    """Financial statement structure."""
    statement_type: str  # income_statement, balance_sheet, cash_flow
    period: str
    data: pd.DataFrame
    metadata: Dict[str, Any]
    confidence: float


class SECDataProcessor:
    """SEC data processor for financial statement extracts."""
    
    def __init__(self):
        """Initialize SEC data processor."""
        self.logger = logging.getLogger(__name__)
        self.pdf_reader = EnhancedPDFReader()
        self.md_a_generator = MDAGenerator()
        
        # SEC API endpoints
        self.sec_base_url = "https://data.sec.gov/api/xbrl/companyfacts"
        self.sec_submissions_url = "https://data.sec.gov/submissions"
        
        # Financial statement patterns
        self.statement_patterns = {
            'income_statement': [
                'revenue', 'sales', 'income', 'profit', 'loss', 'earnings',
                'operating income', 'net income', 'gross profit', 'ebitda'
            ],
            'balance_sheet': [
                'assets', 'liabilities', 'equity', 'cash', 'inventory',
                'accounts receivable', 'debt', 'stockholders equity'
            ],
            'cash_flow': [
                'cash flow', 'operating activities', 'investing activities',
                'financing activities', 'free cash flow'
            ]
        }
    
    async def process_sec_filing(
        self, 
        filing_url: str,
        company_cik: str,
        form_type: str
    ) -> Dict[str, Any]:
        """Process SEC filing and extract financial data."""
        
        result = {
            'filing_info': {},
            'financial_statements': [],
            'md_a_draft': '',
            'key_metrics': [],
            'processing_time': 0.0,
            'success': False
        }
        
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Download and parse filing
            filing_data = await self._download_filing(filing_url)
            if not filing_data['success']:
                return filing_data
            
            # Step 2: Extract financial statements
            statements = await self._extract_financial_statements(filing_data['content'])
            result['financial_statements'] = statements
            
            # Step 3: Calculate key metrics and ratios
            metrics = await self._calculate_key_metrics(statements)
            result['key_metrics'] = metrics
            
            # Step 4: Generate MD&A draft
            md_a_result = await self._generate_md_a_from_statements(statements, metrics)
            result['md_a_draft'] = md_a_result['md_a_draft']
            
            # Step 5: Extract filing metadata
            filing_info = await self._extract_filing_info(filing_data['content'])
            result['filing_info'] = filing_info
            
            result['success'] = True
            
        except Exception as e:
            self.logger.error(f"Error processing SEC filing: {str(e)}")
            result['error'] = str(e)
        
        finally:
            end_time = datetime.utcnow()
            result['processing_time'] = (end_time - start_time).total_seconds()
        
        return result
    
    async def _download_filing(self, filing_url: str) -> Dict[str, Any]:
        """Download SEC filing."""
        try:
            response = requests.get(filing_url, timeout=30)
            response.raise_for_status()
            
            return {
                'content': response.text,
                'status_code': response.status_code,
                'success': True
            }
        
        except Exception as e:
            self.logger.error(f"Error downloading filing: {str(e)}")
            return {
                'error': str(e),
                'success': False
            }
    
    async def _extract_financial_statements(self, content: str) -> List[FinancialStatement]:
        """Extract financial statements from filing content."""
        statements = []
        
        try:
            # Parse HTML content to extract tables
            tables = self._extract_tables_from_html(content)
            
            for table in tables:
                # Classify table type
                table_type = self._classify_table_type(table)
                if table_type:
                    statement = FinancialStatement(
                        statement_type=table_type,
                        period=self._extract_period_from_table(table),
                        data=table,
                        metadata=self._extract_table_metadata(table),
                        confidence=0.8
                    )
                    statements.append(statement)
        
        except Exception as e:
            self.logger.error(f"Error extracting financial statements: {str(e)}")
        
        return statements
    
    def _extract_tables_from_html(self, html_content: str) -> List[pd.DataFrame]:
        """Extract tables from HTML content."""
        tables = []
        
        try:
            # Use pandas to read HTML tables
            dfs = pd.read_html(html_content)
            tables.extend(dfs)
        
        except Exception as e:
            self.logger.warning(f"Error extracting tables from HTML: {str(e)}")
        
        return tables
    
    def _classify_table_type(self, df: pd.DataFrame) -> Optional[str]:
        """Classify table type based on content."""
        if df.empty:
            return None
        
        # Get all text from the dataframe
        all_text = ' '.join([str(cell).lower() for cell in df.values.flatten()])
        
        # Check for income statement indicators
        if any(keyword in all_text for keyword in self.statement_patterns['income_statement']):
            return 'income_statement'
        
        # Check for balance sheet indicators
        if any(keyword in all_text for keyword in self.statement_patterns['balance_sheet']):
            return 'balance_sheet'
        
        # Check for cash flow indicators
        if any(keyword in all_text for keyword in self.statement_patterns['cash_flow']):
            return 'cash_flow'
        
        return None
    
    def _extract_period_from_table(self, df: pd.DataFrame) -> str:
        """Extract period information from table."""
        # Look for date patterns in the dataframe
        date_pattern = r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{4}'
        
        for col in df.columns:
            if isinstance(col, str) and re.search(date_pattern, col):
                return col
        
        # Look in the data
        for row in df.itertuples():
            for cell in row:
                if isinstance(cell, str) and re.search(date_pattern, cell):
                    return cell
        
        return "Unknown Period"
    
    def _extract_table_metadata(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract metadata from table."""
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'data_types': df.dtypes.to_dict(),
            'has_numeric_data': df.select_dtypes(include=[np.number]).shape[1] > 0
        }
    
    async def _calculate_key_metrics(self, statements: List[FinancialStatement]) -> List[Dict[str, Any]]:
        """Calculate key financial metrics from statements."""
        metrics = []
        
        for statement in statements:
            if statement.statement_type == 'income_statement':
                # Calculate income statement metrics
                income_metrics = self._calculate_income_statement_metrics(statement.data)
                metrics.extend(income_metrics)
            
            elif statement.statement_type == 'balance_sheet':
                # Calculate balance sheet metrics
                balance_metrics = self._calculate_balance_sheet_metrics(statement.data)
                metrics.extend(balance_metrics)
            
            elif statement.statement_type == 'cash_flow':
                # Calculate cash flow metrics
                cash_flow_metrics = self._calculate_cash_flow_metrics(statement.data)
                metrics.extend(cash_flow_metrics)
        
        return metrics
    
    def _calculate_income_statement_metrics(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate income statement metrics."""
        metrics = []
        
        try:
            # Look for revenue
            revenue_cols = [col for col in df.columns if 'revenue' in str(col).lower() or 'sales' in str(col).lower()]
            if revenue_cols:
                for col in revenue_cols:
                    numeric_data = pd.to_numeric(df[col], errors='coerce')
                    if not numeric_data.isna().all():
                        latest_revenue = numeric_data.dropna().iloc[-1]
                        metrics.append({
                            'metric': 'Revenue',
                            'value': latest_revenue,
                            'period': statement.period,
                            'statement_type': 'income_statement'
                        })
            
            # Look for net income
            income_cols = [col for col in df.columns if 'net income' in str(col).lower() or 'net profit' in str(col).lower()]
            if income_cols:
                for col in income_cols:
                    numeric_data = pd.to_numeric(df[col], errors='coerce')
                    if not numeric_data.isna().all():
                        latest_income = numeric_data.dropna().iloc[-1]
                        metrics.append({
                            'metric': 'Net Income',
                            'value': latest_income,
                            'period': statement.period,
                            'statement_type': 'income_statement'
                        })
        
        except Exception as e:
            self.logger.error(f"Error calculating income statement metrics: {str(e)}")
        
        return metrics
    
    def _calculate_balance_sheet_metrics(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate balance sheet metrics."""
        metrics = []
        
        try:
            # Look for total assets
            assets_cols = [col for col in df.columns if 'total assets' in str(col).lower()]
            if assets_cols:
                for col in assets_cols:
                    numeric_data = pd.to_numeric(df[col], errors='coerce')
                    if not numeric_data.isna().all():
                        latest_assets = numeric_data.dropna().iloc[-1]
                        metrics.append({
                            'metric': 'Total Assets',
                            'value': latest_assets,
                            'period': statement.period,
                            'statement_type': 'balance_sheet'
                        })
            
            # Look for total liabilities
            liabilities_cols = [col for col in df.columns if 'total liabilities' in str(col).lower()]
            if liabilities_cols:
                for col in liabilities_cols:
                    numeric_data = pd.to_numeric(df[col], errors='coerce')
                    if not numeric_data.isna().all():
                        latest_liabilities = numeric_data.dropna().iloc[-1]
                        metrics.append({
                            'metric': 'Total Liabilities',
                            'value': latest_liabilities,
                            'period': statement.period,
                            'statement_type': 'balance_sheet'
                        })
        
        except Exception as e:
            self.logger.error(f"Error calculating balance sheet metrics: {str(e)}")
        
        return metrics
    
    def _calculate_cash_flow_metrics(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate cash flow metrics."""
        metrics = []
        
        try:
            # Look for operating cash flow
            operating_cols = [col for col in df.columns if 'operating' in str(col).lower() and 'cash' in str(col).lower()]
            if operating_cols:
                for col in operating_cols:
                    numeric_data = pd.to_numeric(df[col], errors='coerce')
                    if not numeric_data.isna().all():
                        latest_operating = numeric_data.dropna().iloc[-1]
                        metrics.append({
                            'metric': 'Operating Cash Flow',
                            'value': latest_operating,
                            'period': statement.period,
                            'statement_type': 'cash_flow'
                        })
        
        except Exception as e:
            self.logger.error(f"Error calculating cash flow metrics: {str(e)}")
        
        return metrics
    
    async def _generate_md_a_from_statements(
        self, 
        statements: List[FinancialStatement], 
        metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate MD&A draft from financial statements."""
        
        # Convert statements to financial data format
        financial_data = self._convert_statements_to_financial_data(statements)
        
        # Generate MD&A draft
        md_a_result = await self.md_a_generator.generate_md_a_draft(
            financial_data=financial_data,
            company_info={},
            period="Q3 2024"
        )
        
        return md_a_result
    
    def _convert_statements_to_financial_data(self, statements: List[FinancialStatement]) -> Dict[str, Any]:
        """Convert financial statements to financial data format."""
        financial_data = {}
        
        for statement in statements:
            if statement.statement_type == 'income_statement':
                # Extract revenue and income data
                revenue_data = self._extract_revenue_data(statement.data)
                if revenue_data:
                    financial_data['revenue'] = revenue_data
                
                income_data = self._extract_income_data(statement.data)
                if income_data:
                    financial_data['net_income'] = income_data
            
            elif statement.statement_type == 'balance_sheet':
                # Extract assets and liabilities data
                assets_data = self._extract_assets_data(statement.data)
                if assets_data:
                    financial_data['assets'] = assets_data
                
                liabilities_data = self._extract_liabilities_data(statement.data)
                if liabilities_data:
                    financial_data['liabilities'] = liabilities_data
            
            elif statement.statement_type == 'cash_flow':
                # Extract cash flow data
                cash_flow_data = self._extract_cash_flow_data(statement.data)
                if cash_flow_data:
                    financial_data['cash_flow'] = cash_flow_data
        
        return financial_data
    
    def _extract_revenue_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract revenue data from income statement."""
        revenue_data = []
        
        try:
            # Look for revenue columns
            revenue_cols = [col for col in df.columns if 'revenue' in str(col).lower() or 'sales' in str(col).lower()]
            
            for col in revenue_cols:
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                for idx, value in numeric_data.dropna().items():
                    revenue_data.append({
                        'value': float(value),
                        'period': str(idx),
                        'type': 'revenue'
                    })
        
        except Exception as e:
            self.logger.error(f"Error extracting revenue data: {str(e)}")
        
        return revenue_data
    
    def _extract_income_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract income data from income statement."""
        income_data = []
        
        try:
            # Look for net income columns
            income_cols = [col for col in df.columns if 'net income' in str(col).lower() or 'net profit' in str(col).lower()]
            
            for col in income_cols:
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                for idx, value in numeric_data.dropna().items():
                    income_data.append({
                        'value': float(value),
                        'period': str(idx),
                        'type': 'net_income'
                    })
        
        except Exception as e:
            self.logger.error(f"Error extracting income data: {str(e)}")
        
        return income_data
    
    def _extract_assets_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract assets data from balance sheet."""
        assets_data = []
        
        try:
            # Look for total assets columns
            assets_cols = [col for col in df.columns if 'total assets' in str(col).lower()]
            
            for col in assets_cols:
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                for idx, value in numeric_data.dropna().items():
                    assets_data.append({
                        'value': float(value),
                        'period': str(idx),
                        'type': 'assets'
                    })
        
        except Exception as e:
            self.logger.error(f"Error extracting assets data: {str(e)}")
        
        return assets_data
    
    def _extract_liabilities_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract liabilities data from balance sheet."""
        liabilities_data = []
        
        try:
            # Look for total liabilities columns
            liabilities_cols = [col for col in df.columns if 'total liabilities' in str(col).lower()]
            
            for col in liabilities_cols:
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                for idx, value in numeric_data.dropna().items():
                    liabilities_data.append({
                        'value': float(value),
                        'period': str(idx),
                        'type': 'liabilities'
                    })
        
        except Exception as e:
            self.logger.error(f"Error extracting liabilities data: {str(e)}")
        
        return liabilities_data
    
    def _extract_cash_flow_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract cash flow data from cash flow statement."""
        cash_flow_data = []
        
        try:
            # Look for operating cash flow columns
            cash_flow_cols = [col for col in df.columns if 'operating' in str(col).lower() and 'cash' in str(col).lower()]
            
            for col in cash_flow_cols:
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                for idx, value in numeric_data.dropna().items():
                    cash_flow_data.append({
                        'value': float(value),
                        'period': str(idx),
                        'type': 'cash_flow'
                    })
        
        except Exception as e:
            self.logger.error(f"Error extracting cash flow data: {str(e)}")
        
        return cash_flow_data
    
    async def _extract_filing_info(self, content: str) -> Dict[str, Any]:
        """Extract filing information from content."""
        filing_info = {}
        
        try:
            # Extract company name
            company_match = re.search(r'company name[:\s]*([^\n]+)', content, re.IGNORECASE)
            if company_match:
                filing_info['company_name'] = company_match.group(1).strip()
            
            # Extract CIK
            cik_match = re.search(r'CIK[:\s]*(\d+)', content, re.IGNORECASE)
            if cik_match:
                filing_info['cik'] = cik_match.group(1)
            
            # Extract form type
            form_match = re.search(r'form[:\s]*(\d+-K|\d+-Q)', content, re.IGNORECASE)
            if form_match:
                filing_info['form_type'] = form_match.group(1)
            
            # Extract filing date
            date_match = re.search(r'filing date[:\s]*(\d{4}-\d{2}-\d{2})', content, re.IGNORECASE)
            if date_match:
                filing_info['filing_date'] = date_match.group(1)
        
        except Exception as e:
            self.logger.error(f"Error extracting filing info: {str(e)}")
        
        return filing_info
    
    async def process_kaggle_sec_data(self, data_path: str) -> Dict[str, Any]:
        """Process SEC data from Kaggle dataset."""
        
        result = {
            'processed_filings': [],
            'financial_statements': [],
            'md_a_drafts': [],
            'success': False
        }
        
        try:
            # Load Kaggle dataset
            df = pd.read_csv(data_path)
            
            # Process each filing
            for idx, row in df.iterrows():
                filing_result = await self.process_sec_filing(
                    filing_url=row.get('filing_url', ''),
                    company_cik=row.get('cik', ''),
                    form_type=row.get('form_type', '')
                )
                
                if filing_result['success']:
                    result['processed_filings'].append(filing_result)
                    result['financial_statements'].extend(filing_result['financial_statements'])
                    result['md_a_drafts'].append(filing_result['md_a_draft'])
            
            result['success'] = True
        
        except Exception as e:
            self.logger.error(f"Error processing Kaggle SEC data: {str(e)}")
            result['error'] = str(e)
        
        return result
