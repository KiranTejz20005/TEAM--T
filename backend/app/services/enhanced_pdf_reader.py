"""
Enhanced PDF reader with advanced text extraction, table detection, and financial data parsing.
"""
import fitz  # PyMuPDF
import pandas as pd
import numpy as np
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

import camelot
import tabula
from pdfplumber import PDF
import cv2
import pytesseract
from PIL import Image
import io

from app.config import settings


class DocumentType(Enum):
    """Financial document types."""
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"
    MD_A = "md_a"
    ANNUAL_REPORT = "annual_report"
    QUARTERLY_REPORT = "quarterly_report"
    UNKNOWN = "unknown"


@dataclass
class FinancialTable:
    """Financial table structure."""
    page_number: int
    table_type: str
    data: pd.DataFrame
    confidence: float
    coordinates: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class TextBlock:
    """Text block structure."""
    page_number: int
    text: str
    coordinates: Dict[str, Any]
    font_info: Dict[str, Any]
    block_type: str  # paragraph, heading, table, etc.


class EnhancedPDFReader:
    """Enhanced PDF reader with financial document intelligence."""
    
    def __init__(self):
        """Initialize enhanced PDF reader."""
        self.logger = logging.getLogger(__name__)
        self.financial_keywords = {
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
    
    def read_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Read PDF with enhanced financial document processing."""
        try:
            doc = fitz.open(pdf_path)
            result = {
                'document_info': self._extract_document_info(doc),
                'text_blocks': [],
                'tables': [],
                'financial_data': {},
                'metadata': {},
                'processing_time': 0,
                'success': False
            }
            
            start_time = datetime.utcnow()
            
            # Extract text blocks
            for page_num in range(len(doc)):
                page = doc[page_num]
                text_blocks = self._extract_text_blocks(page, page_num)
                result['text_blocks'].extend(text_blocks)
            
            # Extract tables
            tables = self._extract_tables_advanced(pdf_path)
            result['tables'] = tables
            
            # Analyze financial content
            financial_data = self._analyze_financial_content(result['text_blocks'], tables)
            result['financial_data'] = financial_data
            
            # Determine document type
            doc_type = self._classify_document_type(result['text_blocks'], tables)
            result['metadata']['document_type'] = doc_type.value
            
            # Extract key metrics
            key_metrics = self._extract_key_metrics(result['text_blocks'], tables)
            result['metadata']['key_metrics'] = key_metrics
            
            result['success'] = True
            result['processing_time'] = (datetime.utcnow() - start_time).total_seconds()
            
            doc.close()
            return result
            
        except Exception as e:
            self.logger.error(f"Error reading PDF {pdf_path}: {str(e)}")
            return {
                'error': str(e),
                'success': False
            }
    
    def _extract_document_info(self, doc) -> Dict[str, Any]:
        """Extract document metadata."""
        metadata = doc.metadata
        return {
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'subject': metadata.get('subject', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creation_date': metadata.get('creationDate', ''),
            'modification_date': metadata.get('modDate', ''),
            'page_count': len(doc),
            'file_size': doc.page_count
        }
    
    def _extract_text_blocks(self, page, page_num: int) -> List[TextBlock]:
        """Extract text blocks with formatting information."""
        blocks = []
        
        # Get text with formatting
        text_dict = page.get_text("dict")
        
        for block in text_dict["blocks"]:
            if "lines" in block:
                block_text = ""
                font_info = {}
                
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"]
                        font_info = {
                            'font': span["font"],
                            'size': span["size"],
                            'flags': span["flags"]
                        }
                
                if block_text.strip():
                    blocks.append(TextBlock(
                        page_number=page_num,
                        text=block_text.strip(),
                        coordinates=block.get("bbox", {}),
                        font_info=font_info,
                        block_type=self._classify_text_block(block_text, font_info)
                    ))
        
        return blocks
    
    def _classify_text_block(self, text: str, font_info: Dict) -> str:
        """Classify text block type."""
        text_lower = text.lower()
        
        # Check for headings
        if font_info.get('size', 0) > 12 or any(word in text_lower for word in ['summary', 'overview', 'introduction']):
            return 'heading'
        
        # Check for financial data
        if any(keyword in text_lower for keyword in ['$', 'revenue', 'income', 'profit', 'loss']):
            return 'financial_data'
        
        # Check for tables
        if re.search(r'\d+[,.]?\d*', text) and len(text.split()) > 3:
            return 'table_data'
        
        return 'paragraph'
    
    def _extract_tables_advanced(self, pdf_path: str) -> List[FinancialTable]:
        """Extract tables using multiple methods."""
        tables = []
        
        try:
            # Method 1: Camelot
            camelot_tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
            for i, table in enumerate(camelot_tables):
                if not table.df.empty:
                    tables.append(FinancialTable(
                        page_number=table.page,
                        table_type='camelot',
                        data=table.df,
                        confidence=table.accuracy,
                        coordinates=table._bbox,
                        metadata={'method': 'camelot', 'index': i}
                    ))
        except Exception as e:
            self.logger.warning(f"Camelot extraction failed: {str(e)}")
        
        try:
            # Method 2: Tabula
            tabula_tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
            for i, table in enumerate(tabula_tables):
                if not table.empty:
                    tables.append(FinancialTable(
                        page_number=0,  # Tabula doesn't provide page info easily
                        table_type='tabula',
                        data=table,
                        confidence=0.8,  # Default confidence
                        coordinates={},
                        metadata={'method': 'tabula', 'index': i}
                    ))
        except Exception as e:
            self.logger.warning(f"Tabula extraction failed: {str(e)}")
        
        try:
            # Method 3: PDFPlumber
            with PDF(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    for i, table in enumerate(page_tables):
                        if table:
                            df = pd.DataFrame(table[1:], columns=table[0])
                            tables.append(FinancialTable(
                                page_number=page_num,
                                table_type='pdfplumber',
                                data=df,
                                confidence=0.7,
                                coordinates={},
                                metadata={'method': 'pdfplumber', 'index': i}
                            ))
        except Exception as e:
            self.logger.warning(f"PDFPlumber extraction failed: {str(e)}")
        
        return tables
    
    def _analyze_financial_content(self, text_blocks: List[TextBlock], tables: List[FinancialTable]) -> Dict[str, Any]:
        """Analyze financial content and extract key information."""
        financial_data = {
            'revenue_data': [],
            'expense_data': [],
            'balance_sheet_items': [],
            'cash_flow_items': [],
            'ratios': {},
            'trends': {},
            'periods': []
        }
        
        # Extract financial data from text
        for block in text_blocks:
            if block.block_type == 'financial_data':
                financial_items = self._extract_financial_items(block.text)
                financial_data.update(financial_items)
        
        # Extract data from tables
        for table in tables:
            table_data = self._analyze_financial_table(table.data)
            financial_data.update(table_data)
        
        return financial_data
    
    def _extract_financial_items(self, text: str) -> Dict[str, Any]:
        """Extract financial items from text."""
        items = {
            'revenue_data': [],
            'expense_data': [],
            'balance_sheet_items': []
        }
        
        # Revenue patterns
        revenue_pattern = r'(?:revenue|sales|income)\s*:?\s*\$?([\d,]+\.?\d*)'
        revenue_matches = re.findall(revenue_pattern, text, re.IGNORECASE)
        for match in revenue_matches:
            items['revenue_data'].append({
                'value': float(match.replace(',', '')),
                'text': text,
                'type': 'revenue'
            })
        
        # Expense patterns
        expense_pattern = r'(?:expense|cost|expenditure)\s*:?\s*\$?([\d,]+\.?\d*)'
        expense_matches = re.findall(expense_pattern, text, re.IGNORECASE)
        for match in expense_matches:
            items['expense_data'].append({
                'value': float(match.replace(',', '')),
                'text': text,
                'type': 'expense'
            })
        
        return items
    
    def _analyze_financial_table(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze financial table data."""
        table_data = {
            'revenue_data': [],
            'expense_data': [],
            'balance_sheet_items': []
        }
        
        # Look for financial patterns in table
        for col in df.columns:
            if any(keyword in str(col).lower() for keyword in ['revenue', 'sales', 'income']):
                for idx, row in df.iterrows():
                    if pd.notna(row[col]) and isinstance(row[col], (int, float)):
                        table_data['revenue_data'].append({
                            'value': float(row[col]),
                            'period': str(idx),
                            'type': 'revenue'
                        })
        
        return table_data
    
    def _classify_document_type(self, text_blocks: List[TextBlock], tables: List[FinancialTable]) -> DocumentType:
        """Classify document type based on content."""
        all_text = ' '.join([block.text for block in text_blocks])
        all_text_lower = all_text.lower()
        
        # Check for income statement indicators
        if any(keyword in all_text_lower for keyword in self.financial_keywords['income_statement']):
            return DocumentType.INCOME_STATEMENT
        
        # Check for balance sheet indicators
        if any(keyword in all_text_lower for keyword in self.financial_keywords['balance_sheet']):
            return DocumentType.BALANCE_SHEET
        
        # Check for cash flow indicators
        if any(keyword in all_text_lower for keyword in self.financial_keywords['cash_flow']):
            return DocumentType.CASH_FLOW
        
        # Check for MD&A indicators
        if any(phrase in all_text_lower for phrase in ['management discussion', 'md&a', 'analysis']):
            return DocumentType.MD_A
        
        return DocumentType.UNKNOWN
    
    def _extract_key_metrics(self, text_blocks: List[TextBlock], tables: List[FinancialTable]) -> Dict[str, Any]:
        """Extract key financial metrics."""
        metrics = {
            'revenue': None,
            'net_income': None,
            'total_assets': None,
            'total_liabilities': None,
            'cash': None,
            'periods': []
        }
        
        # Extract from text blocks
        for block in text_blocks:
            if block.block_type == 'financial_data':
                # Look for revenue
                revenue_match = re.search(r'revenue[:\s]*\$?([\d,]+\.?\d*)', block.text, re.IGNORECASE)
                if revenue_match:
                    metrics['revenue'] = float(revenue_match.group(1).replace(',', ''))
                
                # Look for net income
                income_match = re.search(r'net income[:\s]*\$?([\d,]+\.?\d*)', block.text, re.IGNORECASE)
                if income_match:
                    metrics['net_income'] = float(income_match.group(1).replace(',', ''))
        
        # Extract from tables
        for table in tables:
            if not table.data.empty:
                # Look for financial metrics in table
                for col in table.data.columns:
                    col_lower = str(col).lower()
                    if 'revenue' in col_lower or 'sales' in col_lower:
                        # Get the latest value
                        numeric_values = pd.to_numeric(table.data[col], errors='coerce')
                        if not numeric_values.isna().all():
                            metrics['revenue'] = float(numeric_values.dropna().iloc[-1])
        
        return metrics
    
    def extract_sec_data(self, pdf_path: str) -> Dict[str, Any]:
        """Extract SEC filing data with enhanced parsing."""
        result = self.read_pdf(pdf_path)
        
        if not result['success']:
            return result
        
        # Enhanced SEC-specific processing
        sec_data = {
            'company_info': self._extract_company_info(result['text_blocks']),
            'filing_info': self._extract_filing_info(result['text_blocks']),
            'financial_statements': self._extract_financial_statements(result['tables']),
            'md_a_sections': self._extract_md_a_sections(result['text_blocks']),
            'risk_factors': self._extract_risk_factors(result['text_blocks']),
            'business_overview': self._extract_business_overview(result['text_blocks'])
        }
        
        result['sec_data'] = sec_data
        return result
    
    def _extract_company_info(self, text_blocks: List[TextBlock]) -> Dict[str, Any]:
        """Extract company information."""
        company_info = {}
        
        for block in text_blocks:
            text = block.text
            
            # Extract company name
            if 'company name' in text.lower() or 'registrant' in text.lower():
                lines = text.split('\n')
                for line in lines:
                    if 'company name' in line.lower() or 'registrant' in line.lower():
                        company_info['name'] = line.split(':')[-1].strip()
                        break
            
            # Extract CIK
            cik_match = re.search(r'CIK[:\s]*(\d+)', text, re.IGNORECASE)
            if cik_match:
                company_info['cik'] = cik_match.group(1)
            
            # Extract SIC code
            sic_match = re.search(r'SIC[:\s]*(\d+)', text, re.IGNORECASE)
            if sic_match:
                company_info['sic'] = sic_match.group(1)
        
        return company_info
    
    def _extract_filing_info(self, text_blocks: List[TextBlock]) -> Dict[str, Any]:
        """Extract filing information."""
        filing_info = {}
        
        for block in text_blocks:
            text = block.text
            
            # Extract form type
            form_match = re.search(r'form[:\s]*(\d+-K|\d+-Q)', text, re.IGNORECASE)
            if form_match:
                filing_info['form_type'] = form_match.group(1)
            
            # Extract filing date
            date_match = re.search(r'filing date[:\s]*(\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
            if date_match:
                filing_info['filing_date'] = date_match.group(1)
            
            # Extract period end date
            period_match = re.search(r'period end[:\s]*(\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
            if period_match:
                filing_info['period_end'] = period_match.group(1)
        
        return filing_info
    
    def _extract_financial_statements(self, tables: List[FinancialTable]) -> Dict[str, Any]:
        """Extract financial statements from tables."""
        statements = {
            'income_statement': None,
            'balance_sheet': None,
            'cash_flow': None
        }
        
        for table in tables:
            # Classify table type
            table_type = self._classify_table_type(table.data)
            if table_type:
                statements[table_type] = {
                    'data': table.data,
                    'page': table.page_number,
                    'confidence': table.confidence
                }
        
        return statements
    
    def _classify_table_type(self, df: pd.DataFrame) -> Optional[str]:
        """Classify table type based on content."""
        if df.empty:
            return None
        
        # Check column names and content
        columns_text = ' '.join([str(col).lower() for col in df.columns])
        
        if any(keyword in columns_text for keyword in ['revenue', 'sales', 'income', 'profit']):
            return 'income_statement'
        elif any(keyword in columns_text for keyword in ['assets', 'liabilities', 'equity']):
            return 'balance_sheet'
        elif any(keyword in columns_text for keyword in ['cash flow', 'operating', 'investing']):
            return 'cash_flow'
        
        return None
    
    def _extract_md_a_sections(self, text_blocks: List[TextBlock]) -> Dict[str, Any]:
        """Extract MD&A sections."""
        md_a_sections = {
            'overview': [],
            'results_of_operations': [],
            'liquidity': [],
            'capital_resources': []
        }
        
        current_section = None
        
        for block in text_blocks:
            text = block.text.lower()
            
            # Identify section headers
            if 'results of operations' in text:
                current_section = 'results_of_operations'
            elif 'liquidity' in text:
                current_section = 'liquidity'
            elif 'capital resources' in text:
                current_section = 'capital_resources'
            elif 'overview' in text:
                current_section = 'overview'
            
            # Add content to current section
            if current_section and block.block_type == 'paragraph':
                md_a_sections[current_section].append({
                    'text': block.text,
                    'page': block.page_number
                })
        
        return md_a_sections
    
    def _extract_risk_factors(self, text_blocks: List[TextBlock]) -> List[Dict[str, Any]]:
        """Extract risk factors."""
        risk_factors = []
        in_risk_section = False
        
        for block in text_blocks:
            text = block.text.lower()
            
            if 'risk factors' in text:
                in_risk_section = True
                continue
            
            if in_risk_section and block.block_type == 'paragraph':
                # Look for numbered risk factors
                if re.match(r'^\d+\.', block.text):
                    risk_factors.append({
                        'text': block.text,
                        'page': block.page_number
                    })
        
        return risk_factors
    
    def _extract_business_overview(self, text_blocks: List[TextBlock]) -> List[Dict[str, Any]]:
        """Extract business overview section."""
        business_overview = []
        in_overview_section = False
        
        for block in text_blocks:
            text = block.text.lower()
            
            if 'business' in text and 'overview' in text:
                in_overview_section = True
                continue
            
            if in_overview_section and block.block_type == 'paragraph':
                business_overview.append({
                    'text': block.text,
                    'page': block.page_number
                })
        
        return business_overview
