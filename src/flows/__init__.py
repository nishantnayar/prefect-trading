"""
Prefect flows for the trading system.

This module contains Prefect flows and tasks for:
- Data preprocessing with variance stability testing
- Model training with MLflow integration
- Performance monitoring and reporting
"""

from .preprocessing_flows import (
    data_preprocessing_flow,
    daily_preprocessing_flow,
    extract_historical_data_task,
    select_stocks_task,
    compute_features_task,
    test_variance_stability_task,
    save_features_task,
    save_variance_results_task,
    create_preprocessing_report_task
)

from .training_flows import (
    complete_training_flow,
    daily_training_flow,
    sector_training_flow,
    prepare_training_data_task,
    train_gru_models_task,
    create_training_report_task
)

__all__ = [
    # Preprocessing flows
    "data_preprocessing_flow",
    "daily_preprocessing_flow",
    "extract_historical_data_task",
    "select_stocks_task",
    "compute_features_task",
    "test_variance_stability_task",
    "save_features_task",
    "save_variance_results_task",
    "create_preprocessing_report_task",
    
    # Training flows
    "complete_training_flow",
    "daily_training_flow",
    "sector_training_flow",
    "prepare_training_data_task",
    "train_gru_models_task",
    "create_training_report_task"
] 