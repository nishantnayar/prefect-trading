"""
Training History Component

This module provides the render_training_history function to display
recent training activity in an interactive table.
"""

import streamlit as st
import pandas as pd
from decimal import Decimal


def _safe_float(value):
    """Safely convert value to float, handling decimal.Decimal."""
    if isinstance(value, Decimal):
        return float(value)
    if pd.isna(value):
        return 0.0
    return float(value)


@st.cache_data(ttl=30)  # 30 seconds cache for recent activity
def get_cached_training_history(_manager, limit: int = 20) -> pd.DataFrame:
    """
    Get cached training history data to avoid repeated database calls.
    
    Args:
        _manager: ModelPerformanceManager instance
        limit: Maximum number of recent training records to return
        
    Returns:
        DataFrame with training history data
    """
    return _manager.get_recent_training(limit)


def render_training_history(manager):
    """
    Render the training history table with recent activity.
    
    Args:
        manager: ModelPerformanceManager instance
    """
    st.subheader("🔄 Recent Training Activity")
    
    # Get cached training history
    history_df = get_cached_training_history(manager, limit=20)
    
    if history_df.empty:
        st.info("No recent training activity. Run training to see activity.")
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
    
    history_df['performance'] = history_df['f1_score'].apply(get_performance_indicator)
    
    # Add early stopping indicator
    def get_early_stop_indicator(early_stopped):
        """Get early stopping indicator."""
        return "⏹️ Early Stop" if early_stopped else "✅ Complete"
    
    history_df['training_status'] = history_df['early_stopped'].apply(get_early_stop_indicator)
    
    # Display the training history
    st.dataframe(
        history_df[['pair_symbol', 'f1_score', 'accuracy', 'performance', 'training_status', 'epochs_trained', 'training_date']],
        column_config={
            "pair_symbol": st.column_config.TextColumn(
                "Pair",
                help="Trading pair symbol"
            ),
            "f1_score": st.column_config.NumberColumn(
                "F1 Score",
                format="%.4f",
                help="F1 score achieved"
            ),
            "accuracy": st.column_config.NumberColumn(
                "Accuracy",
                format="%.4f",
                help="Model accuracy"
            ),
            "performance": st.column_config.TextColumn(
                "Performance",
                help="Performance category based on F1 score"
            ),
            "training_status": st.column_config.TextColumn(
                "Status",
                help="Training completion status"
            ),
            "epochs_trained": st.column_config.NumberColumn(
                "Epochs",
                format="%d",
                help="Number of epochs trained"
            ),
            "training_date": st.column_config.DatetimeColumn(
                "Timestamp",
                format="MM/DD/YY HH:mm",
                help="Training completion time"
            )
        },
        hide_index=True,
        use_container_width=True,
        column_order=["pair_symbol", "f1_score", "performance", "accuracy", "training_status", "epochs_trained", "training_date"]
    )
    
    # Add summary statistics
    with st.expander("📊 Training Summary", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_models = len(history_df)
            st.metric(
                "Total Models",
                total_models,
                help="Number of models in recent history"
            )
        
        with col2:
            avg_f1 = _safe_float(history_df['f1_score'].mean())
            st.metric(
                "Average F1",
                f"{avg_f1:.4f}",
                help="Average F1 score of recent models"
            )
        
        with col3:
            excellent_count = len(history_df[history_df['f1_score'] >= 0.65])
            st.metric(
                "Excellent Models",
                excellent_count,
                help="Number of models with F1 ≥ 0.65"
            )
        
        with col4:
            early_stop_count = len(history_df[history_df['early_stopped'] == True])
            st.metric(
                "Early Stops",
                early_stop_count,
                help="Number of models that stopped early"
            )
    
    # Add MLflow integration info
    with st.expander("🔗 MLflow Integration", expanded=False):
        st.write("**Recent MLflow Runs**")
        
        # Show recent runs with MLflow links
        recent_runs = history_df[['pair_symbol', 'f1_score', 'model_run_id', 'experiment_name', 'training_date']].head(5)
        
        for _, run in recent_runs.iterrows():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{run['pair_symbol']}** - F1: {run['f1_score']:.4f}")
            
            with col2:
                # Create MLflow link (placeholder - would need actual MLflow URL)
                mlflow_url = f"http://localhost:5000/#/experiments/{run['experiment_name']}/runs/{run['model_run_id']}"
                st.link_button("View in MLflow", mlflow_url, help=f"Open {run['pair_symbol']} in MLflow")
            
            with col3:
                st.write(f"`{run['model_run_id'][:12]}...`")
        
        st.info("💡 Click 'View in MLflow' to see detailed experiment information")
    
    # Add a divider
    st.divider() 