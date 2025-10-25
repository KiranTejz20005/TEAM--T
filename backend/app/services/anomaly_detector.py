"""
Anomaly detection service for financial data.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy import stats
import logging

from app.config import settings


class AnomalyDetector:
    """Service for detecting anomalies in financial data."""
    
    def __init__(self):
        """Initialize anomaly detector."""
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(
            contamination=0.1,  # Expect 10% anomalies
            random_state=42
        )
    
    async def detect_anomalies(
        self, 
        financial_data: Dict[str, Any], 
        time_series_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Detect anomalies in financial data."""
        
        anomalies = {
            'timestamp': datetime.utcnow().isoformat(),
            'anomalies_detected': [],
            'risk_level': 'low',
            'confidence_score': 0.0,
            'recommendations': []
        }
        
        try:
            # Detect ratio anomalies
            ratio_anomalies = await self._detect_ratio_anomalies(financial_data)
            anomalies['anomalies_detected'].extend(ratio_anomalies)
            
            # Detect trend anomalies
            if time_series_data is not None:
                trend_anomalies = await self._detect_trend_anomalies(time_series_data)
                anomalies['anomalies_detected'].extend(trend_anomalies)
            
            # Detect statistical anomalies
            statistical_anomalies = await self._detect_statistical_anomalies(financial_data)
            anomalies['anomalies_detected'].extend(statistical_anomalies)
            
            # Calculate overall risk level
            anomalies['risk_level'] = self._calculate_risk_level(anomalies['anomalies_detected'])
            anomalies['confidence_score'] = self._calculate_confidence_score(anomalies['anomalies_detected'])
            
            # Generate recommendations
            anomalies['recommendations'] = self._generate_recommendations(anomalies['anomalies_detected'])
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {str(e)}")
            anomalies['error'] = str(e)
        
        return anomalies
    
    async def _detect_ratio_anomalies(self, financial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in financial ratios."""
        anomalies = []
        
        # Define normal ranges for key ratios
        ratio_ranges = {
            'current_ratio': (1.0, 3.0),
            'quick_ratio': (0.5, 2.0),
            'debt_to_equity': (0.0, 2.0),
            'gross_margin': (0.1, 0.8),
            'net_margin': (0.0, 0.3),
            'roe': (0.0, 0.5),
            'roa': (0.0, 0.2)
        }
        
        for ratio_name, (min_val, max_val) in ratio_ranges.items():
            if ratio_name in financial_data:
                value = financial_data[ratio_name]
                
                if value < min_val or value > max_val:
                    anomaly = {
                        'type': 'ratio_anomaly',
                        'metric': ratio_name,
                        'value': value,
                        'normal_range': (min_val, max_val),
                        'severity': 'high' if abs(value - (min_val + max_val) / 2) > (max_val - min_val) else 'medium',
                        'description': f"{ratio_name} of {value:.2f} is outside normal range ({min_val}-{max_val})",
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    anomalies.append(anomaly)
        
        return anomalies
    
    async def _detect_trend_anomalies(self, time_series_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies in time series data."""
        anomalies = []
        
        try:
            # Ensure we have date and value columns
            if 'date' not in time_series_data.columns or 'value' not in time_series_data.columns:
                return anomalies
            
            # Sort by date
            data = time_series_data.sort_values('date')
            values = data['value'].values
            
            if len(values) < 3:
                return anomalies
            
            # Detect sudden changes (Z-score method)
            z_scores = np.abs(stats.zscore(values))
            threshold = 2.5  # 99% confidence
            
            for i, z_score in enumerate(z_scores):
                if z_score > threshold:
                    anomaly = {
                        'type': 'trend_anomaly',
                        'metric': 'sudden_change',
                        'value': values[i],
                        'z_score': z_score,
                        'date': data.iloc[i]['date'].isoformat() if hasattr(data.iloc[i]['date'], 'isoformat') else str(data.iloc[i]['date']),
                        'severity': 'high' if z_score > 3.0 else 'medium',
                        'description': f"Sudden change detected: {values[i]:.2f} (Z-score: {z_score:.2f})",
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    anomalies.append(anomaly)
            
            # Detect trend reversals
            if len(values) >= 5:
                trend_reversals = self._detect_trend_reversals(values)
                for reversal in trend_reversals:
                    anomaly = {
                        'type': 'trend_anomaly',
                        'metric': 'trend_reversal',
                        'value': values[reversal['index']],
                        'date': data.iloc[reversal['index']]['date'].isoformat() if hasattr(data.iloc[reversal['index']]['date'], 'isoformat') else str(data.iloc[reversal['index']]['date']),
                        'severity': reversal['severity'],
                        'description': f"Trend reversal detected: {reversal['description']}",
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    anomalies.append(anomaly)
        
        except Exception as e:
            self.logger.error(f"Error detecting trend anomalies: {str(e)}")
        
        return anomalies
    
    def _detect_trend_reversals(self, values: np.ndarray) -> List[Dict[str, Any]]:
        """Detect trend reversals in time series."""
        reversals = []
        
        if len(values) < 5:
            return reversals
        
        # Calculate moving averages
        short_ma = pd.Series(values).rolling(window=3).mean()
        long_ma = pd.Series(values).rolling(window=5).mean()
        
        # Find crossover points
        for i in range(4, len(values)):
            if not np.isnan(short_ma.iloc[i]) and not np.isnan(long_ma.iloc[i]):
                # Check for crossover
                if (short_ma.iloc[i-1] <= long_ma.iloc[i-1] and short_ma.iloc[i] > long_ma.iloc[i]) or \
                   (short_ma.iloc[i-1] >= long_ma.iloc[i-1] and short_ma.iloc[i] < long_ma.iloc[i]):
                    
                    severity = 'high' if abs(values[i] - values[i-1]) / values[i-1] > 0.2 else 'medium'
                    
                    reversals.append({
                        'index': i,
                        'severity': severity,
                        'description': f"Moving average crossover at index {i}"
                    })
        
        return reversals
    
    async def _detect_statistical_anomalies(self, financial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect statistical anomalies using machine learning."""
        anomalies = []
        
        try:
            # Prepare data for anomaly detection
            numeric_data = []
            feature_names = []
            
            for key, value in financial_data.items():
                if isinstance(value, (int, float)) and not np.isnan(value):
                    numeric_data.append(value)
                    feature_names.append(key)
            
            if len(numeric_data) < 3:
                return anomalies
            
            # Normalize data
            data_array = np.array(numeric_data).reshape(-1, 1)
            normalized_data = self.scaler.fit_transform(data_array)
            
            # Fit isolation forest
            self.isolation_forest.fit(normalized_data)
            
            # Predict anomalies
            predictions = self.isolation_forest.predict(normalized_data)
            scores = self.isolation_forest.score_samples(normalized_data)
            
            # Identify anomalies
            for i, (prediction, score) in enumerate(zip(predictions, scores)):
                if prediction == -1:  # Anomaly detected
                    anomaly = {
                        'type': 'statistical_anomaly',
                        'metric': feature_names[i],
                        'value': numeric_data[i],
                        'anomaly_score': float(score),
                        'severity': 'high' if score < -0.5 else 'medium',
                        'description': f"Statistical anomaly detected in {feature_names[i]}: {numeric_data[i]:.2f}",
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    anomalies.append(anomaly)
        
        except Exception as e:
            self.logger.error(f"Error detecting statistical anomalies: {str(e)}")
        
        return anomalies
    
    def _calculate_risk_level(self, anomalies: List[Dict[str, Any]]) -> str:
        """Calculate overall risk level."""
        if not anomalies:
            return 'low'
        
        high_severity_count = sum(1 for anomaly in anomalies if anomaly.get('severity') == 'high')
        medium_severity_count = sum(1 for anomaly in anomalies if anomaly.get('severity') == 'medium')
        
        if high_severity_count >= 3:
            return 'critical'
        elif high_severity_count >= 1 or medium_severity_count >= 3:
            return 'high'
        elif medium_severity_count >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_confidence_score(self, anomalies: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for anomaly detection."""
        if not anomalies:
            return 0.0
        
        # Base confidence on number and severity of anomalies
        total_anomalies = len(anomalies)
        high_severity_count = sum(1 for anomaly in anomalies if anomaly.get('severity') == 'high')
        
        # Higher confidence with more anomalies
        confidence = min(0.9, 0.5 + (total_anomalies * 0.1) + (high_severity_count * 0.1))
        
        return confidence
    
    def _generate_recommendations(self, anomalies: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on detected anomalies."""
        recommendations = []
        
        if not anomalies:
            recommendations.append("No anomalies detected. Financial data appears normal.")
            return recommendations
        
        # Categorize anomalies by type
        ratio_anomalies = [a for a in anomalies if a.get('type') == 'ratio_anomaly']
        trend_anomalies = [a for a in anomalies if a.get('type') == 'trend_anomaly']
        statistical_anomalies = [a for a in anomalies if a.get('type') == 'statistical_anomaly']
        
        # Generate type-specific recommendations
        if ratio_anomalies:
            recommendations.append("Review financial ratios that are outside normal ranges. Consider industry benchmarks.")
        
        if trend_anomalies:
            recommendations.append("Investigate sudden changes in financial trends. Verify data accuracy and business events.")
        
        if statistical_anomalies:
            recommendations.append("Examine unusual patterns in financial data. Consider external factors and business context.")
        
        # Generate severity-based recommendations
        high_severity_anomalies = [a for a in anomalies if a.get('severity') == 'high']
        if high_severity_anomalies:
            recommendations.append("URGENT: Address high-severity anomalies immediately. Consider consulting with financial experts.")
        
        # Generate general recommendations
        if len(anomalies) > 5:
            recommendations.append("Multiple anomalies detected. Consider comprehensive financial review and audit.")
        
        return recommendations
    
    async def get_anomaly_summary(self, anomalies: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of anomaly detection results."""
        summary = {
            'total_anomalies': len(anomalies.get('anomalies_detected', [])),
            'risk_level': anomalies.get('risk_level', 'low'),
            'confidence_score': anomalies.get('confidence_score', 0.0),
            'anomaly_types': {},
            'severity_distribution': {},
            'top_concerns': [],
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Categorize anomalies by type
        for anomaly in anomalies.get('anomalies_detected', []):
            anomaly_type = anomaly.get('type', 'unknown')
            if anomaly_type not in summary['anomaly_types']:
                summary['anomaly_types'][anomaly_type] = 0
            summary['anomaly_types'][anomaly_type] += 1
            
            # Categorize by severity
            severity = anomaly.get('severity', 'unknown')
            if severity not in summary['severity_distribution']:
                summary['severity_distribution'][severity] = 0
            summary['severity_distribution'][severity] += 1
        
        # Identify top concerns
        high_severity_anomalies = [
            a for a in anomalies.get('anomalies_detected', []) 
            if a.get('severity') == 'high'
        ]
        
        summary['top_concerns'] = [
            {
                'metric': anomaly.get('metric', 'unknown'),
                'value': anomaly.get('value', 0),
                'description': anomaly.get('description', 'No description')
            }
            for anomaly in high_severity_anomalies[:5]  # Top 5 concerns
        ]
        
        return summary
