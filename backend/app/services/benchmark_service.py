"""
Benchmarking service for competitive and industry analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
import requests
from bs4 import BeautifulSoup

from app.config import settings


class BenchmarkService:
    """Service for competitive and industry benchmarking."""
    
    def __init__(self):
        """Initialize benchmark service."""
        self.logger = logging.getLogger(__name__)
        self.industry_benchmarks = {}
        self.competitor_data = {}
        
        # Industry benchmark data (mock data for demonstration)
        self._initialize_benchmark_data()
    
    def _initialize_benchmark_data(self):
        """Initialize benchmark data for different industries."""
        self.industry_benchmarks = {
            'technology': {
                'current_ratio': {'mean': 2.5, 'median': 2.2, 'p25': 1.8, 'p75': 3.1},
                'quick_ratio': {'mean': 2.0, 'median': 1.8, 'p25': 1.4, 'p75': 2.6},
                'debt_to_equity': {'mean': 0.3, 'median': 0.2, 'p25': 0.1, 'p75': 0.4},
                'gross_margin': {'mean': 0.65, 'median': 0.68, 'p25': 0.55, 'p75': 0.75},
                'net_margin': {'mean': 0.12, 'median': 0.10, 'p25': 0.05, 'p75': 0.18},
                'roe': {'mean': 0.15, 'median': 0.12, 'p25': 0.08, 'p75': 0.20},
                'roa': {'mean': 0.08, 'median': 0.06, 'p25': 0.03, 'p75': 0.12}
            },
            'manufacturing': {
                'current_ratio': {'mean': 1.8, 'median': 1.7, 'p25': 1.4, 'p75': 2.2},
                'quick_ratio': {'mean': 1.2, 'median': 1.1, 'p25': 0.9, 'p75': 1.5},
                'debt_to_equity': {'mean': 0.5, 'median': 0.4, 'p25': 0.2, 'p75': 0.7},
                'gross_margin': {'mean': 0.35, 'median': 0.33, 'p25': 0.25, 'p75': 0.45},
                'net_margin': {'mean': 0.08, 'median': 0.06, 'p25': 0.02, 'p75': 0.12},
                'roe': {'mean': 0.12, 'median': 0.10, 'p25': 0.05, 'p75': 0.18},
                'roa': {'mean': 0.06, 'median': 0.05, 'p25': 0.02, 'p75': 0.09}
            },
            'retail': {
                'current_ratio': {'mean': 1.5, 'median': 1.4, 'p25': 1.1, 'p75': 1.8},
                'quick_ratio': {'mean': 0.8, 'median': 0.7, 'p25': 0.5, 'p75': 1.1},
                'debt_to_equity': {'mean': 0.4, 'median': 0.3, 'p25': 0.1, 'p75': 0.6},
                'gross_margin': {'mean': 0.25, 'median': 0.24, 'p25': 0.18, 'p75': 0.32},
                'net_margin': {'mean': 0.04, 'median': 0.03, 'p25': 0.01, 'p75': 0.07},
                'roe': {'mean': 0.10, 'median': 0.08, 'p25': 0.03, 'p75': 0.15},
                'roa': {'mean': 0.05, 'median': 0.04, 'p25': 0.01, 'p75': 0.08}
            },
            'healthcare': {
                'current_ratio': {'mean': 2.2, 'median': 2.0, 'p25': 1.6, 'p75': 2.8},
                'quick_ratio': {'mean': 1.8, 'median': 1.6, 'p25': 1.2, 'p75': 2.4},
                'debt_to_equity': {'mean': 0.3, 'median': 0.2, 'p25': 0.1, 'p75': 0.4},
                'gross_margin': {'mean': 0.45, 'median': 0.43, 'p25': 0.35, 'p75': 0.55},
                'net_margin': {'mean': 0.08, 'median': 0.06, 'p25': 0.02, 'p75': 0.12},
                'roe': {'mean': 0.12, 'median': 0.10, 'p25': 0.05, 'p75': 0.18},
                'roa': {'mean': 0.06, 'median': 0.05, 'p25': 0.02, 'p75': 0.09}
            }
        }
    
    async def benchmark_company(
        self, 
        company_data: Dict[str, Any], 
        industry: str = 'technology',
        company_size: str = 'medium'
    ) -> Dict[str, Any]:
        """Benchmark a company against industry standards."""
        
        benchmark_results = {
            'company_name': company_data.get('company_name', 'Unknown'),
            'industry': industry,
            'company_size': company_size,
            'benchmark_date': datetime.utcnow().isoformat(),
            'ratios_analysis': {},
            'performance_score': 0.0,
            'rankings': {},
            'recommendations': [],
            'strengths': [],
            'weaknesses': []
        }
        
        try:
            # Get industry benchmarks
            if industry not in self.industry_benchmarks:
                benchmark_results['error'] = f"Industry '{industry}' not supported"
                return benchmark_results
            
            industry_benchmarks = self.industry_benchmarks[industry]
            
            # Calculate company ratios
            company_ratios = self._calculate_company_ratios(company_data)
            
            # Analyze each ratio
            total_score = 0
            ratio_count = 0
            
            for ratio_name, company_value in company_ratios.items():
                if ratio_name in industry_benchmarks:
                    benchmark = industry_benchmarks[ratio_name]
                    analysis = self._analyze_ratio_performance(company_value, benchmark, ratio_name)
                    
                    benchmark_results['ratios_analysis'][ratio_name] = analysis
                    total_score += analysis['score']
                    ratio_count += 1
            
            # Calculate overall performance score
            if ratio_count > 0:
                benchmark_results['performance_score'] = total_score / ratio_count
            
            # Generate rankings
            benchmark_results['rankings'] = self._generate_rankings(benchmark_results['ratios_analysis'])
            
            # Generate recommendations
            benchmark_results['recommendations'] = self._generate_recommendations(
                benchmark_results['ratios_analysis'], industry
            )
            
            # Identify strengths and weaknesses
            strengths_weaknesses = self._identify_strengths_weaknesses(benchmark_results['ratios_analysis'])
            benchmark_results['strengths'] = strengths_weaknesses['strengths']
            benchmark_results['weaknesses'] = strengths_weaknesses['weaknesses']
            
        except Exception as e:
            self.logger.error(f"Error benchmarking company: {str(e)}")
            benchmark_results['error'] = str(e)
        
        return benchmark_results
    
    def _calculate_company_ratios(self, company_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate financial ratios for the company."""
        ratios = {}
        
        try:
            # Liquidity ratios
            if 'current_assets' in company_data and 'current_liabilities' in company_data:
                if company_data['current_liabilities'] > 0:
                    ratios['current_ratio'] = company_data['current_assets'] / company_data['current_liabilities']
            
            if 'current_assets' in company_data and 'inventory' in company_data and 'current_liabilities' in company_data:
                if company_data['current_liabilities'] > 0:
                    ratios['quick_ratio'] = (company_data['current_assets'] - company_data['inventory']) / company_data['current_liabilities']
            
            # Leverage ratios
            if 'total_debt' in company_data and 'total_equity' in company_data:
                if company_data['total_equity'] > 0:
                    ratios['debt_to_equity'] = company_data['total_debt'] / company_data['total_equity']
            
            # Profitability ratios
            if 'revenue' in company_data and 'cost_of_goods_sold' in company_data:
                if company_data['revenue'] > 0:
                    ratios['gross_margin'] = (company_data['revenue'] - company_data['cost_of_goods_sold']) / company_data['revenue']
            
            if 'revenue' in company_data and 'net_income' in company_data:
                if company_data['revenue'] > 0:
                    ratios['net_margin'] = company_data['net_income'] / company_data['revenue']
            
            if 'net_income' in company_data and 'total_equity' in company_data:
                if company_data['total_equity'] > 0:
                    ratios['roe'] = company_data['net_income'] / company_data['total_equity']
            
            if 'net_income' in company_data and 'total_assets' in company_data:
                if company_data['total_assets'] > 0:
                    ratios['roa'] = company_data['net_income'] / company_data['total_assets']
        
        except Exception as e:
            self.logger.error(f"Error calculating company ratios: {str(e)}")
        
        return ratios
    
    def _analyze_ratio_performance(
        self, 
        company_value: float, 
        benchmark: Dict[str, float], 
        ratio_name: str
    ) -> Dict[str, Any]:
        """Analyze how a company's ratio performs against industry benchmarks."""
        
        analysis = {
            'company_value': company_value,
            'industry_mean': benchmark['mean'],
            'industry_median': benchmark['median'],
            'industry_p25': benchmark['p25'],
            'industry_p75': benchmark['p75'],
            'percentile': 0.0,
            'performance': 'average',
            'score': 0.0,
            'interpretation': ''
        }
        
        try:
            # Calculate percentile
            if company_value <= benchmark['p25']:
                analysis['percentile'] = 25
                analysis['performance'] = 'below_average'
                analysis['score'] = 0.3
            elif company_value <= benchmark['median']:
                analysis['percentile'] = 50
                analysis['performance'] = 'average'
                analysis['score'] = 0.6
            elif company_value <= benchmark['p75']:
                analysis['percentile'] = 75
                analysis['performance'] = 'above_average'
                analysis['score'] = 0.8
            else:
                analysis['percentile'] = 90
                analysis['performance'] = 'excellent'
                analysis['score'] = 1.0
            
            # Generate interpretation
            analysis['interpretation'] = self._generate_ratio_interpretation(
                ratio_name, company_value, benchmark, analysis['performance']
            )
        
        except Exception as e:
            self.logger.error(f"Error analyzing ratio performance: {str(e)}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _generate_ratio_interpretation(
        self, 
        ratio_name: str, 
        company_value: float, 
        benchmark: Dict[str, float], 
        performance: str
    ) -> str:
        """Generate interpretation for a ratio's performance."""
        
        interpretations = {
            'current_ratio': {
                'below_average': f"Current ratio of {company_value:.2f} is below industry average ({benchmark['mean']:.2f}). Consider improving liquidity.",
                'average': f"Current ratio of {company_value:.2f} is in line with industry average ({benchmark['mean']:.2f}).",
                'above_average': f"Current ratio of {company_value:.2f} is above industry average ({benchmark['mean']:.2f}). Good liquidity position.",
                'excellent': f"Current ratio of {company_value:.2f} significantly exceeds industry average ({benchmark['mean']:.2f}). Excellent liquidity."
            },
            'quick_ratio': {
                'below_average': f"Quick ratio of {company_value:.2f} is below industry average ({benchmark['mean']:.2f}). Consider reducing inventory or increasing cash.",
                'average': f"Quick ratio of {company_value:.2f} is in line with industry average ({benchmark['mean']:.2f}).",
                'above_average': f"Quick ratio of {company_value:.2f} is above industry average ({benchmark['mean']:.2f}). Strong liquidity position.",
                'excellent': f"Quick ratio of {company_value:.2f} significantly exceeds industry average ({benchmark['mean']:.2f}). Excellent liquidity."
            },
            'debt_to_equity': {
                'below_average': f"Debt-to-equity ratio of {company_value:.2f} is below industry average ({benchmark['mean']:.2f}). Consider leveraging for growth.",
                'average': f"Debt-to-equity ratio of {company_value:.2f} is in line with industry average ({benchmark['mean']:.2f}).",
                'above_average': f"Debt-to-equity ratio of {company_value:.2f} is above industry average ({benchmark['mean']:.2f}). Consider reducing debt.",
                'excellent': f"Debt-to-equity ratio of {company_value:.2f} is significantly below industry average ({benchmark['mean']:.2f}). Conservative capital structure."
            },
            'gross_margin': {
                'below_average': f"Gross margin of {company_value:.1%} is below industry average ({benchmark['mean']:.1%}). Consider improving pricing or reducing costs.",
                'average': f"Gross margin of {company_value:.1%} is in line with industry average ({benchmark['mean']:.1%}).",
                'above_average': f"Gross margin of {company_value:.1%} is above industry average ({benchmark['mean']:.1%}). Strong pricing power.",
                'excellent': f"Gross margin of {company_value:.1%} significantly exceeds industry average ({benchmark['mean']:.1%}). Excellent profitability."
            },
            'net_margin': {
                'below_average': f"Net margin of {company_value:.1%} is below industry average ({benchmark['mean']:.1%}). Consider improving operational efficiency.",
                'average': f"Net margin of {company_value:.1%} is in line with industry average ({benchmark['mean']:.1%}).",
                'above_average': f"Net margin of {company_value:.1%} is above industry average ({benchmark['mean']:.1%}). Strong operational efficiency.",
                'excellent': f"Net margin of {company_value:.1%} significantly exceeds industry average ({benchmark['mean']:.1%}). Excellent profitability."
            },
            'roe': {
                'below_average': f"ROE of {company_value:.1%} is below industry average ({benchmark['mean']:.1%}). Consider improving profitability or efficiency.",
                'average': f"ROE of {company_value:.1%} is in line with industry average ({benchmark['mean']:.1%}).",
                'above_average': f"ROE of {company_value:.1%} is above industry average ({benchmark['mean']:.1%}). Strong shareholder returns.",
                'excellent': f"ROE of {company_value:.1%} significantly exceeds industry average ({benchmark['mean']:.1%}). Excellent shareholder returns."
            },
            'roa': {
                'below_average': f"ROA of {company_value:.1%} is below industry average ({benchmark['mean']:.1%}). Consider improving asset utilization.",
                'average': f"ROA of {company_value:.1%} is in line with industry average ({benchmark['mean']:.1%}).",
                'above_average': f"ROA of {company_value:.1%} is above industry average ({benchmark['mean']:.1%}). Strong asset utilization.",
                'excellent': f"ROA of {company_value:.1%} significantly exceeds industry average ({benchmark['mean']:.1%}). Excellent asset utilization."
            }
        }
        
        return interpretations.get(ratio_name, {}).get(performance, f"Ratio {ratio_name} performance: {performance}")
    
    def _generate_rankings(self, ratios_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate rankings based on ratio performance."""
        rankings = {
            'overall_rank': 'average',
            'liquidity_rank': 'average',
            'profitability_rank': 'average',
            'leverage_rank': 'average',
            'efficiency_rank': 'average'
        }
        
        try:
            # Calculate category scores
            liquidity_scores = []
            profitability_scores = []
            leverage_scores = []
            efficiency_scores = []
            
            for ratio_name, analysis in ratios_analysis.items():
                score = analysis.get('score', 0)
                
                if ratio_name in ['current_ratio', 'quick_ratio']:
                    liquidity_scores.append(score)
                elif ratio_name in ['gross_margin', 'net_margin', 'roe']:
                    profitability_scores.append(score)
                elif ratio_name in ['debt_to_equity']:
                    leverage_scores.append(score)
                elif ratio_name in ['roa']:
                    efficiency_scores.append(score)
            
            # Calculate category ranks
            if liquidity_scores:
                avg_liquidity = np.mean(liquidity_scores)
                rankings['liquidity_rank'] = self._score_to_rank(avg_liquidity)
            
            if profitability_scores:
                avg_profitability = np.mean(profitability_scores)
                rankings['profitability_rank'] = self._score_to_rank(avg_profitability)
            
            if leverage_scores:
                avg_leverage = np.mean(leverage_scores)
                rankings['leverage_rank'] = self._score_to_rank(avg_leverage)
            
            if efficiency_scores:
                avg_efficiency = np.mean(efficiency_scores)
                rankings['efficiency_rank'] = self._score_to_rank(avg_efficiency)
            
            # Calculate overall rank
            all_scores = liquidity_scores + profitability_scores + leverage_scores + efficiency_scores
            if all_scores:
                overall_score = np.mean(all_scores)
                rankings['overall_rank'] = self._score_to_rank(overall_score)
        
        except Exception as e:
            self.logger.error(f"Error generating rankings: {str(e)}")
        
        return rankings
    
    def _score_to_rank(self, score: float) -> str:
        """Convert score to rank."""
        if score >= 0.8:
            return 'excellent'
        elif score >= 0.6:
            return 'good'
        elif score >= 0.4:
            return 'average'
        else:
            return 'below_average'
    
    def _generate_recommendations(self, ratios_analysis: Dict[str, Any], industry: str) -> List[str]:
        """Generate recommendations based on benchmark analysis."""
        recommendations = []
        
        try:
            # Analyze each ratio and generate recommendations
            for ratio_name, analysis in ratios_analysis.items():
                performance = analysis.get('performance', 'average')
                company_value = analysis.get('company_value', 0)
                industry_mean = analysis.get('industry_mean', 0)
                
                if performance == 'below_average':
                    if ratio_name == 'current_ratio':
                        recommendations.append("Improve liquidity by increasing current assets or reducing current liabilities")
                    elif ratio_name == 'quick_ratio':
                        recommendations.append("Improve quick ratio by reducing inventory or increasing cash and receivables")
                    elif ratio_name == 'debt_to_equity':
                        recommendations.append("Consider increasing leverage to match industry standards for growth")
                    elif ratio_name in ['gross_margin', 'net_margin']:
                        recommendations.append("Improve profitability through better pricing or cost management")
                    elif ratio_name in ['roe', 'roa']:
                        recommendations.append("Improve return on equity/assets through better operational efficiency")
                
                elif performance == 'excellent':
                    if ratio_name == 'current_ratio':
                        recommendations.append("Excellent liquidity position - consider optimizing working capital")
                    elif ratio_name in ['gross_margin', 'net_margin']:
                        recommendations.append("Excellent profitability - consider reinvesting for growth")
                    elif ratio_name in ['roe', 'roa']:
                        recommendations.append("Excellent returns - consider expanding operations")
            
            # Add industry-specific recommendations
            if industry == 'technology':
                recommendations.append("Focus on innovation and R&D investment to maintain competitive advantage")
            elif industry == 'manufacturing':
                recommendations.append("Optimize supply chain and production efficiency")
            elif industry == 'retail':
                recommendations.append("Focus on inventory turnover and customer experience")
            elif industry == 'healthcare':
                recommendations.append("Maintain regulatory compliance and patient care quality")
        
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
        
        return recommendations
    
    def _identify_strengths_weaknesses(self, ratios_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Identify company strengths and weaknesses."""
        strengths = []
        weaknesses = []
        
        try:
            for ratio_name, analysis in ratios_analysis.items():
                performance = analysis.get('performance', 'average')
                company_value = analysis.get('company_value', 0)
                
                if performance in ['above_average', 'excellent']:
                    strengths.append(f"{ratio_name.replace('_', ' ').title()}: {company_value:.2f} (above industry average)")
                elif performance == 'below_average':
                    weaknesses.append(f"{ratio_name.replace('_', ' ').title()}: {company_value:.2f} (below industry average)")
        
        except Exception as e:
            self.logger.error(f"Error identifying strengths/weaknesses: {str(e)}")
        
        return {'strengths': strengths, 'weaknesses': weaknesses}
    
    async def compare_with_competitors(
        self, 
        company_data: Dict[str, Any], 
        competitor_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare company with competitors."""
        
        comparison = {
            'company_name': company_data.get('company_name', 'Unknown'),
            'competitors': [],
            'comparison_metrics': {},
            'competitive_position': 'average',
            'generated_at': datetime.utcnow().isoformat()
        }
        
        try:
            # Calculate company ratios
            company_ratios = self._calculate_company_ratios(company_data)
            
            # Calculate competitor ratios
            competitor_ratios = []
            for competitor in competitor_data:
                competitor_ratio = self._calculate_company_ratios(competitor)
                competitor_ratio['company_name'] = competitor.get('company_name', 'Unknown')
                competitor_ratios.append(competitor_ratio)
            
            comparison['competitors'] = competitor_ratios
            
            # Compare key metrics
            comparison['comparison_metrics'] = self._compare_metrics(company_ratios, competitor_ratios)
            
            # Determine competitive position
            comparison['competitive_position'] = self._determine_competitive_position(
                company_ratios, competitor_ratios
            )
        
        except Exception as e:
            self.logger.error(f"Error comparing with competitors: {str(e)}")
            comparison['error'] = str(e)
        
        return comparison
    
    def _compare_metrics(self, company_ratios: Dict[str, float], competitor_ratios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare key metrics with competitors."""
        comparison = {}
        
        try:
            # Compare each ratio
            for ratio_name in company_ratios.keys():
                if ratio_name != 'company_name':
                    company_value = company_ratios[ratio_name]
                    competitor_values = [
                        comp[ratio_name] for comp in competitor_ratios 
                        if ratio_name in comp and comp[ratio_name] is not None
                    ]
                    
                    if competitor_values:
                        comparison[ratio_name] = {
                            'company_value': company_value,
                            'competitor_mean': np.mean(competitor_values),
                            'competitor_median': np.median(competitor_values),
                            'competitor_min': np.min(competitor_values),
                            'competitor_max': np.max(competitor_values),
                            'company_rank': self._calculate_rank(company_value, competitor_values)
                        }
        
        except Exception as e:
            self.logger.error(f"Error comparing metrics: {str(e)}")
        
        return comparison
    
    def _calculate_rank(self, company_value: float, competitor_values: List[float]) -> int:
        """Calculate company's rank among competitors."""
        all_values = [company_value] + competitor_values
        sorted_values = sorted(all_values, reverse=True)
        return sorted_values.index(company_value) + 1
    
    def _determine_competitive_position(self, company_ratios: Dict[str, float], competitor_ratios: List[Dict[str, Any]]) -> str:
        """Determine overall competitive position."""
        try:
            total_rank = 0
            ratio_count = 0
            
            for ratio_name in company_ratios.keys():
                if ratio_name != 'company_name':
                    company_value = company_ratios[ratio_name]
                    competitor_values = [
                        comp[ratio_name] for comp in competitor_ratios 
                        if ratio_name in comp and comp[ratio_name] is not None
                    ]
                    
                    if competitor_values:
                        rank = self._calculate_rank(company_value, competitor_values)
                        total_rank += rank
                        ratio_count += 1
            
            if ratio_count > 0:
                avg_rank = total_rank / ratio_count
                if avg_rank <= 1.5:
                    return 'leader'
                elif avg_rank <= 2.5:
                    return 'strong'
                elif avg_rank <= 3.5:
                    return 'average'
                else:
                    return 'weak'
            
        except Exception as e:
            self.logger.error(f"Error determining competitive position: {str(e)}")
        
        return 'average'
    
    async def get_industry_benchmarks(self, industry: str) -> Dict[str, Any]:
        """Get industry benchmarks for a specific industry."""
        if industry in self.industry_benchmarks:
            return self.industry_benchmarks[industry]
        else:
            return {'error': f"Industry '{industry}' not supported"}
    
    async def update_industry_benchmarks(self, industry: str, benchmarks: Dict[str, Any]) -> bool:
        """Update industry benchmarks."""
        try:
            self.industry_benchmarks[industry] = benchmarks
            return True
        except Exception as e:
            self.logger.error(f"Error updating industry benchmarks: {str(e)}")
            return False
