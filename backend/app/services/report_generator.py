"""
Automated report generation service.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
from io import BytesIO
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64

from app.config import settings


class ReportGenerator:
    """Service for generating automated financial reports."""
    
    def __init__(self):
        """Initialize report generator."""
        self.logger = logging.getLogger(__name__)
        self.report_templates = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize report templates."""
        self.report_templates = {
            'executive_summary': {
                'title': 'Executive Summary',
                'sections': ['overview', 'key_metrics', 'financial_highlights', 'recommendations']
            },
            'financial_analysis': {
                'title': 'Financial Analysis Report',
                'sections': ['ratios', 'trends', 'forecasts', 'benchmarks']
            },
            'performance_dashboard': {
                'title': 'Performance Dashboard',
                'sections': ['kpis', 'charts', 'comparisons', 'insights']
            }
        }
    
    async def generate_report(
        self, 
        report_type: str,
        data: Dict[str, Any],
        template: Optional[str] = None,
        format: str = 'html'
    ) -> Dict[str, Any]:
        """Generate a financial report."""
        
        report = {
            'report_id': f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'report_type': report_type,
            'template': template or 'default',
            'format': format,
            'generated_at': datetime.utcnow().isoformat(),
            'content': {},
            'charts': [],
            'tables': [],
            'summary': {}
        }
        
        try:
            if report_type == 'executive_summary':
                report['content'] = await self._generate_executive_summary(data)
            elif report_type == 'financial_analysis':
                report['content'] = await self._generate_financial_analysis(data)
            elif report_type == 'performance_dashboard':
                report['content'] = await self._generate_performance_dashboard(data)
            else:
                report['content'] = await self._generate_custom_report(data, report_type)
            
            # Generate charts
            report['charts'] = await self._generate_charts(data, report_type)
            
            # Generate tables
            report['tables'] = await self._generate_tables(data, report_type)
            
            # Generate summary
            report['summary'] = await self._generate_summary(report['content'])
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            report['error'] = str(e)
        
        return report
    
    async def _generate_executive_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary content."""
        content = {
            'overview': {
                'title': 'Company Overview',
                'content': self._generate_overview_text(data)
            },
            'key_metrics': {
                'title': 'Key Financial Metrics',
                'metrics': self._extract_key_metrics(data)
            },
            'financial_highlights': {
                'title': 'Financial Highlights',
                'highlights': self._generate_financial_highlights(data)
            },
            'recommendations': {
                'title': 'Strategic Recommendations',
                'recommendations': self._generate_recommendations(data)
            }
        }
        
        return content
    
    async def _generate_financial_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate financial analysis content."""
        content = {
            'ratios': {
                'title': 'Financial Ratios Analysis',
                'content': self._analyze_ratios(data)
            },
            'trends': {
                'title': 'Trend Analysis',
                'content': self._analyze_trends(data)
            },
            'forecasts': {
                'title': 'Financial Forecasts',
                'content': self._analyze_forecasts(data)
            },
            'benchmarks': {
                'title': 'Industry Benchmarks',
                'content': self._analyze_benchmarks(data)
            }
        }
        
        return content
    
    async def _generate_performance_dashboard(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance dashboard content."""
        content = {
            'kpis': {
                'title': 'Key Performance Indicators',
                'kpis': self._extract_kpis(data)
            },
            'charts': {
                'title': 'Performance Charts',
                'chart_data': self._prepare_chart_data(data)
            },
            'comparisons': {
                'title': 'Period Comparisons',
                'comparisons': self._generate_comparisons(data)
            },
            'insights': {
                'title': 'Key Insights',
                'insights': self._generate_insights(data)
            }
        }
        
        return content
    
    async def _generate_custom_report(self, data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        """Generate custom report content."""
        content = {
            'title': f'{report_type.title()} Report',
            'sections': [],
            'data': data
        }
        
        # Add custom sections based on data
        if 'financial_ratios' in data:
            content['sections'].append({
                'title': 'Financial Ratios',
                'content': data['financial_ratios']
            })
        
        if 'trends' in data:
            content['sections'].append({
                'title': 'Trend Analysis',
                'content': data['trends']
            })
        
        if 'forecasts' in data:
            content['sections'].append({
                'title': 'Forecasts',
                'content': data['forecasts']
            })
        
        return content
    
    def _generate_overview_text(self, data: Dict[str, Any]) -> str:
        """Generate overview text."""
        company_name = data.get('company_name', 'The Company')
        revenue = data.get('revenue', 0)
        net_income = data.get('net_income', 0)
        
        overview = f"""
        {company_name} is a company with annual revenue of ${revenue:,.0f} and net income of ${net_income:,.0f}. 
        This report provides a comprehensive analysis of the company's financial performance, 
        including key metrics, trends, and strategic recommendations.
        """
        
        return overview.strip()
    
    def _extract_key_metrics(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key financial metrics."""
        metrics = []
        
        # Revenue
        if 'revenue' in data:
            metrics.append({
                'name': 'Revenue',
                'value': f"${data['revenue']:,.0f}",
                'change': self._calculate_change(data, 'revenue'),
                'trend': self._determine_trend(data, 'revenue')
            })
        
        # Net Income
        if 'net_income' in data:
            metrics.append({
                'name': 'Net Income',
                'value': f"${data['net_income']:,.0f}",
                'change': self._calculate_change(data, 'net_income'),
                'trend': self._determine_trend(data, 'net_income')
            })
        
        # Total Assets
        if 'total_assets' in data:
            metrics.append({
                'name': 'Total Assets',
                'value': f"${data['total_assets']:,.0f}",
                'change': self._calculate_change(data, 'total_assets'),
                'trend': self._determine_trend(data, 'total_assets')
            })
        
        # Current Ratio
        if 'current_assets' in data and 'current_liabilities' in data:
            current_ratio = data['current_assets'] / data['current_liabilities']
            metrics.append({
                'name': 'Current Ratio',
                'value': f"{current_ratio:.2f}",
                'change': 'N/A',
                'trend': 'stable'
            })
        
        return metrics
    
    def _generate_financial_highlights(self, data: Dict[str, Any]) -> List[str]:
        """Generate financial highlights."""
        highlights = []
        
        # Revenue highlight
        if 'revenue' in data:
            highlights.append(f"Revenue: ${data['revenue']:,.0f}")
        
        # Profitability highlight
        if 'net_income' in data and 'revenue' in data:
            net_margin = (data['net_income'] / data['revenue']) * 100
            highlights.append(f"Net Margin: {net_margin:.1f}%")
        
        # Growth highlight
        if 'revenue_growth' in data:
            highlights.append(f"Revenue Growth: {data['revenue_growth']:.1f}%")
        
        # Liquidity highlight
        if 'current_assets' in data and 'current_liabilities' in data:
            current_ratio = data['current_assets'] / data['current_liabilities']
            highlights.append(f"Current Ratio: {current_ratio:.2f}")
        
        return highlights
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations."""
        recommendations = []
        
        # Liquidity recommendations
        if 'current_assets' in data and 'current_liabilities' in data:
            current_ratio = data['current_assets'] / data['current_liabilities']
            if current_ratio < 1.5:
                recommendations.append("Improve liquidity by increasing current assets or reducing current liabilities")
            elif current_ratio > 3.0:
                recommendations.append("Consider optimizing working capital to improve efficiency")
        
        # Profitability recommendations
        if 'net_income' in data and 'revenue' in data:
            net_margin = (data['net_income'] / data['revenue']) * 100
            if net_margin < 5:
                recommendations.append("Focus on improving operational efficiency to increase profitability")
            elif net_margin > 15:
                recommendations.append("Consider reinvesting profits for growth opportunities")
        
        # Growth recommendations
        if 'revenue_growth' in data:
            if data['revenue_growth'] < 5:
                recommendations.append("Develop strategies to accelerate revenue growth")
            elif data['revenue_growth'] > 20:
                recommendations.append("Ensure sustainable growth and operational scalability")
        
        return recommendations
    
    def _analyze_ratios(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial ratios."""
        analysis = {
            'liquidity_ratios': {},
            'profitability_ratios': {},
            'leverage_ratios': {},
            'efficiency_ratios': {}
        }
        
        # Liquidity ratios
        if 'current_assets' in data and 'current_liabilities' in data:
            analysis['liquidity_ratios']['current_ratio'] = {
                'value': data['current_assets'] / data['current_liabilities'],
                'interpretation': 'Measures short-term liquidity'
            }
        
        # Profitability ratios
        if 'net_income' in data and 'revenue' in data:
            analysis['profitability_ratios']['net_margin'] = {
                'value': (data['net_income'] / data['revenue']) * 100,
                'interpretation': 'Percentage of revenue that becomes profit'
            }
        
        # Leverage ratios
        if 'total_debt' in data and 'total_assets' in data:
            analysis['leverage_ratios']['debt_ratio'] = {
                'value': data['total_debt'] / data['total_assets'],
                'interpretation': 'Percentage of assets financed by debt'
            }
        
        return analysis
    
    def _analyze_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial trends."""
        trends = {
            'revenue_trend': 'stable',
            'profit_trend': 'stable',
            'asset_trend': 'stable',
            'key_insights': []
        }
        
        # Analyze revenue trend
        if 'revenue_growth' in data:
            if data['revenue_growth'] > 10:
                trends['revenue_trend'] = 'increasing'
                trends['key_insights'].append('Strong revenue growth indicates market expansion')
            elif data['revenue_growth'] < -5:
                trends['revenue_trend'] = 'decreasing'
                trends['key_insights'].append('Revenue decline requires immediate attention')
        
        # Analyze profit trend
        if 'net_income_growth' in data:
            if data['net_income_growth'] > 15:
                trends['profit_trend'] = 'increasing'
                trends['key_insights'].append('Improving profitability through operational efficiency')
            elif data['net_income_growth'] < -10:
                trends['profit_trend'] = 'decreasing'
                trends['key_insights'].append('Profitability challenges need strategic intervention')
        
        return trends
    
    def _analyze_forecasts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial forecasts."""
        forecasts = {
            'revenue_forecast': {},
            'profit_forecast': {},
            'confidence_level': 'medium',
            'key_assumptions': []
        }
        
        # Revenue forecast
        if 'revenue_forecast' in data:
            forecasts['revenue_forecast'] = data['revenue_forecast']
            forecasts['key_assumptions'].append('Revenue growth based on historical trends')
        
        # Profit forecast
        if 'profit_forecast' in data:
            forecasts['profit_forecast'] = data['profit_forecast']
            forecasts['key_assumptions'].append('Profitability maintained at current levels')
        
        return forecasts
    
    def _analyze_benchmarks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze industry benchmarks."""
        benchmarks = {
            'industry_comparison': {},
            'competitive_position': 'average',
            'improvement_areas': []
        }
        
        # Industry comparison
        if 'industry_benchmarks' in data:
            benchmarks['industry_comparison'] = data['industry_benchmarks']
        
        # Competitive position
        if 'performance_score' in data:
            score = data['performance_score']
            if score > 0.8:
                benchmarks['competitive_position'] = 'excellent'
            elif score > 0.6:
                benchmarks['competitive_position'] = 'good'
            elif score > 0.4:
                benchmarks['competitive_position'] = 'average'
            else:
                benchmarks['competitive_position'] = 'below_average'
        
        return benchmarks
    
    def _extract_kpis(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key performance indicators."""
        kpis = []
        
        # Revenue KPI
        if 'revenue' in data:
            kpis.append({
                'name': 'Revenue',
                'value': data['revenue'],
                'target': data.get('revenue_target', data['revenue'] * 1.1),
                'status': 'on_track' if data['revenue'] >= data.get('revenue_target', data['revenue'] * 1.1) * 0.9 else 'behind'
            })
        
        # Profit KPI
        if 'net_income' in data:
            kpis.append({
                'name': 'Net Income',
                'value': data['net_income'],
                'target': data.get('profit_target', data['net_income'] * 1.15),
                'status': 'on_track' if data['net_income'] >= data.get('profit_target', data['net_income'] * 1.15) * 0.9 else 'behind'
            })
        
        return kpis
    
    def _prepare_chart_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for charts."""
        chart_data = {
            'revenue_chart': {},
            'profit_chart': {},
            'ratio_chart': {}
        }
        
        # Revenue chart data
        if 'revenue_history' in data:
            chart_data['revenue_chart'] = {
                'x': data['revenue_history']['dates'],
                'y': data['revenue_history']['values'],
                'type': 'line',
                'title': 'Revenue Trend'
            }
        
        # Profit chart data
        if 'profit_history' in data:
            chart_data['profit_chart'] = {
                'x': data['profit_history']['dates'],
                'y': data['profit_history']['values'],
                'type': 'bar',
                'title': 'Profit Trend'
            }
        
        return chart_data
    
    def _generate_comparisons(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate period comparisons."""
        comparisons = []
        
        # Year-over-year comparison
        if 'revenue_yoy' in data:
            comparisons.append({
                'metric': 'Revenue',
                'current': data['revenue'],
                'previous': data['revenue_yoy']['previous'],
                'change': data['revenue_yoy']['change'],
                'change_pct': data['revenue_yoy']['change_pct']
            })
        
        # Quarter-over-quarter comparison
        if 'revenue_qoq' in data:
            comparisons.append({
                'metric': 'Revenue',
                'current': data['revenue'],
                'previous': data['revenue_qoq']['previous'],
                'change': data['revenue_qoq']['change'],
                'change_pct': data['revenue_qoq']['change_pct']
            })
        
        return comparisons
    
    def _generate_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate key insights."""
        insights = []
        
        # Revenue insights
        if 'revenue_growth' in data:
            if data['revenue_growth'] > 15:
                insights.append('Exceptional revenue growth indicates strong market position')
            elif data['revenue_growth'] < 0:
                insights.append('Revenue decline requires immediate strategic review')
        
        # Profitability insights
        if 'net_margin' in data:
            if data['net_margin'] > 0.15:
                insights.append('High profitability provides flexibility for growth investments')
            elif data['net_margin'] < 0.05:
                insights.append('Low profitability requires cost optimization focus')
        
        # Liquidity insights
        if 'current_ratio' in data:
            if data['current_ratio'] > 2.0:
                insights.append('Strong liquidity position enables strategic opportunities')
            elif data['current_ratio'] < 1.0:
                insights.append('Liquidity concerns require immediate attention')
        
        return insights
    
    async def _generate_charts(self, data: Dict[str, Any], report_type: str) -> List[Dict[str, Any]]:
        """Generate charts for the report."""
        charts = []
        
        try:
            # Revenue trend chart
            if 'revenue_history' in data:
                chart = self._create_revenue_chart(data['revenue_history'])
                charts.append(chart)
            
            # Profit trend chart
            if 'profit_history' in data:
                chart = self._create_profit_chart(data['profit_history'])
                charts.append(chart)
            
            # Ratio comparison chart
            if 'financial_ratios' in data:
                chart = self._create_ratio_chart(data['financial_ratios'])
                charts.append(chart)
            
        except Exception as e:
            self.logger.error(f"Error generating charts: {str(e)}")
        
        return charts
    
    def _create_revenue_chart(self, revenue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create revenue trend chart."""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=revenue_data['dates'],
            y=revenue_data['values'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color='blue', width=2)
        ))
        
        fig.update_layout(
            title='Revenue Trend',
            xaxis_title='Date',
            yaxis_title='Revenue ($)',
            template='plotly_white'
        )
        
        return {
            'type': 'revenue_trend',
            'title': 'Revenue Trend',
            'data': fig.to_dict()
        }
    
    def _create_profit_chart(self, profit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create profit trend chart."""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=profit_data['dates'],
            y=profit_data['values'],
            name='Profit',
            marker_color='green'
        ))
        
        fig.update_layout(
            title='Profit Trend',
            xaxis_title='Date',
            yaxis_title='Profit ($)',
            template='plotly_white'
        )
        
        return {
            'type': 'profit_trend',
            'title': 'Profit Trend',
            'data': fig.to_dict()
        }
    
    def _create_ratio_chart(self, ratios_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create ratio comparison chart."""
        fig = go.Figure()
        
        ratios = list(ratios_data.keys())
        values = list(ratios_data.values())
        
        fig.add_trace(go.Bar(
            x=ratios,
            y=values,
            name='Financial Ratios',
            marker_color='purple'
        ))
        
        fig.update_layout(
            title='Financial Ratios',
            xaxis_title='Ratio',
            yaxis_title='Value',
            template='plotly_white'
        )
        
        return {
            'type': 'ratio_comparison',
            'title': 'Financial Ratios',
            'data': fig.to_dict()
        }
    
    async def _generate_tables(self, data: Dict[str, Any], report_type: str) -> List[Dict[str, Any]]:
        """Generate tables for the report."""
        tables = []
        
        try:
            # Financial metrics table
            if 'financial_metrics' in data:
                table = {
                    'title': 'Financial Metrics',
                    'headers': ['Metric', 'Value', 'Change', 'Trend'],
                    'rows': self._format_metrics_table(data['financial_metrics'])
                }
                tables.append(table)
            
            # Ratio analysis table
            if 'financial_ratios' in data:
                table = {
                    'title': 'Financial Ratios',
                    'headers': ['Ratio', 'Value', 'Benchmark', 'Status'],
                    'rows': self._format_ratios_table(data['financial_ratios'])
                }
                tables.append(table)
            
        except Exception as e:
            self.logger.error(f"Error generating tables: {str(e)}")
        
        return tables
    
    def _format_metrics_table(self, metrics: Dict[str, Any]) -> List[List[str]]:
        """Format metrics data for table."""
        rows = []
        
        for metric, value in metrics.items():
            rows.append([
                metric.replace('_', ' ').title(),
                f"${value:,.0f}" if isinstance(value, (int, float)) else str(value),
                'N/A',
                'stable'
            ])
        
        return rows
    
    def _format_ratios_table(self, ratios: Dict[str, Any]) -> List[List[str]]:
        """Format ratios data for table."""
        rows = []
        
        for ratio, value in ratios.items():
            rows.append([
                ratio.replace('_', ' ').title(),
                f"{value:.2f}" if isinstance(value, (int, float)) else str(value),
                'Industry Avg',
                'Good' if isinstance(value, (int, float)) and value > 1 else 'Needs Improvement'
            ])
        
        return rows
    
    async def _generate_summary(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report summary."""
        summary = {
            'total_sections': len(content),
            'key_findings': [],
            'recommendations_count': 0,
            'charts_count': 0,
            'tables_count': 0
        }
        
        # Extract key findings
        for section_name, section_content in content.items():
            if isinstance(section_content, dict) and 'content' in section_content:
                if 'highlights' in section_content['content']:
                    summary['key_findings'].extend(section_content['content']['highlights'])
                if 'recommendations' in section_content['content']:
                    summary['recommendations_count'] += len(section_content['content']['recommendations'])
        
        return summary
    
    def _calculate_change(self, data: Dict[str, Any], metric: str) -> str:
        """Calculate change for a metric."""
        if f"{metric}_previous" in data:
            current = data[metric]
            previous = data[f"{metric}_previous"]
            change = ((current - previous) / previous) * 100
            return f"{change:+.1f}%"
        return "N/A"
    
    def _determine_trend(self, data: Dict[str, Any], metric: str) -> str:
        """Determine trend for a metric."""
        if f"{metric}_growth" in data:
            growth = data[f"{metric}_growth"]
            if growth > 5:
                return "increasing"
            elif growth < -5:
                return "decreasing"
            else:
                return "stable"
        return "stable"
    
    async def export_report(self, report: Dict[str, Any], format: str = 'pdf') -> bytes:
        """Export report in specified format."""
        try:
            if format == 'pdf':
                return await self._export_to_pdf(report)
            elif format == 'excel':
                return await self._export_to_excel(report)
            elif format == 'html':
                return await self._export_to_html(report)
            else:
                raise ValueError(f"Unsupported format: {format}")
        
        except Exception as e:
            self.logger.error(f"Error exporting report: {str(e)}")
            raise
    
    async def _export_to_pdf(self, report: Dict[str, Any]) -> bytes:
        """Export report to PDF."""
        # This would integrate with a PDF generation library
        # For now, return a placeholder
        return b"PDF content placeholder"
    
    async def _export_to_excel(self, report: Dict[str, Any]) -> bytes:
        """Export report to Excel."""
        # This would integrate with openpyxl or xlsxwriter
        # For now, return a placeholder
        return b"Excel content placeholder"
    
    async def _export_to_html(self, report: Dict[str, Any]) -> bytes:
        """Export report to HTML."""
        # This would generate HTML content
        # For now, return a placeholder
        return b"HTML content placeholder"
