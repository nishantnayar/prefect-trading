#!/usr/bin/env python3
"""
Script to fix deleted MLflow experiment issues.

This script handles the case where an MLflow experiment has been deleted
but the system is trying to use it. It will either restore the experiment
or create a new one with a different name.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import mlflow
from mlflow.tracking import MlflowClient
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_deleted_experiment(experiment_name: str):
    """
    Fix a deleted experiment by either restoring it or creating a new one.
    
    Args:
        experiment_name: The name of the deleted experiment
    """
    try:
        # Set up MLflow client
        client = MlflowClient()
        
        # Check if experiment exists
        experiment = mlflow.get_experiment_by_name(experiment_name)
        
        if experiment is None:
            logger.info(f"Experiment '{experiment_name}' does not exist. Creating new experiment.")
            experiment_id = mlflow.create_experiment(experiment_name)
            mlflow.set_experiment(experiment_name)
            logger.info(f"Created new experiment: {experiment_name} (ID: {experiment_id})")
            return experiment_id
            
        elif hasattr(experiment, 'lifecycle_stage') and experiment.lifecycle_stage == "deleted":
            logger.info(f"Experiment '{experiment_name}' was deleted. Attempting to restore...")
            
            try:
                # Try to restore the experiment
                client.restore_experiment(experiment.experiment_id)
                mlflow.set_experiment(experiment_name)
                logger.info(f"Successfully restored experiment: {experiment_name}")
                return experiment.experiment_id
                
            except Exception as restore_error:
                logger.warning(f"Could not restore experiment: {restore_error}")
                logger.info("Creating new experiment with timestamp...")
                
                # Create new experiment with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"{experiment_name}_restored_{timestamp}"
                
                experiment_id = mlflow.create_experiment(new_name)
                mlflow.set_experiment(new_name)
                logger.info(f"Created new experiment: {new_name} (ID: {experiment_id})")
                return experiment_id
        else:
            logger.info(f"Experiment '{experiment_name}' exists and is active.")
            mlflow.set_experiment(experiment_name)
            return experiment.experiment_id
            
    except Exception as e:
        logger.error(f"Error fixing experiment '{experiment_name}': {e}")
        raise


def main():
    """Main function to fix the specific deleted experiment."""
    # The specific experiment that's causing the issue
    experiment_name = "pairs_trading/technology_sector/gru_training"
    
    logger.info(f"Attempting to fix deleted experiment: {experiment_name}")
    
    try:
        experiment_id = fix_deleted_experiment(experiment_name)
        logger.info(f"Successfully fixed experiment. Experiment ID: {experiment_id}")
        print(f"✅ Experiment fixed successfully! Experiment ID: {experiment_id}")
        
    except Exception as e:
        logger.error(f"Failed to fix experiment: {e}")
        print(f"❌ Failed to fix experiment: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 