"""
Dataset Integration Service for FinMDA-Bot.
Integrates multiple financial datasets and provides unified access.
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

from app.services.sec_dataset_processor import SECDatasetProcessor
from app.services.financial_datasets import FinancialDatasetsManager
from app.services.enhanced_guardrails import EnhancedGuardrailsService
from app.services.enhanced_evaluator import EnhancedEvaluator

class DatasetIntegrationService:
    """Service for integrating and managing multiple financial datasets."""
    
    def __init__(self, datasets_path: str = "data/financial_datasets"):
        self.logger = logging.getLogger(__name__)
        self.datasets_path = Path(datasets_path)
        self.datasets_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.sec_processor = SECDatasetProcessor(str(self.datasets_path / "sec_financial_statements"))
        self.datasets_manager = FinancialDatasetsManager(str(self.datasets_path))
        self.guardrails = EnhancedGuardrailsService()
        self.evaluator = EnhancedEvaluator()
        
        # Dataset registry
        self.registered_datasets = {}
        self.dataset_metadata = {}
        
    async def register_dataset(self, dataset_name: str, dataset_config: Dict[str, Any]) -> bool:
        """Register a new dataset configuration."""
        try:
            self.registered_datasets[dataset_name] = dataset_config
            self.dataset_metadata[dataset_name] = {
                'registered_at': datetime.now().isoformat(),
                'status': 'registered',
                'config': dataset_config
            }
            
            self.logger.info(f"Dataset {dataset_name} registered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering dataset {dataset_name}: {str(e)}")
            return False
    
    async def load_all_datasets(self) -> Dict[str, Any]:
        """Load all registered datasets."""
        try:
            load_results = {}
            
            # Load SEC dataset
            if 'sec_financial_statements' in self.registered_datasets:
                sec_result = await self.sec_processor.load_dataset()
                load_results['sec_financial_statements'] = {
                    'status': 'loaded',
                    'data': sec_result,
                    'metadata': self.sec_processor.metadata
                }
            
            # Load other datasets through datasets manager
            for dataset_name in self.registered_datasets:
                if dataset_name != 'sec_financial_statements':
                    try:
                        dataset_result = await self.datasets_manager.load_dataset(dataset_name)
                        load_results[dataset_name] = {
                            'status': 'loaded',
                            'data': dataset_result
                        }
                    except Exception as e:
                        load_results[dataset_name] = {
                            'status': 'error',
                            'error': str(e)
                        }
            
            return load_results
            
        except Exception as e:
            self.logger.error(f"Error loading datasets: {str(e)}")
            return {}
    
    async def get_unified_financial_data(self, company_name: str = None, 
                                       sector: str = None, 
                                       date_range: tuple = None) -> Dict[str, Any]:
        """Get unified financial data from all loaded datasets."""
        try:
            unified_data = {
                'company_data': {},
                'sector_data': {},
                'market_data': {},
                'economic_data': {},
                'metadata': {
                    'query_timestamp': datetime.now().isoformat(),
                    'filters': {
                        'company_name': company_name,
                        'sector': sector,
                        'date_range': date_range
                    }
                }
            }
            
            # Get SEC data
            if hasattr(self.sec_processor, 'processed_data') and self.sec_processor.processed_data:
                if company_name:
                    company_data = await self.sec_processor.get_company_analysis(company_name)
                    unified_data['company_data']['sec'] = company_data
                
                if sector:
                    sector_data = await self.sec_processor.get_sector_analysis(sector)
                    unified_data['sector_data']['sec'] = sector_data
            
            # Get data from other datasets
            for dataset_name, dataset_data in self.datasets_manager.loaded_datasets.items():
                if 'data' in dataset_data and hasattr(dataset_data['data'], 'columns'):
                    # Filter data based on criteria
                    filtered_data = self._filter_dataset_data(
                        dataset_data['data'], company_name, sector, date_range
                    )
                    
                    if dataset_name in ['yahoo_finance', 'quandl_financial_data']:
                        unified_data['market_data'][dataset_name] = filtered_data
                    elif dataset_name in ['fred_economic_data', 'world_bank_data']:
                        unified_data['economic_data'][dataset_name] = filtered_data
            
            return unified_data
            
        except Exception as e:
            self.logger.error(f"Error getting unified financial data: {str(e)}")
            return {}
    
    def _filter_dataset_data(self, df, company_name: str = None, 
                           sector: str = None, date_range: tuple = None):
        """Filter dataset data based on criteria."""
        try:
            filtered_df = df.copy()
            
            # Filter by company name
            if company_name and 'company_name' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['company_name'].str.contains(company_name, case=False, na=False)]
            
            # Filter by sector
            if sector and 'sector' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['sector'].str.contains(sector, case=False, na=False)]
            
            # Filter by date range
            if date_range and 'date' in filtered_df.columns:
                start_date, end_date = date_range
                filtered_df['date'] = pd.to_datetime(filtered_df['date'], errors='coerce')
                filtered_df = filtered_df[
                    (filtered_df['date'] >= start_date) & 
                    (filtered_df['date'] <= end_date)
                ]
            
            return filtered_df.to_dict('records')
            
        except Exception as e:
            self.logger.error(f"Error filtering dataset data: {str(e)}")
            return []
    
    async def validate_data_quality(self, dataset_name: str) -> Dict[str, Any]:
        """Validate data quality for a specific dataset."""
        try:
            validation_result = {
                'dataset_name': dataset_name,
                'validation_timestamp': datetime.now().isoformat(),
                'quality_score': 0.0,
                'issues': [],
                'recommendations': []
            }
            
            # Get dataset data
            if dataset_name == 'sec_financial_statements':
                dataset_data = self.sec_processor.processed_data
            else:
                dataset_data = self.datasets_manager.loaded_datasets.get(dataset_name, {})
            
            if not dataset_data:
                validation_result['issues'].append("Dataset not loaded")
                return validation_result
            
            # Validate data quality
            quality_metrics = await self._assess_data_quality(dataset_data)
            validation_result['quality_score'] = quality_metrics.get('overall_score', 0.0)
            validation_result['quality_metrics'] = quality_metrics
            
            # Generate recommendations
            validation_result['recommendations'] = await self._generate_quality_recommendations(quality_metrics)
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating data quality: {str(e)}")
            return {'error': str(e)}
    
    async def _assess_data_quality(self, dataset_data: Dict[str, Any]) -> Dict[str, float]:
        """Assess data quality metrics."""
        try:
            quality_metrics = {
                'completeness': 0.0,
                'consistency': 0.0,
                'accuracy': 0.0,
                'timeliness': 0.0,
                'overall_score': 0.0
            }
            
            # Calculate completeness
            if 'data' in dataset_data and hasattr(dataset_data['data'], 'isnull'):
                total_cells = dataset_data['data'].size
                non_null_cells = dataset_data['data'].count().sum()
                quality_metrics['completeness'] = non_null_cells / total_cells if total_cells > 0 else 0.0
            
            # Calculate consistency
            if 'data' in dataset_data and hasattr(dataset_data['data'], 'duplicated'):
                duplicate_rows = dataset_data['data'].duplicated().sum()
                total_rows = len(dataset_data['data'])
                quality_metrics['consistency'] = 1.0 - (duplicate_rows / total_rows) if total_rows > 0 else 0.0
            
            # Calculate overall score
            quality_metrics['overall_score'] = (
                quality_metrics['completeness'] * 0.4 +
                quality_metrics['consistency'] * 0.3 +
                quality_metrics['accuracy'] * 0.2 +
                quality_metrics['timeliness'] * 0.1
            )
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Error assessing data quality: {str(e)}")
            return {}
    
    async def _generate_quality_recommendations(self, quality_metrics: Dict[str, float]) -> List[str]:
        """Generate recommendations based on quality metrics."""
        recommendations = []
        
        if quality_metrics.get('completeness', 0) < 0.8:
            recommendations.append("Data completeness is low. Consider data imputation or additional data sources.")
        
        if quality_metrics.get('consistency', 0) < 0.9:
            recommendations.append("Data consistency issues detected. Review for duplicate or conflicting records.")
        
        if quality_metrics.get('overall_score', 0) < 0.7:
            recommendations.append("Overall data quality is below recommended threshold. Review data sources and processing.")
        
        return recommendations
    
    async def run_comprehensive_analysis(self, analysis_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive analysis across all datasets."""
        try:
            analysis_result = {
                'analysis_timestamp': datetime.now().isoformat(),
                'config': analysis_config,
                'results': {},
                'quality_assessment': {},
                'recommendations': []
            }
            
            # Load all datasets
            load_results = await self.load_all_datasets()
            analysis_result['dataset_loading'] = load_results
            
            # Get unified data
            unified_data = await self.get_unified_financial_data(
                company_name=analysis_config.get('company_name'),
                sector=analysis_config.get('sector'),
                date_range=analysis_config.get('date_range')
            )
            analysis_result['unified_data'] = unified_data
            
            # Validate data quality
            quality_results = {}
            for dataset_name in self.registered_datasets:
                quality_result = await self.validate_data_quality(dataset_name)
                quality_results[dataset_name] = quality_result
            analysis_result['quality_assessment'] = quality_results
            
            # Generate recommendations
            analysis_result['recommendations'] = await self._generate_analysis_recommendations(
                unified_data, quality_results
            )
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error running comprehensive analysis: {str(e)}")
            return {'error': str(e)}
    
    async def _generate_analysis_recommendations(self, unified_data: Dict[str, Any], 
                                               quality_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # Check data availability
        if not unified_data.get('company_data'):
            recommendations.append("No company-specific data available. Consider loading SEC dataset.")
        
        if not unified_data.get('market_data'):
            recommendations.append("No market data available. Consider loading Yahoo Finance or Quandl data.")
        
        if not unified_data.get('economic_data'):
            recommendations.append("No economic data available. Consider loading FRED or World Bank data.")
        
        # Check data quality
        for dataset_name, quality_result in quality_results.items():
            if quality_result.get('quality_score', 0) < 0.7:
                recommendations.append(f"Data quality for {dataset_name} is below threshold. Review data source.")
        
        return recommendations
    
    async def export_analysis_results(self, analysis_results: Dict[str, Any], 
                                    output_path: str) -> bool:
        """Export analysis results to file."""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            export_data = {
                'analysis_results': analysis_results,
                'export_timestamp': datetime.now().isoformat(),
                'metadata': {
                    'total_datasets': len(self.registered_datasets),
                    'loaded_datasets': list(self.datasets_manager.loaded_datasets.keys())
                }
            }
            
            async with aiofiles.open(output_file, 'w') as f:
                await f.write(json.dumps(export_data, indent=2, default=str))
            
            self.logger.info(f"Analysis results exported to {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting analysis results: {str(e)}")
            return False
