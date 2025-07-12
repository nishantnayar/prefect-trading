"""
Chart Helpers Utility

This module provides utility functions for creating and customizing
charts and visualizations.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional


class ChartHelpers:
    """
    Utility class for creating and customizing charts.
    """
    
    @staticmethod
    def create_performance_color_scale() -> List[str]:
        """
        Create a color scale for performance visualization.
        
        Returns:
            List of colors for different performance levels
        """
        return [
            '#d62728',  # Red for poor performance
            '#ff7f0e',  # Orange for moderate performance
            '#2ca02c',  # Green for good performance
            '#1f77b4'   # Blue for excellent performance
        ]
    
    @staticmethod
    def add_performance_thresholds(fig: go.Figure, thresholds: Dict[str, float]) -> go.Figure:
        """
        Add performance threshold lines to a chart.
        
        Args:
            fig: Plotly figure object
            thresholds: Dict with threshold values
            
        Returns:
            Updated figure with threshold lines
        """
        if 'excellent' in thresholds:
            fig.add_hline(
                y=thresholds['excellent'],
                line_dash="dash",
                line_color="green",
                annotation_text="Excellent"
            )
        
        if 'good' in thresholds:
            fig.add_hline(
                y=thresholds['good'],
                line_dash="dash",
                line_color="orange",
                annotation_text="Good"
            )
        
        return fig
    
    @staticmethod
    def create_metric_card(title: str, value: str, delta: Optional[str] = None, 
                          delta_color: str = "normal") -> str:
        """
        Create HTML for a metric card.
        
        Args:
            title: Card title
            value: Main value
            delta: Delta value (optional)
            delta_color: Color for delta ("normal", "inverse", "off")
            
        Returns:
            HTML string for the metric card
        """
        delta_html = ""
        if delta:
            delta_class = f"delta-{delta_color}" if delta_color != "normal" else "delta"
            delta_html = f'<div class="{delta_class}">{delta}</div>'
        
        return f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """
        Format a value as a percentage.
        
        Args:
            value: Value to format
            decimals: Number of decimal places
            
        Returns:
            Formatted percentage string
        """
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_f1_score(value: float, decimals: int = 4) -> str:
        """
        Format an F1 score.
        
        Args:
            value: F1 score value
            decimals: Number of decimal places
            
        Returns:
            Formatted F1 score string
        """
        return f"{value:.{decimals}f}" 