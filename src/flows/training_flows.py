"""
Prefect flows for model training with preprocessing integration.

This module provides Prefect flows and tasks for:
1. Model training with preprocessed data
2. MLflow integration and experiment tracking
3. Performance monitoring and reporting
4. Model deployment and management
"""

from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
import pandas as pd
from prefect import flow, task, get_run_logger
from prefect.artifacts import create_markdown_artifact
import mlflow
import mlflow.pytorch

from src.ml.train_gru_models import run_gru_training, prepare_pairs_data_from_features
from src.ml.mlflow_manager import MLflowManager
from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.symbol_manager import SymbolManager
from src.flows.preprocessing_flows import data_preprocessing_flow


@task(name="Prepare Training Data")
def prepare_training_data_task(
    stable_features: pd.DataFrame,
    stable_symbols: List[str],
    top_pairs: int = 20
) -> List[pd.DataFrame]:
    """
    Prepare training data from stable features.
    
    Args:
        stable_features: DataFrame with stable features
        stable_symbols: List of stable symbols
        top_pairs: Number of top pairs to use for training
        
    Returns:
        List of pair DataFrames for training
    """
    logger = get_run_logger()
    logger.info(f"Preparing training data for {len(stable_symbols)} stable symbols")
    
    try:
        pairs_data_list = prepare_pairs_data_from_features(
            stable_features, stable_symbols, top_pairs
        )
        logger.info(f"Prepared {len(pairs_data_list)} pairs for training")
        return pairs_data_list
    except Exception as e:
        logger.error(f"Error preparing training data: {e}")
        raise


@task(name="Train GRU Models")
def train_gru_models_task(
    pairs_data_list: List[pd.DataFrame],
    sectors: Optional[List[str]] = None,
    use_preprocessing: bool = False  # We already have preprocessed data
) -> Tuple[Any, Dict, Any]:
    """
    Train GRU models for pairs trading.
    
    Args:
        pairs_data_list: List of pair DataFrames for training
        sectors: List of sectors (for MLflow tracking)
        use_preprocessing: Whether to use preprocessing (should be False here)
        
    Returns:
        Tuple of (model, history, trainer)
    """
    logger = get_run_logger()
    logger.info(f"Training GRU models for {len(pairs_data_list)} pairs")
    
    try:
        # Set up MLflow
        mlflow_manager = MLflowManager()
        mlflow_manager.setup_experiment()
        
        # Train models
        model, history, trainer = run_gru_training(
            sectors=sectors,
            use_preprocessing=use_preprocessing  # We already have preprocessed data
        )
        
        logger.info("GRU model training completed successfully")
        return model, history, trainer
    except Exception as e:
        logger.error(f"Error training GRU models: {e}")
        raise


@task(name="Create Training Report")
def create_training_report_task(
    pairs_data_list: List[pd.DataFrame],
    stable_symbols: List[str],
    test_results: List[Dict],
    training_results: Optional[Dict] = None
) -> str:
    """
    Create a markdown report of the training results.
    
    Args:
        pairs_data_list: List of pair DataFrames used for training
        stable_symbols: List of stable symbols
        test_results: Variance stability test results
        training_results: Optional training performance results
        
    Returns:
        Markdown report string
    """
    logger = get_run_logger()
    
    # Calculate statistics
    total_pairs = len(pairs_data_list)
    total_data_points = sum(len(pair_df) for pair_df in pairs_data_list) if pairs_data_list else 0
    
    # Create markdown report
    report = f"""
# Model Training Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Training Summary

- **Stable Symbols:** {len(stable_symbols)}
- **Training Pairs:** {total_pairs}
- **Total Data Points:** {total_data_points:,}
- **Variance Stability Rate:** {(len([r for r in test_results if r.get('is_stable', False)]) / len(test_results) * 100) if test_results else 0:.1f}%

## Stable Symbols Used for Training

"""
    
    for symbol in stable_symbols[:20]:  # Show first 20
        report += f"- **{symbol}**\n"
    
    if len(stable_symbols) > 20:
        report += f"- ... and {len(stable_symbols) - 20} more\n"
    
    report += f"""
## Training Pairs

"""
    
    for i, pair_df in enumerate(pairs_data_list[:10]):  # Show first 10
        if len(pair_df) > 0:
            symbol1 = pair_df['symbol1'].iloc[0] if 'symbol1' in pair_df.columns else 'Unknown'
            symbol2 = pair_df['symbol2'].iloc[0] if 'symbol2' in pair_df.columns else 'Unknown'
            correlation = pair_df['correlation'].iloc[0] if 'correlation' in pair_df.columns else 'N/A'
            data_points = len(pair_df)
            report += f"- **{symbol1}-{symbol2}:** {correlation:.4f} correlation, {data_points:,} data points\n"
    
    if len(pairs_data_list) > 10:
        report += f"- ... and {len(pairs_data_list) - 10} more pairs\n"
    
    if training_results:
        report += f"""
## Training Performance

- **Best F1 Score:** {training_results.get('best_f1', 'N/A')}
- **Average F1 Score:** {training_results.get('avg_f1', 'N/A')}
- **Models Trained:** {training_results.get('models_trained', 'N/A')}
- **Success Rate:** {training_results.get('success_rate', 'N/A')}%
"""
    
    # Create Prefect artifact
    create_markdown_artifact(
        key="training-report",
        markdown=report,
        description="Model training with preprocessing integration report"
    )
    
    logger.info("Created training report")
    return report


@flow(name="Complete Training with Preprocessing Flow")
def complete_training_flow(
    sectors: Optional[List[str]] = None,
    threshold_percent: float = 0.8,
    min_records: int = 100,
    computation_method: str = 'expanding_window',
    min_periods: int = 30,
    test_window: int = 30,
    arch_lags: int = 5,
    top_pairs: int = 20
) -> Tuple[pd.DataFrame, List[str], List[Dict], List[pd.DataFrame]]:
    """
    Complete training flow that includes preprocessing and model training.
    
    Args:
        sectors: List of sectors to process
        threshold_percent: Percentage threshold for stock selection
        min_records: Minimum records required for stock selection
        computation_method: Method for z-score computation
        min_periods: Minimum periods for expanding window
        test_window: Window size for variance stability testing
        arch_lags: Number of lags for ARCH test
        top_pairs: Number of top pairs to use for training
        
    Returns:
        Tuple of (stable_features, stable_symbols, test_results, pairs_data_list)
    """
    logger = get_run_logger()
    logger.info("Starting Complete Training with Preprocessing Flow")
    
    try:
        # Step 1: Data preprocessing with variance stability testing
        logger.info("Step 1: Running data preprocessing...")
        stable_features, stable_symbols, test_results = data_preprocessing_flow(
            sectors=sectors,
            threshold_percent=threshold_percent,
            min_records=min_records,
            computation_method=computation_method,
            min_periods=min_periods,
            test_window=test_window,
            arch_lags=arch_lags
        )
        
        # Step 2: Prepare training data
        logger.info("Step 2: Preparing training data...")
        pairs_data_list = prepare_training_data_task(stable_features, stable_symbols, top_pairs)
        
        # Step 3: Train models
        logger.info("Step 3: Training GRU models...")
        model, history, trainer = train_gru_models_task(
            pairs_data_list, sectors, use_preprocessing=False
        )
        
        # Step 4: Create training report
        logger.info("Step 4: Creating training report...")
        report = create_training_report_task(pairs_data_list, stable_symbols, test_results)
        
        logger.info("Complete training flow finished successfully!")
        return stable_features, stable_symbols, test_results, pairs_data_list
        
    except Exception as e:
        logger.error(f"Complete training flow failed: {e}")
        raise


@flow(name="Daily Training Flow")
def daily_training_flow():
    """
    Daily training flow that runs automatically.
    Uses default configuration and processes all active sectors.
    """
    logger = get_run_logger()
    logger.info("Starting Daily Training Flow")
    
    try:
        # Get active sectors from config
        symbol_manager = SymbolManager()
        active_sectors = symbol_manager.get_active_sectors()
        
        logger.info(f"Training for active sectors: {active_sectors}")
        
        # Run complete training flow
        stable_features, stable_symbols, test_results, pairs_data_list = complete_training_flow(
            sectors=active_sectors,
            threshold_percent=0.8,
            min_records=100,
            computation_method='expanding_window',
            min_periods=30,
            test_window=30,
            arch_lags=5,
            top_pairs=20
        )
        
        logger.info("Daily training completed successfully")
        return stable_features, stable_symbols, test_results, pairs_data_list
        
    except Exception as e:
        logger.error(f"Daily training flow failed: {e}")
        raise


@flow(name="Sector-Specific Training Flow")
def sector_training_flow(sectors: List[str]):
    """
    Training flow for specific sectors.
    
    Args:
        sectors: List of sectors to train models for
    """
    logger = get_run_logger()
    logger.info(f"Starting Sector-Specific Training Flow for sectors: {sectors}")
    
    try:
        # Run complete training flow for specific sectors
        stable_features, stable_symbols, test_results, pairs_data_list = complete_training_flow(
            sectors=sectors,
            threshold_percent=0.8,
            min_records=100,
            computation_method='expanding_window',
            min_periods=30,
            test_window=30,
            arch_lags=5,
            top_pairs=20
        )
        
        logger.info(f"Sector-specific training completed successfully for {sectors}")
        return stable_features, stable_symbols, test_results, pairs_data_list
        
    except Exception as e:
        logger.error(f"Sector-specific training flow failed: {e}")
        raise


if __name__ == "__main__":
    # For testing
    daily_training_flow() 