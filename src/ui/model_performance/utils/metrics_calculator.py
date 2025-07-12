"""
Metrics Calculator Utility

This module provides utility functions for calculating and analyzing
model performance metrics.
"""

import pandas as pd
from typing import Dict, List, Tuple


class MetricsCalculator:
    """
    Utility class for calculating and analyzing model performance metrics.
    """
    
    @staticmethod
    def calculate_performance_percentiles(f1_scores: List[float]) -> Dict[str, float]:
        """
        Calculate performance percentiles from F1 scores.
        
        Args:
            f1_scores: List of F1 scores
            
        Returns:
            Dict with percentile values
        """
        if not f1_scores:
            return {}
        
        df = pd.DataFrame({'f1_score': f1_scores})
        percentiles = df['f1_score'].quantile([0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
        
        return {
            'p25': percentiles[0.25],
            'p50': percentiles[0.5],
            'p75': percentiles[0.75],
            'p90': percentiles[0.9],
            'p95': percentiles[0.95],
            'p99': percentiles[0.99]
        }
    
    @staticmethod
    def calculate_performance_categories(f1_scores: List[float]) -> Dict[str, int]:
        """
        Categorize models by performance level.
        
        Args:
            f1_scores: List of F1 scores
            
        Returns:
            Dict with category counts
        """
        if not f1_scores:
            return {}
        
        excellent = sum(1 for score in f1_scores if score >= 0.65)
        good = sum(1 for score in f1_scores if 0.60 <= score < 0.65)
        needs_improvement = sum(1 for score in f1_scores if score < 0.60)
        
        return {
            'excellent': excellent,
            'good': good,
            'needs_improvement': needs_improvement,
            'total': len(f1_scores)
        }
    
    @staticmethod
    def calculate_trend_metrics(historical_data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate trend metrics from historical data.
        
        Args:
            historical_data: DataFrame with date and F1 score columns
            
        Returns:
            Dict with trend metrics
        """
        if historical_data.empty:
            return {}
        
        # Calculate moving averages
        ma_7d = historical_data['f1_score'].rolling(7).mean().iloc[-1]
        ma_30d = historical_data['f1_score'].rolling(30).mean().iloc[-1]
        
        # Calculate trend
        if len(historical_data) >= 2:
            first_score = historical_data['f1_score'].iloc[0]
            last_score = historical_data['f1_score'].iloc[-1]
            trend = ((last_score - first_score) / first_score) * 100
        else:
            trend = 0.0
        
        return {
            'ma_7d': ma_7d,
            'ma_30d': ma_30d,
            'trend_percent': trend
        } 