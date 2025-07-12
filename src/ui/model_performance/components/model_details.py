"""
Model Details Component

This module provides the render_model_details function to display
detailed information about a specific model pair.
"""

import streamlit as st
import pandas as pd
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from functools import lru_cache


@st.cache_data(ttl=300)  # 5 minutes cache for model details
def get_cached_model_details(_manager, pair_symbol: str):
    """
    Get cached model details to avoid repeated database calls.
    
    Args:
        _manager: ModelPerformanceManager instance
        pair_symbol: The pair symbol to get details for
        
    Returns:
        Dict containing model details
    """
    return _manager.get_model_details(pair_symbol)


@lru_cache(maxsize=32)
def get_mlflow_experiment_id(experiment_name: str) -> str:
    """
    Look up the MLflow experiment ID by name using direct DB access.
    Returns the experiment ID as a string, or None if not found.
    """
    conn = psycopg2.connect(
        host=os.getenv("MLFLOW_DB_HOST"),
        port=os.getenv("MLFLOW_DB_PORT"),
        dbname=os.getenv("MLFLOW_DB_NAME"),
        user=os.getenv("MLFLOW_DB_USER"),
        password=os.getenv("MLFLOW_DB_PASSWORD"),
    )
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT experiment_id FROM experiments WHERE name = %s", (experiment_name,))
            row = cur.fetchone()
            return str(row["experiment_id"]) if row else None
    finally:
        conn.close()


def render_model_details(manager):
    """
    Render the model details section with pair selector and detailed view.
    
    Args:
        manager: ModelPerformanceManager instance
    """
    st.subheader("📋 Model Details")
    
    # Get available pairs for selection
    rankings_df = manager.get_rankings(limit=100)
    
    if rankings_df.empty:
        st.info("No model data available. Run training to see model details.")
        return
    
    # Get unique pairs
    available_pairs = sorted(rankings_df['pair_symbol'].unique().tolist())
    
    # Pair selector
    selected_pair = st.selectbox(
        "Select Pair for Details",
        options=available_pairs,
        help="Choose a trading pair to view detailed model information"
    )
    
    if selected_pair:
        # Get cached model details
        details = get_cached_model_details(manager, selected_pair)
        
        if not details:
            st.warning(f"No details available for {selected_pair}")
            return
        
        # Display model details in expander
        with st.expander(f"📋 Model Details: {selected_pair}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("🎯 Performance Metrics")
                
                # Performance metrics with color coding
                f1_score = details.get('f1_score', 0) or 0
                accuracy = details.get('accuracy', 0) or 0
                precision = details.get('precision', 0) or 0
                recall = details.get('recall', 0) or 0
                auc_score = details.get('auc_score', 0) or 0
                
                # F1 Score with color coding
                if f1_score >= 0.65:
                    st.success(f"**F1 Score:** {f1_score:.4f} 🟢")
                elif f1_score >= 0.60:
                    st.warning(f"**F1 Score:** {f1_score:.4f} 🟡")
                else:
                    st.error(f"**F1 Score:** {f1_score:.4f} 🔴")
                
                st.metric("Accuracy", f"{accuracy:.4f}")
                st.metric("Precision", f"{precision:.4f}")
                st.metric("Recall", f"{recall:.4f}")
                st.metric("AUC Score", f"{auc_score:.4f}")
            
            with col2:
                st.subheader("🏋️ Training Info")
                
                epochs_trained = details.get('epochs_trained', 0) or 0
                early_stopped = details.get('early_stopped', False) or False
                loss = details.get('loss', 0) or 0
                val_loss = details.get('val_loss', 0) or 0
                training_date = details.get('training_date')
                
                st.metric("Epochs Trained", epochs_trained)
                
                if early_stopped:
                    st.warning("⏹️ Early Stopped")
                else:
                    st.success("✅ Complete Training")
                
                st.metric("Training Loss", f"{loss:.4f}")
                st.metric("Validation Loss", f"{val_loss:.4f}")
                
                if training_date:
                    st.metric("Training Date", training_date.strftime('%Y-%m-%d %H:%M'))
            
            with col3:
                st.subheader("🔗 MLflow Details")
                
                model_run_id = details.get('model_run_id', 'N/A') or 'N/A'
                experiment_name = details.get('experiment_name', 'N/A') or 'N/A'
                
                st.metric("Experiment", experiment_name)
                st.metric("Status", "✅ Registered")
                
                # MLflow link
                if model_run_id != 'N/A' and experiment_name != 'N/A':
                    # The experiment_name is actually the experiment_id in our database
                    experiment_id = experiment_name
                    base_url = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
                    mlflow_url = f"{base_url}/#/experiments/{experiment_id}/runs/{model_run_id}"
                    st.link_button(
                        "🔗 View in MLflow",
                        mlflow_url,
                        help=f"Open {selected_pair} experiment in MLflow"
                    )
        
        # Add hyperparameters section
        with st.expander("⚙️ Hyperparameters", expanded=False):
            hyperparameters = details.get('hyperparameters')
            
            if hyperparameters:
                if isinstance(hyperparameters, str):
                    try:
                        # Try to parse JSON string
                        hyperparams_dict = json.loads(hyperparameters)
                    except json.JSONDecodeError:
                        st.write(f"**Raw Hyperparameters:** {hyperparameters}")
                        hyperparams_dict = None
                else:
                    hyperparams_dict = hyperparameters
                
                if hyperparams_dict:
                    # Display as formatted JSON
                    st.json(hyperparams_dict)
                    
                    # Also display as key-value pairs
                    st.write("**Key Parameters:**")
                    for key, value in hyperparams_dict.items():
                        st.write(f"- **{key}:** {value}")
                else:
                    st.write(f"**Raw Hyperparameters:** {hyperparameters}")
            else:
                st.info("No hyperparameters available")
        
        # Add performance comparison
        with st.expander("📊 Performance Comparison", expanded=False):
            # Compare with other pairs
            other_pairs = rankings_df[rankings_df['pair_symbol'] != selected_pair]
            
            if not other_pairs.empty:
                current_rank = rankings_df[rankings_df['pair_symbol'] == selected_pair]['rank_position'].iloc[0]
                total_pairs = len(rankings_df)
                percentile = ((total_pairs - current_rank + 1) / total_pairs) * 100
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Current Rank", f"{current_rank}/{total_pairs}")
                
                with col2:
                    st.metric("Percentile", f"{percentile:.1f}%")
                
                with col3:
                    better_than = len(other_pairs[other_pairs['f1_score'] < f1_score])
                    st.metric("Better Than", f"{better_than} pairs")
                
                # Show top 5 pairs for comparison
                st.write("**Top 5 Performing Pairs:**")
                top_5 = rankings_df.head(5)[['rank_position', 'pair_symbol', 'f1_score']]
                
                for _, row in top_5.iterrows():
                    if row['pair_symbol'] == selected_pair:
                        st.write(f"**{row['rank_position']}. {row['pair_symbol']} - {row['f1_score']:.4f}** (Current)")
                    else:
                        st.write(f"{row['rank_position']}. {row['pair_symbol']} - {row['f1_score']:.4f}")
            else:
                st.info("No comparison data available")
        
        # Add a divider
        st.divider() 