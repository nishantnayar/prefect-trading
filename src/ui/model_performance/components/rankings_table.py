"""
Rankings Table Component

This module provides the render_rankings_table function to display
model rankings in an interactive table with filtering and sorting.
"""

import streamlit as st
import pandas as pd
from typing import List
from decimal import Decimal


def _safe_float(value):
    """Safely convert value to float, handling decimal.Decimal."""
    if isinstance(value, Decimal):
        return float(value)
    if pd.isna(value):
        return 0.0
    return float(value)


@st.cache_data(ttl=60)  # 1 minute cache for rankings
def get_cached_rankings(_manager, limit: int = 50) -> pd.DataFrame:
    """
    Get cached rankings data to avoid repeated database calls.
    
    Args:
        _manager: ModelPerformanceManager instance
        limit: Maximum number of rankings to return
        
    Returns:
        DataFrame with rankings data
    """
    return _manager.get_rankings(limit)


def render_rankings_table(manager):
    """
    Render the rankings table with interactive filtering and sorting.
    
    Args:
        manager: ModelPerformanceManager instance
    """
    st.subheader("🏆 Top Performing Pairs")
    
    # Get cached rankings data
    rankings_df = get_cached_rankings(manager, limit=50)
    
    if rankings_df.empty:
        st.info("No rankings data available. Run training to generate rankings.")
        return
    
    # Get unique pairs for filter
    all_pairs = rankings_df['pair_symbol'].unique().tolist()
    
    # Create filters
    col1, col2 = st.columns(2)
    
    with col1:
        min_f1 = st.slider(
            "Minimum F1 Score",
            min_value=_safe_float(rankings_df['f1_score'].min()),
            max_value=_safe_float(rankings_df['f1_score'].max()),
            value=_safe_float(rankings_df['f1_score'].min()),
            step=0.01,
            help="Filter pairs by minimum F1 score"
        )
    
    with col2:
        selected_pairs = st.multiselect(
            "Filter by Pairs",
            options=all_pairs,
            default=all_pairs[:10] if len(all_pairs) <= 10 else [],
            help="Select specific pairs to display"
        )
    
    # Apply filters
    filtered_df = rankings_df[
        (rankings_df['f1_score'] >= min_f1) & 
        (rankings_df['pair_symbol'].isin(selected_pairs))
    ].copy()
    
    if filtered_df.empty:
        st.warning("No pairs match the selected filters.")
        return
    
    # Add performance indicators
    def get_performance_indicator(f1_score):
        """Get performance indicator based on F1 score."""
        if f1_score >= 0.65:
            return "🟢 Excellent"
        elif f1_score >= 0.60:
            return "🟡 Good"
        else:
            return "🔴 Needs Improvement"
    
    filtered_df['performance'] = filtered_df['f1_score'].apply(get_performance_indicator)
    
    # Display the filtered data
    st.dataframe(
        filtered_df[['rank_position', 'pair_symbol', 'f1_score', 'accuracy', 'precision', 'recall', 'performance', 'training_date']],
        column_config={
            "rank_position": st.column_config.NumberColumn(
                "Rank",
                format="%d",
                help="Ranking position based on F1 score"
            ),
            "pair_symbol": st.column_config.TextColumn(
                "Pair",
                help="Trading pair symbol"
            ),
            "f1_score": st.column_config.NumberColumn(
                "F1 Score",
                format="%.4f",
                help="F1 score (harmonic mean of precision and recall)"
            ),
            "accuracy": st.column_config.NumberColumn(
                "Accuracy",
                format="%.4f",
                help="Model accuracy"
            ),
            "precision": st.column_config.NumberColumn(
                "Precision",
                format="%.4f",
                help="Model precision"
            ),
            "recall": st.column_config.NumberColumn(
                "Recall",
                format="%.4f",
                help="Model recall"
            ),
            "performance": st.column_config.TextColumn(
                "Performance",
                help="Performance category based on F1 score"
            ),
            "training_date": st.column_config.DatetimeColumn(
                "Last Updated",
                format="MM/DD/YY HH:mm",
                help="Date and time of last training"
            )
        },
        hide_index=True,
        use_container_width=True,
        column_order=["rank_position", "pair_symbol", "f1_score", "performance", "accuracy", "precision", "recall", "training_date"]
    )
    
    # Add download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        "📥 Download Rankings CSV",
        csv,
        f"model_rankings_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv",
        help="Download the filtered rankings data as CSV"
    )
    
    # Add summary statistics
    with st.expander("📊 Rankings Summary", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Pairs",
                len(filtered_df),
                help="Number of pairs in current view"
            )
        
        with col2:
            avg_f1 = _safe_float(filtered_df['f1_score'].mean())
            st.metric(
                "Average F1",
                f"{avg_f1:.4f}",
                help="Average F1 score of displayed pairs"
            )
        
        with col3:
            best_f1 = _safe_float(filtered_df['f1_score'].max())
            st.metric(
                "Best F1",
                f"{best_f1:.4f}",
                help="Highest F1 score in current view"
            )
        
        with col4:
            excellent_count = len(filtered_df[filtered_df['f1_score'] >= 0.65])
            st.metric(
                "Excellent Models",
                excellent_count,
                help="Number of models with F1 ≥ 0.65"
            )
    
    # Add a divider
    st.divider() 