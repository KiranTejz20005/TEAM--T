"""
Financial analysis service for calculating ratios, forecasts, and trends.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from prophet import Prophet
from sklearn.linear_model import LinearRegression
from scipy import stats

from app.config import settings


class FinancialAnalyzer:
    """Service for financial analysis and calculations."""
    
    def __init__(self):
        """Initialize financial analyzer."""
        self.ratio_calculators = {
            "liquidity": self._calculate_liquidity_ratios,
            "profitability": self._calculate_profitability_ratios,
            "leverage": self._calculate_leverage_ratios,
            "efficiency": self._calculate_efficiency_ratios,
            "valuation": self._calculate_valuation_ratios
        }
    
    async def calculate_ratios(
        self, 
        document_id: int, 
        ratio_types: List[str], 
        period: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate financial ratios for a document."""
        
        # This would typically fetch data from the database
        # For now, we'll use sample data
        sample_data = self._get_sample_financial_data()
        
        results = {}
        confidence_scores = []
        
        for ratio_type in ratio_types:
            if ratio_type in self.ratio_calculators:
                try:
                    ratios = self.ratio_calculators[ratio_type](sample_data)
                    results[ratio_type] = ratios
                    confidence_scores.append(0.95)  # High confidence for calculations
                except Exception as e:
                    results[ratio_type] = {"error": str(e)}
                    confidence_scores.append(0.0)
        
        # Calculate overall confidence
        overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        
        return {
            "ratios": results,
            "confidence_score": overall_confidence,
            "calculation_date": datetime.utcnow().isoformat(),
            "period": period or "current",
            "document_id": document_id
        }
    
    def _calculate_liquidity_ratios(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate liquidity ratios."""
        current_assets = data.get("current_assets", 0)
        current_liabilities = data.get("current_liabilities", 0)
        inventory = data.get("inventory", 0)
        cash = data.get("cash", 0)
        
        ratios = {}
        
        if current_liabilities > 0:
            ratios["current_ratio"] = current_assets / current_liabilities
            ratios["quick_ratio"] = (current_assets - inventory) / current_liabilities
            ratios["cash_ratio"] = cash / current_liabilities
        
        return ratios
    
    def _calculate_profitability_ratios(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate profitability ratios."""
        revenue = data.get("revenue", 0)
        gross_profit = data.get("gross_profit", 0)
        net_income = data.get("net_income", 0)
        total_assets = data.get("total_assets", 0)
        shareholders_equity = data.get("shareholders_equity", 0)
        
        ratios = {}
        
        if revenue > 0:
            ratios["gross_margin"] = gross_profit / revenue
            ratios["net_margin"] = net_income / revenue
        
        if total_assets > 0:
            ratios["return_on_assets"] = net_income / total_assets
        
        if shareholders_equity > 0:
            ratios["return_on_equity"] = net_income / shareholders_equity
        
        return ratios
    
    def _calculate_leverage_ratios(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate leverage ratios."""
        total_debt = data.get("total_debt", 0)
        total_assets = data.get("total_assets", 0)
        shareholders_equity = data.get("shareholders_equity", 0)
        ebit = data.get("ebit", 0)
        interest_expense = data.get("interest_expense", 0)
        
        ratios = {}
        
        if total_assets > 0:
            ratios["debt_ratio"] = total_debt / total_assets
        
        if shareholders_equity > 0:
            ratios["debt_to_equity"] = total_debt / shareholders_equity
        
        if interest_expense > 0:
            ratios["interest_coverage"] = ebit / interest_expense
        
        return ratios
    
    def _calculate_efficiency_ratios(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate efficiency ratios."""
        revenue = data.get("revenue", 0)
        total_assets = data.get("total_assets", 0)
        inventory = data.get("inventory", 0)
        accounts_receivable = data.get("accounts_receivable", 0)
        cogs = data.get("cost_of_goods_sold", 0)
        
        ratios = {}
        
        if total_assets > 0:
            ratios["asset_turnover"] = revenue / total_assets
        
        if inventory > 0:
            ratios["inventory_turnover"] = cogs / inventory
        
        if accounts_receivable > 0:
            ratios["receivables_turnover"] = revenue / accounts_receivable
        
        return ratios
    
    def _calculate_valuation_ratios(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate valuation ratios."""
        market_cap = data.get("market_cap", 0)
        net_income = data.get("net_income", 0)
        book_value = data.get("book_value", 0)
        ebitda = data.get("ebitda", 0)
        enterprise_value = data.get("enterprise_value", 0)
        
        ratios = {}
        
        if net_income > 0:
            ratios["price_to_earnings"] = market_cap / net_income
        
        if book_value > 0:
            ratios["price_to_book"] = market_cap / book_value
        
        if ebitda > 0:
            ratios["ev_to_ebitda"] = enterprise_value / ebitda
        
        return ratios
    
    async def generate_forecast(
        self, 
        document_id: int, 
        metric: str, 
        periods: int = 12,
        method: str = "prophet"
    ) -> Dict[str, Any]:
        """Generate financial forecasts."""
        
        # Generate sample time series data
        historical_data = self._generate_sample_time_series(metric, periods * 2)
        
        if method == "prophet":
            forecast_data = await self._prophet_forecast(historical_data, periods)
        elif method == "linear":
            forecast_data = await self._linear_forecast(historical_data, periods)
        else:
            raise ValueError(f"Unsupported forecasting method: {method}")
        
        return {
            "metric": metric,
            "forecast_data": forecast_data["forecast"],
            "confidence_intervals": forecast_data["confidence_intervals"],
            "method": method,
            "periods": periods,
            "confidence_score": forecast_data.get("confidence_score", 0.85),
            "document_id": document_id
        }
    
    async def _prophet_forecast(self, data: pd.DataFrame, periods: int) -> Dict[str, Any]:
        """Generate forecast using Prophet."""
        try:
            # Prepare data for Prophet
            df = data.rename(columns={'date': 'ds', 'value': 'y'})
            
            # Initialize and fit model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False
            )
            model.fit(df)
            
            # Make future dataframe
            future = model.make_future_dataframe(periods=periods, freq='M')
            forecast = model.predict(future)
            
            # Extract forecast data
            forecast_periods = forecast.tail(periods)
            
            return {
                "forecast": [
                    {
                        "date": row['ds'].strftime('%Y-%m-%d'),
                        "value": row['yhat'],
                        "lower_bound": row['yhat_lower'],
                        "upper_bound": row['yhat_upper']
                    }
                    for _, row in forecast_periods.iterrows()
                ],
                "confidence_intervals": [
                    {
                        "date": row['ds'].strftime('%Y-%m-%d'),
                        "lower": row['yhat_lower'],
                        "upper": row['yhat_upper']
                    }
                    for _, row in forecast_periods.iterrows()
                ],
                "confidence_score": 0.9
            }
            
        except Exception as e:
            return {
                "forecast": [],
                "confidence_intervals": [],
                "confidence_score": 0.0,
                "error": str(e)
            }
    
    async def _linear_forecast(self, data: pd.DataFrame, periods: int) -> Dict[str, Any]:
        """Generate forecast using linear regression."""
        try:
            # Prepare data
            X = np.arange(len(data)).reshape(-1, 1)
            y = data['value'].values
            
            # Fit linear model
            model = LinearRegression()
            model.fit(X, y)
            
            # Generate forecast
            future_X = np.arange(len(data), len(data) + periods).reshape(-1, 1)
            forecast_values = model.predict(future_X)
            
            # Calculate confidence intervals (simplified)
            residuals = y - model.predict(X)
            std_error = np.std(residuals)
            
            forecast_dates = pd.date_range(
                start=data['date'].iloc[-1] + pd.Timedelta(days=30),
                periods=periods,
                freq='M'
            )
            
            return {
                "forecast": [
                    {
                        "date": date.strftime('%Y-%m-%d'),
                        "value": float(value),
                        "lower_bound": float(value - 1.96 * std_error),
                        "upper_bound": float(value + 1.96 * std_error)
                    }
                    for date, value in zip(forecast_dates, forecast_values)
                ],
                "confidence_intervals": [
                    {
                        "date": date.strftime('%Y-%m-%d'),
                        "lower": float(value - 1.96 * std_error),
                        "upper": float(value + 1.96 * std_error)
                    }
                    for date, value in zip(forecast_dates, forecast_values)
                ],
                "confidence_score": 0.8
            }
            
        except Exception as e:
            return {
                "forecast": [],
                "confidence_intervals": [],
                "confidence_score": 0.0,
                "error": str(e)
            }
    
    async def analyze_trends(
        self, 
        document_id: int, 
        metrics: List[str], 
        time_period: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze trends in financial data."""
        
        results = {}
        
        for metric in metrics:
            # Generate sample time series data
            data = self._generate_sample_time_series(metric, 24)  # 2 years of monthly data
            
            # Calculate trend
            trend_analysis = self._calculate_trend(data)
            
            results[metric] = {
                "trend_direction": trend_analysis["direction"],
                "trend_strength": trend_analysis["strength"],
                "slope": trend_analysis["slope"],
                "r_squared": trend_analysis["r_squared"],
                "p_value": trend_analysis["p_value"],
                "forecast_next_period": trend_analysis["forecast"],
                "volatility": trend_analysis["volatility"]
            }
        
        return {
            "trends": results,
            "analysis_date": datetime.utcnow().isoformat(),
            "time_period": time_period or "24_months",
            "confidence_score": 0.85,
            "document_id": document_id
        }
    
    def _calculate_trend(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trend statistics for time series data."""
        try:
            # Prepare data
            X = np.arange(len(data))
            y = data['value'].values
            
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
            
            # Calculate trend direction and strength
            direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
            strength = abs(r_value)
            
            # Calculate volatility (standard deviation of residuals)
            predicted = slope * X + intercept
            residuals = y - predicted
            volatility = np.std(residuals)
            
            # Forecast next period
            next_period = slope * len(X) + intercept
            
            return {
                "direction": direction,
                "strength": strength,
                "slope": slope,
                "r_squared": r_value ** 2,
                "p_value": p_value,
                "forecast": next_period,
                "volatility": volatility
            }
            
        except Exception as e:
            return {
                "direction": "unknown",
                "strength": 0.0,
                "slope": 0.0,
                "r_squared": 0.0,
                "p_value": 1.0,
                "forecast": 0.0,
                "volatility": 0.0,
                "error": str(e)
            }
    
    def _get_sample_financial_data(self) -> Dict[str, Any]:
        """Get sample financial data for calculations."""
        return {
            "revenue": 1000000,
            "gross_profit": 400000,
            "net_income": 150000,
            "total_assets": 2000000,
            "current_assets": 500000,
            "current_liabilities": 200000,
            "total_debt": 800000,
            "shareholders_equity": 1200000,
            "inventory": 100000,
            "cash": 200000,
            "accounts_receivable": 150000,
            "cost_of_goods_sold": 600000,
            "ebit": 200000,
            "interest_expense": 50000,
            "market_cap": 5000000,
            "book_value": 1200000,
            "ebitda": 250000,
            "enterprise_value": 6000000
        }
    
    def _generate_sample_time_series(self, metric: str, periods: int) -> pd.DataFrame:
        """Generate sample time series data for forecasting."""
        # Create date range
        start_date = datetime.now() - timedelta(days=periods * 30)
        dates = pd.date_range(start=start_date, periods=periods, freq='M')
        
        # Generate sample data with trend and seasonality
        np.random.seed(42)  # For reproducibility
        
        # Base value based on metric
        base_values = {
            "revenue": 100000,
            "expenses": 80000,
            "profit": 20000,
            "assets": 2000000,
            "cash": 200000
        }
        
        base_value = base_values.get(metric, 100000)
        
        # Generate trend
        trend = np.linspace(0, 0.1, periods)  # 10% growth over period
        
        # Generate seasonality
        seasonal = 0.05 * np.sin(2 * np.pi * np.arange(periods) / 12)  # Annual seasonality
        
        # Generate noise
        noise = np.random.normal(0, 0.02, periods)
        
        # Combine components
        values = base_value * (1 + trend + seasonal + noise)
        
        return pd.DataFrame({
            'date': dates,
            'value': values
        })
