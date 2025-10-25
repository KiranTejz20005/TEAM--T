"""
Scenario modeling service for financial what-if analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging

from app.config import settings


class ScenarioModeler:
    """Service for financial scenario modeling and what-if analysis."""
    
    def __init__(self):
        """Initialize scenario modeler."""
        self.logger = logging.getLogger(__name__)
        self.scenarios = {}
    
    async def create_scenario(
        self, 
        base_data: Dict[str, Any], 
        scenario_name: str,
        changes: Dict[str, Any],
        scenario_type: str = "sensitivity"
    ) -> Dict[str, Any]:
        """Create a new financial scenario."""
        
        scenario = {
            'scenario_id': f"scenario_{len(self.scenarios) + 1}",
            'scenario_name': scenario_name,
            'scenario_type': scenario_type,
            'base_data': base_data,
            'changes': changes,
            'created_at': datetime.utcnow().isoformat(),
            'results': {},
            'impact_analysis': {},
            'sensitivity_metrics': {}
        }
        
        try:
            # Apply changes to base data
            modified_data = self._apply_changes(base_data, changes)
            scenario['modified_data'] = modified_data
            
            # Calculate scenario results
            scenario['results'] = await self._calculate_scenario_results(
                base_data, modified_data, scenario_type
            )
            
            # Perform impact analysis
            scenario['impact_analysis'] = await self._analyze_impact(
                base_data, modified_data
            )
            
            # Calculate sensitivity metrics
            scenario['sensitivity_metrics'] = await self._calculate_sensitivity_metrics(
                base_data, modified_data, changes
            )
            
            # Store scenario
            self.scenarios[scenario['scenario_id']] = scenario
            
        except Exception as e:
            self.logger.error(f"Error creating scenario: {str(e)}")
            scenario['error'] = str(e)
        
        return scenario
    
    def _apply_changes(self, base_data: Dict[str, Any], changes: Dict[str, Any]) -> Dict[str, Any]:
        """Apply changes to base financial data."""
        modified_data = base_data.copy()
        
        for metric, change in changes.items():
            if metric in modified_data:
                if isinstance(change, dict):
                    # Percentage change
                    if 'percentage' in change:
                        percentage = change['percentage']
                        if percentage > 0:
                            modified_data[metric] = modified_data[metric] * (1 + percentage / 100)
                        else:
                            modified_data[metric] = modified_data[metric] * (1 - abs(percentage) / 100)
                    
                    # Absolute change
                    elif 'absolute' in change:
                        modified_data[metric] = modified_data[metric] + change['absolute']
                    
                    # New value
                    elif 'new_value' in change:
                        modified_data[metric] = change['new_value']
                
                # Simple percentage change
                elif isinstance(change, (int, float)):
                    if change > 0:
                        modified_data[metric] = modified_data[metric] * (1 + change / 100)
                    else:
                        modified_data[metric] = modified_data[metric] * (1 - abs(change) / 100)
        
        return modified_data
    
    async def _calculate_scenario_results(
        self, 
        base_data: Dict[str, Any], 
        modified_data: Dict[str, Any],
        scenario_type: str
    ) -> Dict[str, Any]:
        """Calculate results for the scenario."""
        results = {
            'financial_ratios': {},
            'key_metrics': {},
            'cash_flow_impact': {},
            'profitability_impact': {},
            'liquidity_impact': {}
        }
        
        try:
            # Calculate financial ratios for both scenarios
            base_ratios = self._calculate_ratios(base_data)
            modified_ratios = self._calculate_ratios(modified_data)
            
            results['financial_ratios'] = {
                'base': base_ratios,
                'modified': modified_ratios,
                'change': {
                    ratio: modified_ratios[ratio] - base_ratios[ratio]
                    for ratio in base_ratios.keys()
                    if ratio in modified_ratios
                }
            }
            
            # Calculate key metrics
            results['key_metrics'] = self._calculate_key_metrics(base_data, modified_data)
            
            # Calculate cash flow impact
            results['cash_flow_impact'] = self._calculate_cash_flow_impact(base_data, modified_data)
            
            # Calculate profitability impact
            results['profitability_impact'] = self._calculate_profitability_impact(base_data, modified_data)
            
            # Calculate liquidity impact
            results['liquidity_impact'] = self._calculate_liquidity_impact(base_data, modified_data)
            
        except Exception as e:
            self.logger.error(f"Error calculating scenario results: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def _calculate_ratios(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate financial ratios."""
        ratios = {}
        
        try:
            # Liquidity ratios
            if 'current_assets' in data and 'current_liabilities' in data:
                if data['current_liabilities'] > 0:
                    ratios['current_ratio'] = data['current_assets'] / data['current_liabilities']
            
            # Profitability ratios
            if 'revenue' in data and 'net_income' in data:
                if data['revenue'] > 0:
                    ratios['net_margin'] = data['net_income'] / data['revenue']
            
            if 'total_assets' in data and 'net_income' in data:
                if data['total_assets'] > 0:
                    ratios['roa'] = data['net_income'] / data['total_assets']
            
            # Leverage ratios
            if 'total_debt' in data and 'total_assets' in data:
                if data['total_assets'] > 0:
                    ratios['debt_ratio'] = data['total_debt'] / data['total_assets']
            
        except Exception as e:
            self.logger.error(f"Error calculating ratios: {str(e)}")
        
        return ratios
    
    def _calculate_key_metrics(self, base_data: Dict[str, Any], modified_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key financial metrics."""
        metrics = {}
        
        # Revenue change
        if 'revenue' in base_data and 'revenue' in modified_data:
            revenue_change = modified_data['revenue'] - base_data['revenue']
            revenue_change_pct = (revenue_change / base_data['revenue']) * 100 if base_data['revenue'] > 0 else 0
            metrics['revenue_change'] = {
                'absolute': revenue_change,
                'percentage': revenue_change_pct
            }
        
        # Profit change
        if 'net_income' in base_data and 'net_income' in modified_data:
            profit_change = modified_data['net_income'] - base_data['net_income']
            profit_change_pct = (profit_change / base_data['net_income']) * 100 if base_data['net_income'] > 0 else 0
            metrics['profit_change'] = {
                'absolute': profit_change,
                'percentage': profit_change_pct
            }
        
        # Asset change
        if 'total_assets' in base_data and 'total_assets' in modified_data:
            asset_change = modified_data['total_assets'] - base_data['total_assets']
            asset_change_pct = (asset_change / base_data['total_assets']) * 100 if base_data['total_assets'] > 0 else 0
            metrics['asset_change'] = {
                'absolute': asset_change,
                'percentage': asset_change_pct
            }
        
        return metrics
    
    def _calculate_cash_flow_impact(self, base_data: Dict[str, Any], modified_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cash flow impact."""
        impact = {}
        
        # Operating cash flow impact
        if 'operating_cash_flow' in base_data and 'operating_cash_flow' in modified_data:
            ocf_change = modified_data['operating_cash_flow'] - base_data['operating_cash_flow']
            impact['operating_cash_flow_change'] = ocf_change
        
        # Free cash flow impact
        if 'free_cash_flow' in base_data and 'free_cash_flow' in modified_data:
            fcf_change = modified_data['free_cash_flow'] - base_data['free_cash_flow']
            impact['free_cash_flow_change'] = fcf_change
        
        # Cash position impact
        if 'cash' in base_data and 'cash' in modified_data:
            cash_change = modified_data['cash'] - base_data['cash']
            impact['cash_position_change'] = cash_change
        
        return impact
    
    def _calculate_profitability_impact(self, base_data: Dict[str, Any], modified_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate profitability impact."""
        impact = {}
        
        # Gross margin impact
        if all(key in base_data for key in ['revenue', 'cost_of_goods_sold']) and \
           all(key in modified_data for key in ['revenue', 'cost_of_goods_sold']):
            
            base_gross_margin = (base_data['revenue'] - base_data['cost_of_goods_sold']) / base_data['revenue']
            modified_gross_margin = (modified_data['revenue'] - modified_data['cost_of_goods_sold']) / modified_data['revenue']
            
            impact['gross_margin_change'] = modified_gross_margin - base_gross_margin
        
        # Net margin impact
        if 'revenue' in base_data and 'net_income' in base_data and \
           'revenue' in modified_data and 'net_income' in modified_data:
            
            base_net_margin = base_data['net_income'] / base_data['revenue']
            modified_net_margin = modified_data['net_income'] / modified_data['revenue']
            
            impact['net_margin_change'] = modified_net_margin - base_net_margin
        
        return impact
    
    def _calculate_liquidity_impact(self, base_data: Dict[str, Any], modified_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate liquidity impact."""
        impact = {}
        
        # Current ratio impact
        if all(key in base_data for key in ['current_assets', 'current_liabilities']) and \
           all(key in modified_data for key in ['current_assets', 'current_liabilities']):
            
            base_current_ratio = base_data['current_assets'] / base_data['current_liabilities']
            modified_current_ratio = modified_data['current_assets'] / modified_data['current_liabilities']
            
            impact['current_ratio_change'] = modified_current_ratio - base_current_ratio
        
        # Quick ratio impact
        if all(key in base_data for key in ['current_assets', 'inventory', 'current_liabilities']) and \
           all(key in modified_data for key in ['current_assets', 'inventory', 'current_liabilities']):
            
            base_quick_ratio = (base_data['current_assets'] - base_data['inventory']) / base_data['current_liabilities']
            modified_quick_ratio = (modified_data['current_assets'] - modified_data['inventory']) / modified_data['current_liabilities']
            
            impact['quick_ratio_change'] = modified_quick_ratio - base_quick_ratio
        
        return impact
    
    async def _analyze_impact(self, base_data: Dict[str, Any], modified_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the overall impact of the scenario."""
        impact = {
            'overall_impact': 'neutral',
            'risk_assessment': 'low',
            'key_changes': [],
            'recommendations': []
        }
        
        try:
            # Calculate overall impact score
            impact_score = 0
            key_changes = []
            
            # Revenue impact
            if 'revenue' in base_data and 'revenue' in modified_data:
                revenue_change_pct = ((modified_data['revenue'] - base_data['revenue']) / base_data['revenue']) * 100
                impact_score += revenue_change_pct * 0.3  # 30% weight
                if abs(revenue_change_pct) > 5:
                    key_changes.append(f"Revenue change: {revenue_change_pct:.1f}%")
            
            # Profit impact
            if 'net_income' in base_data and 'net_income' in modified_data:
                profit_change_pct = ((modified_data['net_income'] - base_data['net_income']) / base_data['net_income']) * 100
                impact_score += profit_change_pct * 0.4  # 40% weight
                if abs(profit_change_pct) > 10:
                    key_changes.append(f"Profit change: {profit_change_pct:.1f}%")
            
            # Asset impact
            if 'total_assets' in base_data and 'total_assets' in modified_data:
                asset_change_pct = ((modified_data['total_assets'] - base_data['total_assets']) / base_data['total_assets']) * 100
                impact_score += asset_change_pct * 0.3  # 30% weight
                if abs(asset_change_pct) > 5:
                    key_changes.append(f"Asset change: {asset_change_pct:.1f}%")
            
            # Determine overall impact
            if impact_score > 10:
                impact['overall_impact'] = 'positive'
            elif impact_score < -10:
                impact['overall_impact'] = 'negative'
            else:
                impact['overall_impact'] = 'neutral'
            
            # Risk assessment
            if abs(impact_score) > 20:
                impact['risk_assessment'] = 'high'
            elif abs(impact_score) > 10:
                impact['risk_assessment'] = 'medium'
            else:
                impact['risk_assessment'] = 'low'
            
            impact['key_changes'] = key_changes
            
            # Generate recommendations
            if impact['overall_impact'] == 'positive':
                impact['recommendations'].append("Scenario shows positive impact. Consider implementing changes.")
            elif impact['overall_impact'] == 'negative':
                impact['recommendations'].append("Scenario shows negative impact. Review and adjust strategy.")
            else:
                impact['recommendations'].append("Scenario shows neutral impact. Monitor closely.")
            
            if impact['risk_assessment'] == 'high':
                impact['recommendations'].append("High risk scenario. Conduct detailed analysis before implementation.")
        
        except Exception as e:
            self.logger.error(f"Error analyzing impact: {str(e)}")
            impact['error'] = str(e)
        
        return impact
    
    async def _calculate_sensitivity_metrics(
        self, 
        base_data: Dict[str, Any], 
        modified_data: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate sensitivity metrics for the scenario."""
        metrics = {}
        
        try:
            # Calculate sensitivity for each changed metric
            for metric, change in changes.items():
                if metric in base_data and metric in modified_data:
                    base_value = base_data[metric]
                    modified_value = modified_data[metric]
                    
                    if base_value != 0:
                        sensitivity = (modified_value - base_value) / base_value
                        metrics[f"{metric}_sensitivity"] = sensitivity
                        
                        # Calculate impact on other metrics
                        for other_metric in base_data.keys():
                            if other_metric != metric and other_metric in modified_data:
                                other_base = base_data[other_metric]
                                other_modified = modified_data[other_metric]
                                
                                if other_base != 0:
                                    cross_sensitivity = (other_modified - other_base) / other_base
                                    metrics[f"{metric}_to_{other_metric}_sensitivity"] = cross_sensitivity
        
        except Exception as e:
            self.logger.error(f"Error calculating sensitivity metrics: {str(e)}")
            metrics['error'] = str(e)
        
        return metrics
    
    async def compare_scenarios(self, scenario_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple scenarios."""
        comparison = {
            'scenarios': [],
            'comparison_metrics': {},
            'best_scenario': None,
            'worst_scenario': None,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        try:
            # Get scenarios
            scenarios = [self.scenarios[sid] for sid in scenario_ids if sid in self.scenarios]
            
            if len(scenarios) < 2:
                comparison['error'] = "Need at least 2 scenarios to compare"
                return comparison
            
            comparison['scenarios'] = [
                {
                    'scenario_id': scenario['scenario_id'],
                    'scenario_name': scenario['scenario_name'],
                    'impact_analysis': scenario['impact_analysis']
                }
                for scenario in scenarios
            ]
            
            # Compare key metrics
            comparison['comparison_metrics'] = self._compare_key_metrics(scenarios)
            
            # Determine best and worst scenarios
            best_worst = self._determine_best_worst_scenarios(scenarios)
            comparison['best_scenario'] = best_worst['best']
            comparison['worst_scenario'] = best_worst['worst']
        
        except Exception as e:
            self.logger.error(f"Error comparing scenarios: {str(e)}")
            comparison['error'] = str(e)
        
        return comparison
    
    def _compare_key_metrics(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare key metrics across scenarios."""
        metrics = {}
        
        # Compare revenue impact
        revenue_impacts = []
        for scenario in scenarios:
            if 'key_metrics' in scenario['results'] and 'revenue_change' in scenario['results']['key_metrics']:
                revenue_impacts.append(scenario['results']['key_metrics']['revenue_change']['percentage'])
        
        if revenue_impacts:
            metrics['revenue_impact_comparison'] = {
                'min': min(revenue_impacts),
                'max': max(revenue_impacts),
                'average': np.mean(revenue_impacts),
                'std': np.std(revenue_impacts)
            }
        
        # Compare profit impact
        profit_impacts = []
        for scenario in scenarios:
            if 'key_metrics' in scenario['results'] and 'profit_change' in scenario['results']['key_metrics']:
                profit_impacts.append(scenario['results']['key_metrics']['profit_change']['percentage'])
        
        if profit_impacts:
            metrics['profit_impact_comparison'] = {
                'min': min(profit_impacts),
                'max': max(profit_impacts),
                'average': np.mean(profit_impacts),
                'std': np.std(profit_impacts)
            }
        
        return metrics
    
    def _determine_best_worst_scenarios(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Determine best and worst scenarios."""
        best_worst = {'best': None, 'worst': None}
        
        try:
            # Score scenarios based on impact
            scenario_scores = []
            for scenario in scenarios:
                score = 0
                
                # Revenue impact score
                if 'key_metrics' in scenario['results'] and 'revenue_change' in scenario['results']['key_metrics']:
                    score += scenario['results']['key_metrics']['revenue_change']['percentage'] * 0.4
                
                # Profit impact score
                if 'key_metrics' in scenario['results'] and 'profit_change' in scenario['results']['key_metrics']:
                    score += scenario['results']['key_metrics']['profit_change']['percentage'] * 0.6
                
                scenario_scores.append((scenario['scenario_id'], score))
            
            # Sort by score
            scenario_scores.sort(key=lambda x: x[1], reverse=True)
            
            if scenario_scores:
                best_worst['best'] = scenario_scores[0][0]
                best_worst['worst'] = scenario_scores[-1][0]
        
        except Exception as e:
            self.logger.error(f"Error determining best/worst scenarios: {str(e)}")
        
        return best_worst
    
    async def get_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific scenario by ID."""
        return self.scenarios.get(scenario_id)
    
    async def list_scenarios(self) -> List[Dict[str, Any]]:
        """List all scenarios."""
        return [
            {
                'scenario_id': scenario['scenario_id'],
                'scenario_name': scenario['scenario_name'],
                'scenario_type': scenario['scenario_type'],
                'created_at': scenario['created_at'],
                'impact_analysis': scenario['impact_analysis']
            }
            for scenario in self.scenarios.values()
        ]
    
    async def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario."""
        if scenario_id in self.scenarios:
            del self.scenarios[scenario_id]
            return True
        return False
