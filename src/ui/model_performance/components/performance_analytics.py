"""
Performance Analytics Component

This module provides the render_performance_analytics function to display
various performance analytics charts and visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from decimal import Decimal


def _safe_float(value):
    """Safely convert value to float, handling decimal.Decimal."""
    if isinstance(value, Decimal):
        return float(value)
    if pd.isna(value):
        return 0.0
    return float(value)


@st.cache_data(ttl=300)  # 5 minutes cache for analytics data
def get_cached_analytics_data(_manager):
    """
    Get cached analytics data to avoid repeated database calls.
    
    Args:
        _manager: ModelPerformanceManager instance
        
    Returns:
        Tuple of (f1_distribution, accuracy_precision, training_history) DataFrames
    """
    f1_dist = _manager.get_f1_distribution()
    acc_prec = _manager.get_accuracy_precision_data()
    train_hist = _manager.get_training_history()
    return f1_dist, acc_prec, train_hist


def render_performance_analytics(manager):
    """
    Render the performance analytics section with multiple charts.
    
    Args:
        manager: ModelPerformanceManager instance
    """
    st.subheader("📊 Performance Analytics")
    
    # Get cached analytics data
    f1_dist_df, acc_prec_df, train_hist_df = get_cached_analytics_data(manager)
    
    # Create tabs for different analytics
    tab1, tab2, tab3 = st.tabs(["F1 Distribution", "Accuracy vs Precision", "Training History"])
    
    with tab1:
        render_f1_distribution(f1_dist_df)
    
    with tab2:
        render_accuracy_precision(acc_prec_df)
    
    with tab3:
        render_training_history_chart(train_hist_df)
    
    # Add a divider
    st.divider()


def render_f1_distribution(f1_dist_df):
    """Render F1 score distribution histogram."""
    st.write("**F1 Score Distribution**")
    
    if f1_dist_df.empty:
        st.info("No F1 distribution data available.")
        return
    
    # Create histogram
    fig = px.histogram(
        f1_dist_df,
        x='f1_score',
        nbins=20,
        title="F1 Score Distribution",
        labels={'f1_score': 'F1 Score', 'count': 'Number of Models'},
        color_discrete_sequence=['#1f77b4']
    )
    
    # Add vertical lines for performance thresholds
    fig.add_vline(x=0.65, line_dash="dash", line_color="green", 
                  annotation_text="Excellent (0.65)")
    fig.add_vline(x=0.60, line_dash="dash", line_color="orange", 
                  annotation_text="Good (0.60)")
    
    fig.update_layout(
        xaxis_title="F1 Score",
        yaxis_title="Number of Models",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        mean_f1 = _safe_float(f1_dist_df['f1_score'].mean()) if not f1_dist_df.empty else 0.0
        st.metric("Mean F1", f"{mean_f1:.4f}")
    
    with col2:
        median_f1 = _safe_float(f1_dist_df['f1_score'].median()) if not f1_dist_df.empty else 0.0
        st.metric("Median F1", f"{median_f1:.4f}")
    
    with col3:
        std_f1 = _safe_float(f1_dist_df['f1_score'].std()) if not f1_dist_df.empty else 0.0
        st.metric("Std Dev", f"{std_f1:.4f}")
    
    with col4:
        excellent_count = len(f1_dist_df[f1_dist_df['f1_score'] >= 0.65])
        total_count = len(f1_dist_df)
        excellent_pct = (excellent_count / total_count) * 100 if total_count > 0 else 0
        st.metric("Excellent %", f"{excellent_pct:.1f}%")


def render_accuracy_precision(acc_prec_df):
    """Render accuracy vs precision scatter plot."""
    st.write("**Accuracy vs Precision Analysis**")
    
    if acc_prec_df.empty:
        st.info("No accuracy-precision data available.")
        return
    
    # Create scatter plot
    fig = px.scatter(
        acc_prec_df,
        x='accuracy',
        y='precision',
        color='f1_score',
        size='f1_score',
        hover_data=['pair_symbol'],
        title="Accuracy vs Precision",
        labels={'accuracy': 'Accuracy', 'precision': 'Precision', 'f1_score': 'F1 Score'},
        color_continuous_scale='viridis'
    )
    
    # Add diagonal line for reference
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode='lines',
            line=dict(dash='dash', color='gray'),
            name='Perfect Line',
            showlegend=True
        )
    )
    
    fig.update_layout(
        xaxis_title="Accuracy",
        yaxis_title="Precision",
        xaxis=dict(range=[0, 1]),
        yaxis=dict(range=[0, 1])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add correlation analysis
    correlation = acc_prec_df['accuracy'].corr(acc_prec_df['precision'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        correlation_safe = _safe_float(correlation) if not pd.isna(correlation) else 0.0
        st.metric("Accuracy-Precision Correlation", f"{correlation_safe:.3f}")
    
    with col2:
        avg_accuracy = _safe_float(acc_prec_df['accuracy'].mean()) if not acc_prec_df.empty else 0.0
        st.metric("Average Accuracy", f"{avg_accuracy:.4f}")
    
    with col3:
        avg_precision = _safe_float(acc_prec_df['precision'].mean()) if not acc_prec_df.empty else 0.0
        st.metric("Average Precision", f"{avg_precision:.4f}")


def render_training_history_chart(train_hist_df):
    """Render training history over time."""
    st.write("**Training History Over Time**")
    
    if train_hist_df.empty:
        st.info("No training history data available.")
        return
    
    # Create line chart
    fig = px.line(
        train_hist_df,
        x='training_date',
        y='f1_score',
        color='pair_symbol',
        title="F1 Score Over Time",
        labels={'training_date': 'Date', 'f1_score': 'F1 Score', 'pair_symbol': 'Pair'},
        hover_data=['pair_symbol']
    )
    
    # Add horizontal line for excellent threshold
    fig.add_hline(y=0.65, line_dash="dash", line_color="green", 
                  annotation_text="Excellent Threshold (0.65)")
    
    fig.update_layout(
        xaxis_title="Training Date",
        yaxis_title="F1 Score",
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add time-based statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Recent performance (last 7 days)
        recent_data = train_hist_df[train_hist_df['training_date'] >= pd.Timestamp.now() - pd.Timedelta(days=7)]
        if not recent_data.empty:
            recent_avg = _safe_float(recent_data['f1_score'].mean())
            st.metric("7-Day Avg F1", f"{recent_avg:.4f}")
        else:
            st.metric("7-Day Avg F1", "N/A")
    
    with col2:
        # Best recent performance
        if not train_hist_df.empty:
            best_recent = _safe_float(train_hist_df['f1_score'].max())
            best_pair = train_hist_df.loc[train_hist_df['f1_score'].idxmax(), 'pair_symbol']
            st.metric("Best Recent F1", f"{best_recent:.4f}", f"({best_pair})")
        else:
            st.metric("Best Recent F1", "N/A")
    
    with col3:
        # Performance trend
        if len(train_hist_df) >= 2:
            first_f1 = _safe_float(train_hist_df.iloc[0]['f1_score'])
            last_f1 = _safe_float(train_hist_df.iloc[-1]['f1_score'])
            trend = ((last_f1 - first_f1) / first_f1) * 100 if first_f1 > 0 else 0.0
            st.metric("Performance Trend", f"{trend:+.1f}%")
        else:
            st.metric("Performance Trend", "N/A") 