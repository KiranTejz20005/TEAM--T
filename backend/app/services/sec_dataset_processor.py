"""
SEC Financial Statement Dataset Processor for FinMDA-Bot.
Processes and integrates SEC financial statement extracts from Kaggle.
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import asyncio
import aiofiles

class SECDatasetProcessor:
    """Processor for SEC financial statement dataset."""
    
    def __init__(self, dataset_path: str = "data/sec_financial_statements"):
        self.logger = logging.getLogger(__name__)
        self.dataset_path = Path(dataset_path)
        self.processed_data = {}
        self.metadata = {}
        
        # Financial statement types
        self.statement_types = {
            'income_statement': ['revenue', 'net_income', 'gross_profit', 'operating_income'],
            'balance_sheet': ['total_assets', 'total_liabilities', 'total_equity', 'cash'],
            'cash_flow': ['operating_cash_flow', 'investing_cash_flow', 'financing_cash_flow']
        }
        
        # Standard financial ratios
        self.standard_ratios = {
            'liquidity': ['current_ratio', 'quick_ratio', 'cash_ratio'],
            'profitability': ['gross_margin', 'operating_margin', 'net_margin', 'roe', 'roa'],
            'leverage': ['debt_to_equity', 'debt_ratio', 'equity_ratio'],
            'efficiency': ['asset_turnover', 'inventory_turnover', 'receivables_turnover']
        }
    
    async def load_dataset(self, file_path: str = None) -> Dict[str, Any]:
        """Load SEC financial statement dataset."""
        try:
            if file_path:
                dataset_file = Path(file_path)
            else:
                # Look for dataset files in the dataset path
                dataset_files = list(self.dataset_path.glob("*.csv"))
                if not dataset_files:
                    raise FileNotFoundError(f"No CSV files found in {self.dataset_path}")
                dataset_file = dataset_files[0]
            
            self.logger.info(f"Loading SEC dataset from {dataset_file}")
            
            # Load the dataset
            df = pd.read_csv(dataset_file)
            
            # Process the dataset
            processed_data = await self._process_sec_dataframe(df)
            
            self.processed_data = processed_data
            self.metadata = {
                'source_file': str(dataset_file),
                'total_records': len(df),
                'processed_at': datetime.now().isoformat(),
                'columns': list(df.columns)
            }
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error loading SEC dataset: {str(e)}")
            return {}
    
    async def _process_sec_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Process SEC financial statement dataframe."""
        try:
            processed_data = {
                'companies': {},
                'statements': {},
                'ratios': {},
                'trends': {},
                'metadata': {}
            }
            
            # Group by company
            if 'company_name' in df.columns:
                for company, company_data in df.groupby('company_name'):
                    processed_data['companies'][company] = await self._process_company_data(company_data)
            
            # Process financial statements
            processed_data['statements'] = await self._extract_financial_statements(df)
            
            # Calculate ratios
            processed_data['ratios'] = await self._calculate_financial_ratios(df)
            
            # Analyze trends
            processed_data['trends'] = await self._analyze_financial_trends(df)
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error processing SEC dataframe: {str(e)}")
            return {}
    
    async def _process_company_data(self, company_df: pd.DataFrame) -> Dict[str, Any]:
        """Process data for a specific company."""
        try:
            company_data = {
                'name': company_df['company_name'].iloc[0] if 'company_name' in company_df.columns else 'Unknown',
                'ticker': company_df['ticker'].iloc[0] if 'ticker' in company_df.columns else 'Unknown',
                'sector': company_df['sector'].iloc[0] if 'sector' in company_df.columns else 'Unknown',
                'statements': {},
                'ratios': {},
                'trends': {}
            }
            
            # Extract financial statements
            company_data['statements'] = await self._extract_company_statements(company_df)
            
            # Calculate company-specific ratios
            company_data['ratios'] = await self._calculate_company_ratios(company_df)
            
            # Analyze company trends
            company_data['trends'] = await self._analyze_company_trends(company_df)
            
            return company_data
            
        except Exception as e:
            self.logger.error(f"Error processing company data: {str(e)}")
            return {}
    
    async def _extract_financial_statements(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract and organize financial statements."""
        try:
            statements = {
                'income_statements': [],
                'balance_sheets': [],
                'cash_flow_statements': []
            }
            
            # Group by statement type if available
            if 'statement_type' in df.columns:
                for stmt_type, stmt_data in df.groupby('statement_type'):
                    if stmt_type.lower() in ['income', 'income_statement', 'p&l']:
                        statements['income_statements'].append(await self._process_income_statement(stmt_data))
                    elif stmt_type.lower() in ['balance', 'balance_sheet']:
                        statements['balance_sheets'].append(await self._process_balance_sheet(stmt_data))
                    elif stmt_type.lower() in ['cash_flow', 'cash_flow_statement']:
                        statements['cash_flow_statements'].append(await self._process_cash_flow_statement(stmt_data))
            
            return statements
            
        except Exception as e:
            self.logger.error(f"Error extracting financial statements: {str(e)}")
            return {}
    
    async def _process_income_statement(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Process income statement data."""
        try:
            income_statement = {
                'period': df['period'].iloc[0] if 'period' in df.columns else 'Unknown',
                'revenue': self._extract_financial_value(df, 'revenue'),
                'cost_of_goods_sold': self._extract_financial_value(df, 'cost_of_goods_sold'),
                'gross_profit': self._extract_financial_value(df, 'gross_profit'),
                'operating_expenses': self._extract_financial_value(df, 'operating_expenses'),
                'operating_income': self._extract_financial_value(df, 'operating_income'),
                'net_income': self._extract_financial_value(df, 'net_income'),
                'eps': self._extract_financial_value(df, 'eps')
            }
            
            return income_statement
            
        except Exception as e:
            self.logger.error(f"Error processing income statement: {str(e)}")
            return {}
    
    async def _process_balance_sheet(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Process balance sheet data."""
        try:
            balance_sheet = {
                'period': df['period'].iloc[0] if 'period' in df.columns else 'Unknown',
                'total_assets': self._extract_financial_value(df, 'total_assets'),
                'current_assets': self._extract_financial_value(df, 'current_assets'),
                'fixed_assets': self._extract_financial_value(df, 'fixed_assets'),
                'total_liabilities': self._extract_financial_value(df, 'total_liabilities'),
                'current_liabilities': self._extract_financial_value(df, 'current_liabilities'),
                'long_term_debt': self._extract_financial_value(df, 'long_term_debt'),
                'total_equity': self._extract_financial_value(df, 'total_equity'),
                'retained_earnings': self._extract_financial_value(df, 'retained_earnings')
            }
            
            return balance_sheet
            
        except Exception as e:
            self.logger.error(f"Error processing balance sheet: {str(e)}")
            return {}
    
    async def _process_cash_flow_statement(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Process cash flow statement data."""
        try:
            cash_flow = {
                'period': df['period'].iloc[0] if 'period' in df.columns else 'Unknown',
                'operating_cash_flow': self._extract_financial_value(df, 'operating_cash_flow'),
                'investing_cash_flow': self._extract_financial_value(df, 'investing_cash_flow'),
                'financing_cash_flow': self._extract_financial_value(df, 'financing_cash_flow'),
                'net_cash_flow': self._extract_financial_value(df, 'net_cash_flow'),
                'free_cash_flow': self._extract_financial_value(df, 'free_cash_flow')
            }
            
            return cash_flow
            
        except Exception as e:
            self.logger.error(f"Error processing cash flow statement: {str(e)}")
            return {}
    
    def _extract_financial_value(self, df: pd.DataFrame, column_name: str) -> float:
        """Extract financial value from dataframe."""
        try:
            if column_name in df.columns:
                # Get the first non-null value
                value = df[column_name].dropna().iloc[0] if not df[column_name].dropna().empty else 0.0
                return float(value) if pd.notna(value) else 0.0
            return 0.0
        except Exception:
            return 0.0
    
    async def _calculate_financial_ratios(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate financial ratios from the dataset."""
        try:
            ratios = {
                'liquidity': {},
                'profitability': {},
                'leverage': {},
                'efficiency': {}
            }
            
            # Group by company for ratio calculations
            if 'company_name' in df.columns:
                for company, company_df in df.groupby('company_name'):
                    company_ratios = await self._calculate_company_ratios(company_df)
                    ratios[company] = company_ratios
            
            return ratios
            
        except Exception as e:
            self.logger.error(f"Error calculating financial ratios: {str(e)}")
            return {}
    
    async def _calculate_company_ratios(self, company_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate ratios for a specific company."""
        try:
            ratios = {}
            
            # Extract key financial metrics
            revenue = self._extract_financial_value(company_df, 'revenue')
            net_income = self._extract_financial_value(company_df, 'net_income')
            total_assets = self._extract_financial_value(company_df, 'total_assets')
            total_liabilities = self._extract_financial_value(company_df, 'total_liabilities')
            total_equity = self._extract_financial_value(company_df, 'total_equity')
            current_assets = self._extract_financial_value(company_df, 'current_assets')
            current_liabilities = self._extract_financial_value(company_df, 'current_liabilities')
            
            # Liquidity ratios
            if current_liabilities > 0:
                ratios['current_ratio'] = current_assets / current_liabilities
            else:
                ratios['current_ratio'] = 0.0
            
            # Profitability ratios
            if revenue > 0:
                ratios['net_margin'] = net_income / revenue
            else:
                ratios['net_margin'] = 0.0
            
            if total_assets > 0:
                ratios['roa'] = net_income / total_assets
            else:
                ratios['roa'] = 0.0
            
            if total_equity > 0:
                ratios['roe'] = net_income / total_equity
            else:
                ratios['roe'] = 0.0
            
            # Leverage ratios
            if total_equity > 0:
                ratios['debt_to_equity'] = total_liabilities / total_equity
            else:
                ratios['debt_to_equity'] = 0.0
            
            if total_assets > 0:
                ratios['debt_ratio'] = total_liabilities / total_assets
            else:
                ratios['debt_ratio'] = 0.0
            
            return ratios
            
        except Exception as e:
            self.logger.error(f"Error calculating company ratios: {str(e)}")
            return {}
    
    async def _analyze_financial_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze financial trends across the dataset."""
        try:
            trends = {
                'sector_performance': {},
                'industry_benchmarks': {},
                'market_trends': {}
            }
            
            # Analyze by sector if available
            if 'sector' in df.columns:
                for sector, sector_df in df.groupby('sector'):
                    sector_trends = await self._analyze_sector_trends(sector_df)
                    trends['sector_performance'][sector] = sector_trends
            
            # Calculate industry benchmarks
            trends['industry_benchmarks'] = await self._calculate_industry_benchmarks(df)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing financial trends: {str(e)}")
            return {}
    
    async def _analyze_sector_trends(self, sector_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends for a specific sector."""
        try:
            trends = {
                'average_revenue': 0.0,
                'average_profit_margin': 0.0,
                'growth_rate': 0.0,
                'volatility': 0.0
            }
            
            # Calculate sector averages
            if 'revenue' in sector_df.columns:
                trends['average_revenue'] = sector_df['revenue'].mean()
            
            if 'net_income' in sector_df.columns and 'revenue' in sector_df.columns:
                profit_margins = sector_df['net_income'] / sector_df['revenue']
                trends['average_profit_margin'] = profit_margins.mean()
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing sector trends: {str(e)}")
            return {}
    
    async def _calculate_industry_benchmarks(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate industry benchmarks."""
        try:
            benchmarks = {}
            
            # Calculate key financial metrics
            if 'revenue' in df.columns:
                benchmarks['median_revenue'] = df['revenue'].median()
                benchmarks['revenue_75th_percentile'] = df['revenue'].quantile(0.75)
                benchmarks['revenue_25th_percentile'] = df['revenue'].quantile(0.25)
            
            if 'net_income' in df.columns and 'revenue' in df.columns:
                profit_margins = df['net_income'] / df['revenue']
                benchmarks['median_profit_margin'] = profit_margins.median()
                benchmarks['profit_margin_75th_percentile'] = profit_margins.quantile(0.75)
                benchmarks['profit_margin_25th_percentile'] = profit_margins.quantile(0.25)
            
            return benchmarks
            
        except Exception as e:
            self.logger.error(f"Error calculating industry benchmarks: {str(e)}")
            return {}
    
    async def get_company_analysis(self, company_name: str) -> Dict[str, Any]:
        """Get comprehensive analysis for a specific company."""
        try:
            if not self.processed_data or 'companies' not in self.processed_data:
                return {"error": "No processed data available"}
            
            if company_name not in self.processed_data['companies']:
                return {"error": f"Company {company_name} not found in dataset"}
            
            company_data = self.processed_data['companies'][company_name]
            
            # Add additional analysis
            analysis = {
                'company_info': {
                    'name': company_data.get('name', 'Unknown'),
                    'ticker': company_data.get('ticker', 'Unknown'),
                    'sector': company_data.get('sector', 'Unknown')
                },
                'financial_statements': company_data.get('statements', {}),
                'ratios': company_data.get('ratios', {}),
                'trends': company_data.get('trends', {}),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error getting company analysis: {str(e)}")
            return {"error": str(e)}
    
    async def get_sector_analysis(self, sector: str) -> Dict[str, Any]:
        """Get analysis for a specific sector."""
        try:
            if not self.processed_data or 'trends' not in self.processed_data:
                return {"error": "No processed data available"}
            
            sector_trends = self.processed_data['trends'].get('sector_performance', {}).get(sector, {})
            
            analysis = {
                'sector': sector,
                'performance_metrics': sector_trends,
                'benchmarks': self.processed_data['trends'].get('industry_benchmarks', {}),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error getting sector analysis: {str(e)}")
            return {"error": str(e)}
    
    async def export_processed_data(self, output_path: str) -> bool:
        """Export processed data to JSON file."""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            export_data = {
                'processed_data': self.processed_data,
                'metadata': self.metadata,
                'export_timestamp': datetime.now().isoformat()
            }
            
            async with aiofiles.open(output_file, 'w') as f:
                await f.write(json.dumps(export_data, indent=2, default=str))
            
            self.logger.info(f"Processed data exported to {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting processed data: {str(e)}")
            return False
