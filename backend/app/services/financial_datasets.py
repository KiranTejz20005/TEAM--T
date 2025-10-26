"""
Financial Datasets Integration for FinMDA-Bot.
Integrates multiple open source financial datasets for comprehensive analysis.
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
import requests
from urllib.parse import urljoin

class FinancialDatasetsManager:
    """Manager for multiple financial datasets."""
    
    def __init__(self, datasets_path: str = "data/financial_datasets"):
        self.logger = logging.getLogger(__name__)
        self.datasets_path = Path(datasets_path)
        self.datasets_path.mkdir(parents=True, exist_ok=True)
        
        # Available datasets configuration
        self.available_datasets = {
            'sec_financial_statements': {
                'name': 'SEC Financial Statement Extracts',
                'source': 'Kaggle',
                'url': 'https://www.kaggle.com/datasets/securities-exchange-commission/financial-statement-extracts',
                'description': 'Financial statement extracts from SEC filings',
                'file_types': ['.csv'],
                'columns': ['company_name', 'ticker', 'sector', 'period', 'revenue', 'net_income', 'total_assets']
            },
            'yahoo_finance': {
                'name': 'Yahoo Finance Data',
                'source': 'Yahoo Finance API',
                'url': 'https://finance.yahoo.com/',
                'description': 'Stock prices, financial metrics, and market data',
                'file_types': ['.csv'],
                'columns': ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
            },
            'fred_economic_data': {
                'name': 'FRED Economic Data',
                'source': 'Federal Reserve Economic Data',
                'url': 'https://fred.stlouisfed.org/',
                'description': 'Economic indicators and macroeconomic data',
                'file_types': ['.csv'],
                'columns': ['date', 'value', 'series_id']
            },
            'quandl_financial_data': {
                'name': 'Quandl Financial Data',
                'source': 'Quandl',
                'url': 'https://www.quandl.com/',
                'description': 'Financial and economic data from various sources',
                'file_types': ['.csv'],
                'columns': ['date', 'value', 'series_name']
            },
            'world_bank_data': {
                'name': 'World Bank Financial Data',
                'source': 'World Bank Open Data',
                'url': 'https://data.worldbank.org/',
                'description': 'Global financial and economic indicators',
                'file_types': ['.csv'],
                'columns': ['country', 'indicator', 'year', 'value']
            }
        }
        
        self.loaded_datasets = {}
        
    async def load_dataset(self, dataset_name: str, file_path: str = None) -> Dict[str, Any]:
        """Load a specific financial dataset."""
        try:
            if dataset_name not in self.available_datasets:
                raise ValueError(f"Dataset {dataset_name} not available")
            
            dataset_config = self.available_datasets[dataset_name]
            
            if file_path:
                dataset_file = Path(file_path)
            else:
                # Look for dataset files in the datasets path
                dataset_files = list(self.datasets_path.glob(f"{dataset_name}*"))
                if not dataset_files:
                    raise FileNotFoundError(f"No files found for dataset {dataset_name}")
                dataset_file = dataset_files[0]
            
            self.logger.info(f"Loading {dataset_name} from {dataset_file}")
            
            # Load the dataset based on file type
            if dataset_file.suffix == '.csv':
                df = pd.read_csv(dataset_file)
            elif dataset_file.suffix == '.json':
                df = pd.read_json(dataset_file)
            elif dataset_file.suffix == '.xlsx':
                df = pd.read_excel(dataset_file)
            else:
                raise ValueError(f"Unsupported file type: {dataset_file.suffix}")
            
            # Process the dataset
            processed_data = await self._process_dataset(df, dataset_name, dataset_config)
            
            self.loaded_datasets[dataset_name] = processed_data
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error loading dataset {dataset_name}: {str(e)}")
            return {}
    
    async def _process_dataset(self, df: pd.DataFrame, dataset_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process a loaded dataset."""
        try:
            processed_data = {
                'name': config['name'],
                'source': config['source'],
                'description': config['description'],
                'total_records': len(df),
                'columns': list(df.columns),
                'data': df,
                'processed_at': datetime.now().isoformat(),
                'statistics': {},
                'insights': {}
            }
            
            # Calculate basic statistics
            processed_data['statistics'] = await self._calculate_dataset_statistics(df, dataset_name)
            
            # Generate insights
            processed_data['insights'] = await self._generate_dataset_insights(df, dataset_name)
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error processing dataset {dataset_name}: {str(e)}")
            return {}
    
    async def _calculate_dataset_statistics(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        """Calculate statistics for a dataset."""
        try:
            stats = {
                'total_records': len(df),
                'total_columns': len(df.columns),
                'missing_values': df.isnull().sum().to_dict(),
                'data_types': df.dtypes.to_dict(),
                'numeric_summary': {},
                'categorical_summary': {}
            }
            
            # Numeric columns summary
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                stats['numeric_summary'] = df[numeric_columns].describe().to_dict()
            
            # Categorical columns summary
            categorical_columns = df.select_dtypes(include=['object']).columns
            if len(categorical_columns) > 0:
                for col in categorical_columns:
                    stats['categorical_summary'][col] = {
                        'unique_values': df[col].nunique(),
                        'most_common': df[col].value_counts().head().to_dict()
                    }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating dataset statistics: {str(e)}")
            return {}
    
    async def _generate_dataset_insights(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        """Generate insights from a dataset."""
        try:
            insights = {
                'data_quality': {},
                'trends': {},
                'anomalies': {},
                'recommendations': []
            }
            
            # Data quality assessment
            insights['data_quality'] = await self._assess_data_quality(df)
            
            # Trend analysis
            insights['trends'] = await self._analyze_trends(df, dataset_name)
            
            # Anomaly detection
            insights['anomalies'] = await self._detect_anomalies(df, dataset_name)
            
            # Generate recommendations
            insights['recommendations'] = await self._generate_recommendations(df, dataset_name)
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating dataset insights: {str(e)}")
            return {}
    
    async def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess data quality of a dataset."""
        try:
            quality_metrics = {
                'completeness': 0.0,
                'consistency': 0.0,
                'accuracy': 0.0,
                'timeliness': 0.0
            }
            
            # Completeness (percentage of non-null values)
            total_cells = df.size
            non_null_cells = df.count().sum()
            quality_metrics['completeness'] = non_null_cells / total_cells if total_cells > 0 else 0.0
            
            # Consistency (check for duplicate rows)
            duplicate_rows = df.duplicated().sum()
            quality_metrics['consistency'] = 1.0 - (duplicate_rows / len(df)) if len(df) > 0 else 0.0
            
            # Accuracy (check for outliers in numeric columns)
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            outlier_count = 0
            total_numeric_values = 0
            
            for col in numeric_columns:
                if df[col].notna().sum() > 0:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                    outlier_count += len(outliers)
                    total_numeric_values += df[col].notna().sum()
            
            quality_metrics['accuracy'] = 1.0 - (outlier_count / total_numeric_values) if total_numeric_values > 0 else 0.0
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Error assessing data quality: {str(e)}")
            return {}
    
    async def _analyze_trends(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        """Analyze trends in a dataset."""
        try:
            trends = {}
            
            # Time-based trend analysis
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df_sorted = df.sort_values('date')
                
                # Analyze trends over time
                numeric_columns = df_sorted.select_dtypes(include=[np.number]).columns
                for col in numeric_columns:
                    if df_sorted[col].notna().sum() > 1:
                        # Calculate trend (simple linear regression slope)
                        x = np.arange(len(df_sorted))
                        y = df_sorted[col].fillna(0)
                        trend_slope = np.polyfit(x, y, 1)[0]
                        trends[f'{col}_trend'] = {
                            'slope': trend_slope,
                            'direction': 'increasing' if trend_slope > 0 else 'decreasing',
                            'strength': abs(trend_slope)
                        }
            
            # Sector/industry trend analysis
            if 'sector' in df.columns:
                sector_trends = {}
                for sector, sector_df in df.groupby('sector'):
                    sector_trends[sector] = {
                        'record_count': len(sector_df),
                        'average_values': sector_df.select_dtypes(include=[np.number]).mean().to_dict()
                    }
                trends['sector_analysis'] = sector_trends
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {str(e)}")
            return {}
    
    async def _detect_anomalies(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        """Detect anomalies in a dataset."""
        try:
            anomalies = {
                'outliers': {},
                'missing_patterns': {},
                'data_inconsistencies': {}
            }
            
            # Detect outliers in numeric columns
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if df[col].notna().sum() > 0:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                    if len(outliers) > 0:
                        anomalies['outliers'][col] = {
                            'count': len(outliers),
                            'percentage': len(outliers) / len(df) * 100,
                            'indices': outliers.index.tolist()
                        }
            
            # Detect missing data patterns
            missing_data = df.isnull().sum()
            if missing_data.sum() > 0:
                anomalies['missing_patterns'] = {
                    'total_missing': missing_data.sum(),
                    'missing_by_column': missing_data.to_dict(),
                    'missing_percentage': (missing_data / len(df) * 100).to_dict()
                }
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {str(e)}")
            return {}
    
    async def _generate_recommendations(self, df: pd.DataFrame, dataset_name: str) -> List[str]:
        """Generate recommendations for dataset usage."""
        try:
            recommendations = []
            
            # Data quality recommendations
            missing_percentage = df.isnull().sum().sum() / df.size * 100
            if missing_percentage > 10:
                recommendations.append(f"High missing data percentage ({missing_percentage:.1f}%). Consider data imputation.")
            
            # Column-specific recommendations
            if 'date' in df.columns:
                recommendations.append("Date column detected. Consider time series analysis.")
            
            if 'sector' in df.columns:
                recommendations.append("Sector column detected. Consider sector-based analysis.")
            
            if 'company_name' in df.columns:
                recommendations.append("Company names detected. Consider company-specific analysis.")
            
            # Numeric data recommendations
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                recommendations.append(f"{len(numeric_columns)} numeric columns available for financial ratio calculations.")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    async def get_dataset_summary(self, dataset_name: str) -> Dict[str, Any]:
        """Get summary of a loaded dataset."""
        try:
            if dataset_name not in self.loaded_datasets:
                return {"error": f"Dataset {dataset_name} not loaded"}
            
            dataset = self.loaded_datasets[dataset_name]
            
            summary = {
                'name': dataset['name'],
                'source': dataset['source'],
                'description': dataset['description'],
                'total_records': dataset['total_records'],
                'columns': dataset['columns'],
                'statistics': dataset['statistics'],
                'insights': dataset['insights'],
                'loaded_at': dataset['processed_at']
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting dataset summary: {str(e)}")
            return {"error": str(e)}
    
    async def compare_datasets(self, dataset_names: List[str]) -> Dict[str, Any]:
        """Compare multiple datasets."""
        try:
            if len(dataset_names) < 2:
                return {"error": "At least 2 datasets required for comparison"}
            
            comparison = {
                'datasets': {},
                'common_columns': [],
                'differences': {},
                'recommendations': []
            }
            
            # Get summaries for all datasets
            for dataset_name in dataset_names:
                if dataset_name in self.loaded_datasets:
                    comparison['datasets'][dataset_name] = await self.get_dataset_summary(dataset_name)
            
            # Find common columns
            all_columns = []
            for dataset_name in dataset_names:
                if dataset_name in self.loaded_datasets:
                    all_columns.append(set(self.loaded_datasets[dataset_name]['columns']))
            
            if all_columns:
                comparison['common_columns'] = list(set.intersection(*all_columns))
            
            # Generate comparison recommendations
            comparison['recommendations'] = await self._generate_comparison_recommendations(dataset_names)
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Error comparing datasets: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_comparison_recommendations(self, dataset_names: List[str]) -> List[str]:
        """Generate recommendations for dataset comparison."""
        try:
            recommendations = []
            
            # Check for complementary datasets
            if 'sec_financial_statements' in dataset_names and 'yahoo_finance' in dataset_names:
                recommendations.append("SEC and Yahoo Finance datasets can be combined for comprehensive financial analysis")
            
            if 'fred_economic_data' in dataset_names:
                recommendations.append("FRED economic data can provide macroeconomic context for financial analysis")
            
            if 'world_bank_data' in dataset_names:
                recommendations.append("World Bank data can provide global economic indicators for international analysis")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating comparison recommendations: {str(e)}")
            return []
    
    async def export_combined_analysis(self, output_path: str) -> bool:
        """Export combined analysis of all loaded datasets."""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            combined_analysis = {
                'datasets': self.loaded_datasets,
                'comparison': await self.compare_datasets(list(self.loaded_datasets.keys())),
                'export_timestamp': datetime.now().isoformat()
            }
            
            async with aiofiles.open(output_file, 'w') as f:
                await f.write(json.dumps(combined_analysis, indent=2, default=str))
            
            self.logger.info(f"Combined analysis exported to {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting combined analysis: {str(e)}")
            return False
