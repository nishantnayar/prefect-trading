"""
Model Performance Dashboard UI Module

This module provides the UI components for displaying model performance metrics,
rankings, trends, and training history in a comprehensive dashboard.
"""

from .main import render_model_performance
from .components.metrics_dashboard import render_metrics_dashboard
from .components.rankings_table import render_rankings_table
from .components.trends_chart import render_trends_chart
from .components.training_history import render_training_history
from .components.performance_analytics import render_performance_analytics
from .components.model_details import render_model_details

__all__ = [
    'render_model_performance',
    'render_metrics_dashboard',
    'render_rankings_table',
    'render_trends_chart',
    'render_training_history',
    'render_performance_analytics',
    'render_model_details'
] 