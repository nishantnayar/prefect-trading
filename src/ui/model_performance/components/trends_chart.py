"""
Trends Chart Component

This module provides the render_trends_chart function to display
performance trends using plotly charts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from decimal import Decimal


def _safe_float(value):
    """Safely convert value to float, handling decimal.Decimal."""
    if isinstance(value, Decimal):
        return float(value)
    if pd.isna(value):
        return 0.0
    return float(value)


@st.cache_data(ttl=600)  # 10 minutes cache for trends
def get_cached_trends(_manager, days: int = 30) -> pd.DataFrame:
    """
    Get cached trends data to avoid repeated database calls.
    
    Args:
        _manager: ModelPerformanceManager instance
        days: Number of days to look back
        
    Returns:
        DataFrame with trends data
    """
    return _manager.get_trends(days)


def render_trends_chart(manager):
    """
    Render the trends chart with performance metrics over time.
    
    Args:
        manager: ModelPerformanceManager instance
    """
    st.subheader("📊 Performance Trends")
    
    # Period selector
    col1, col2 = st.columns([1, 3])
    
    with col1:
        period_days = st.selectbox(
            "Time Period",
            options=[7, 30, 90],
            format_func=lambda x: f"{x} Days",
            help="Select the time period for trend analysis"
        )
    
    with col2:
        st.write("")  # Spacer for alignment
    
    # Get cached trends data
    trends_df = get_cached_trends(manager, days=period_days)
    
    if trends_df.empty:
        st.info("No trends data available. Run training to generate trends.")
        return
    
    # Sort by date for proper charting
    trends_df = trends_df.sort_values('trend_date')
    
    # Create the main trends chart
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Average F1 Scores Over Time', 'Model Counts Over Time'),
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3]
    )
    
    # Add F1 score lines
    fig.add_trace(
        go.Scatter(
            x=trends_df['trend_date'],
            y=trends_df['avg_f1_7d'],
            mode='lines+markers',
            name='7-Day Average',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=trends_df['trend_date'],
            y=trends_df['avg_f1_30d'],
            mode='lines+markers',
            name='30-Day Average',
            line=dict(color='#ff7f0e', width=2),
            marker=dict(size=6)
        ),
        row=1, col=1
    )
    
    # Add best F1 scores
    fig.add_trace(
        go.Scatter(
            x=trends_df['trend_date'],
            y=trends_df['best_f1_7d'],
            mode='lines+markers',
            name='Best 7-Day',
            line=dict(color='#2ca02c', width=2, dash='dash'),
            marker=dict(size=4)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=trends_df['trend_date'],
            y=trends_df['best_f1_30d'],
            mode='lines+markers',
            name='Best 30-Day',
            line=dict(color='#d62728', width=2, dash='dash'),
            marker=dict(size=4)
        ),
        row=1, col=1
    )
    
    # Add model counts
    fig.add_trace(
        go.Bar(
            x=trends_df['trend_date'],
            y=trends_df['model_count_7d'],
            name='7-Day Models',
            marker_color='#1f77b4',
            opacity=0.7
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=trends_df['trend_date'],
            y=trends_df['model_count_30d'],
            name='30-Day Models',
            marker_color='#ff7f0e',
            opacity=0.7
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        title=f"Performance Trends - Last {period_days} Days",
        height=600,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )
    
    # Update axes
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="F1 Score", row=1, col=1)
    fig.update_yaxes(title_text="Model Count", row=2, col=1)
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Display current metrics
    if not trends_df.empty:
        latest = trends_df.iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "7-Day Avg F1",
                f"{latest['avg_f1_7d']:.4f}" if pd.notna(latest['avg_f1_7d']) else "N/A",
                help="Average F1 score over the last 7 days"
            )
        
        with col2:
            st.metric(
                "30-Day Avg F1",
                f"{latest['avg_f1_30d']:.4f}" if pd.notna(latest['avg_f1_30d']) else "N/A",
                help="Average F1 score over the last 30 days"
            )
        
        with col3:
            st.metric(
                "Best 7-Day F1",
                f"{latest['best_f1_7d']:.4f}" if pd.notna(latest['best_f1_7d']) else "N/A",
                help="Best F1 score in the last 7 days"
            )
        
        with col4:
            st.metric(
                "Best 30-Day F1",
                f"{latest['best_f1_30d']:.4f}" if pd.notna(latest['best_f1_30d']) else "N/A",
                help="Best F1 score in the last 30 days"
            )
    
    # Add trend analysis
    with st.expander("📈 Trend Analysis", expanded=False):
        if len(trends_df) >= 2:
            # Calculate trends
            first_7d = _safe_float(trends_df.iloc[0]['avg_f1_7d'])
            last_7d = _safe_float(trends_df.iloc[-1]['avg_f1_7d'])
            first_30d = _safe_float(trends_df.iloc[0]['avg_f1_30d'])
            last_30d = _safe_float(trends_df.iloc[-1]['avg_f1_30d'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**7-Day Trend**")
                if pd.notna(first_7d) and pd.notna(last_7d):
                    change_7d = ((last_7d - first_7d) / first_7d) * 100
                    if change_7d > 0:
                        st.success(f"📈 Improving by {change_7d:.2f}%")
                    elif change_7d < 0:
                        st.error(f"📉 Declining by {abs(change_7d):.2f}%")
                    else:
                        st.info("➡️ Stable")
                else:
                    st.info("ℹ️ Insufficient data")
            
            with col2:
                st.write("**30-Day Trend**")
                if pd.notna(first_30d) and pd.notna(last_30d):
                    change_30d = ((last_30d - first_30d) / first_30d) * 100
                    if change_30d > 0:
                        st.success(f"📈 Improving by {change_30d:.2f}%")
                    elif change_30d < 0:
                        st.error(f"📉 Declining by {abs(change_30d):.2f}%")
                    else:
                        st.info("➡️ Stable")
                else:
                    st.info("ℹ️ Insufficient data")
        else:
            st.info("Need at least 2 data points for trend analysis")
    
    # Add a divider
    st.divider() 