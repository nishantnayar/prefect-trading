"""
Metrics Dashboard Component

This module provides the render_metrics_dashboard function to display
top-level model performance metrics in a clean, organized layout.
"""

import streamlit as st
from typing import Dict
import streamlit as st


@st.cache_data(ttl=300)  # 5 minutes cache
def get_cached_overview_metrics(_manager) -> Dict:
    """
    Get cached overview metrics to avoid repeated database calls.
    
    Args:
        _manager: ModelPerformanceManager instance
        
    Returns:
        Dict containing overview metrics
    """
    return _manager.get_overview_metrics()


def render_metrics_dashboard(manager):
    """
    Render the metrics dashboard with top-level performance indicators.
    
    Args:
        manager: ModelPerformanceManager instance
    """
    st.subheader("📈 Model Performance Overview")
    
    # Get cached metrics
    metrics = get_cached_overview_metrics(manager)
    
    # Display metrics in a clean 4-column layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_models = metrics.get('total_models', 0) or 0
        models_today = metrics.get('models_today', 0) or 0
        st.metric(
            "Total Models",
            f"{total_models:,}",
            f"+{models_today} today",
            help="Total number of models trained in the system"
        )
    
    with col2:
        # Determine delta color based on F1 change
        f1_change = metrics.get('f1_change', 0) or 0
        avg_f1_score = metrics.get('avg_f1_score', 0) or 0
        delta_color = "normal" if f1_change >= 0 else "inverse"
        delta_text = f"{f1_change:+.2f}%" if f1_change != 0 else "0.00%"
        
        st.metric(
            "Average F1 Score",
            f"{avg_f1_score:.4f}",
            delta_text,
            delta_color=delta_color,
            help="Average F1 score across all trained models"
        )
    
    with col3:
        best_pair = metrics.get('best_pair', 'N/A') or 'N/A'
        best_f1_score = metrics.get('best_f1_score', 0) or 0
        st.metric(
            "Best Performing Pair",
            best_pair,
            f"F1: {best_f1_score:.4f}",
            help="Pair with the highest F1 score"
        )
    
    with col4:
        # Color code based on activity level
        if models_today > 0:
            activity_color = "normal"
            activity_help = f"{models_today} models trained today"
        else:
            activity_color = "off"
            activity_help = "No models trained today"
        
        st.metric(
            "Training Activity",
            f"{models_today}",
            "models today",
            delta_color=activity_color,
            help=activity_help
        )
    
    # Add a small info section below metrics
    with st.expander("ℹ️ Performance Insights", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**System Health**")
            if avg_f1_score >= 0.65:
                st.success("✅ Excellent performance")
            elif avg_f1_score >= 0.60:
                st.warning("⚠️ Good performance")
            else:
                st.error("❌ Performance needs improvement")
        
        with col2:
            st.write("**Recent Activity**")
            if models_today > 0:
                st.success(f"✅ {models_today} models trained today")
            else:
                st.info("ℹ️ No training activity today")
        
        # Add performance trend indicator
        st.write("**Performance Trend**")
        if f1_change > 0:
            st.success(f"📈 F1 scores improving by {f1_change:.2f}%")
        elif f1_change < 0:
            st.error(f"📉 F1 scores declining by {abs(f1_change):.2f}%")
        else:
            st.info("➡️ F1 scores stable")
    
    # Add a divider
    st.divider() 