#!/usr/bin/env python3
"""
MLflow Configuration Manager for GARCH-GRU Pairs Trading System

This module provides a centralized interface for MLflow operations including:
- Experiment tracking and management
- Model logging and registration
- Configuration management
- Integration with the trading system
"""

import os
import yaml
import mlflow
import mlflow.pytorch
from mlflow.tracking import MlflowClient
from mlflow.models import infer_signature
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLflowManager:
    """
    Centralized MLflow management for the pairs trading system.
    
    Handles experiment tracking, model logging, and configuration management
    for the GARCH-GRU pairs trading strategy.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize MLflow manager with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.client = None
        self._setup_mlflow()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file with environment variable substitution."""
        try:
            with open(self.config_path, 'r') as file:
                content = file.read()
            
            # Handle environment variable substitution
            content = self._substitute_env_vars(content)
            
            config = yaml.safe_load(content)
            return config.get('mlflow', {})
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found. Using defaults.")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _substitute_env_vars(self, content: str) -> str:
        """Substitute environment variables in YAML content."""
        import re
        import os
        
        def replace_env_var(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) else ""
            
            # Check if environment variable exists
            env_value = os.environ.get(var_name)
            if env_value is not None:
                return env_value
            else:
                return default_value
        
        # Pattern to match ${VAR:-default} or ${VAR}
        pattern = r'\$\{([^:}]+)(?::-([^}]*))?\}'
        return re.sub(pattern, replace_env_var, content)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default MLflow configuration."""
        return {
            'tracking_uri': 'http://localhost:5000',
            'registry_uri': 'http://localhost:5000',
            'experiment_name': 'pairs_trading',
            'backend_store_uri': 'postgresql://postgres:nishant@localhost/mlflow_db',
            'artifact_root': 'file:./mlruns'
        }
    
    def _setup_mlflow(self):
        """Setup MLflow tracking and client with robust retry logic."""
        try:
            # Set tracking URI
            tracking_uri = self.config.get('tracking_uri', 'http://localhost:5000')
            mlflow.set_tracking_uri(tracking_uri)
            # Set registry URI
            registry_uri = self.config.get('registry_uri', tracking_uri)
            mlflow.set_registry_uri(registry_uri)
            # Initialize client
            self.client = MlflowClient()
            # Set default experiment with robust retry logic
            experiment_name = self.config.get('experiment_name', 'pairs_trading')
            max_retries = 5
            backoff = 0.5
            for attempt in range(1, max_retries + 1):
                try:
                    self.set_experiment(experiment_name, retrying=True)
                    break
                except Exception as exp_error:
                    logger.warning(f"Attempt {attempt}/{max_retries} to set experiment {experiment_name} failed: {exp_error}")
                    if attempt < max_retries:
                        time.sleep(backoff)
                        backoff *= 2
                    else:
                        logger.error(f"All {max_retries} attempts failed to create experiment '{experiment_name}'. Check MLflow server status and permissions.")
                        logger.error(f"Last error: {exp_error}")
                        # Don't create fallback experiment - let the user fix the issue
                        raise Exception(f"Failed to create MLflow experiment '{experiment_name}' after {max_retries} attempts. Please check MLflow server status.")
            logger.info(f"MLflow setup complete. Tracking URI: {tracking_uri}")
        except Exception as e:
            logger.error(f"Error setting up MLflow: {e}")
            # Don't raise - allow the manager to be created even if setup fails
            # The experiment will be set when actually needed

    def set_experiment(self, experiment_name: str, retrying: bool = False) -> str:
        """
        Set or create experiment, with optional retrying flag to avoid nested retries.
        """
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
                logger.info(f"Created new experiment: {experiment_name}")
            else:
                experiment_id = experiment.experiment_id
                if hasattr(experiment, 'lifecycle_stage') and experiment.lifecycle_stage == "deleted":
                    logger.warning(f"Experiment {experiment_name} was deleted. Attempting to restore it.")
                    try:
                        # Try to restore the deleted experiment instead of recreating
                        if self.client:
                            self.client.restore_experiment(experiment_id)
                            logger.info(f"Restored deleted experiment: {experiment_name}")
                        else:
                            # If client is not available, try to create with a different name
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            new_name = f"{experiment_name}_restored_{timestamp}"
                            experiment_id = mlflow.create_experiment(new_name)
                            experiment_name = new_name
                            logger.info(f"Created restored experiment with new name: {new_name}")
                    except Exception as restore_error:
                        logger.warning(f"Could not restore experiment: {restore_error}")
                        # Try to create with a different name as fallback
                        try:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            new_name = f"{experiment_name}_restored_{timestamp}"
                            experiment_id = mlflow.create_experiment(new_name)
                            experiment_name = new_name
                            logger.info(f"Created experiment with new name: {new_name}")
                        except Exception as create_error:
                            if not retrying:
                                raise create_error
                            logger.error(f"Failed to create experiment '{experiment_name}' after restoration attempt: {create_error}")
                            raise Exception(f"Cannot create experiment '{experiment_name}'. Please check MLflow server status and permissions.")
                else:
                    logger.info(f"Using existing experiment: {experiment_name}")
            mlflow.set_experiment(experiment_name)
            return experiment_id
        except Exception as e:
            logger.error(f"Error setting experiment {experiment_name}: {e}")
            if not retrying:
                # Only retry if not already in a retry loop
                raise
            # Don't create fallback experiment - let the user fix the issue
            logger.error(f"Failed to set experiment '{experiment_name}'. Please check MLflow server status and permissions.")
            raise Exception(f"Cannot set experiment '{experiment_name}'. Please check MLflow server status and permissions.")
    
    def handle_deleted_experiment_issue(self, experiment_name: str) -> str:
        """
        Handle the specific case of deleted experiments by creating a new one with a timestamp.
        This is a fallback method for when restoration fails.
        
        Args:
            experiment_name: The original experiment name that was deleted
            
        Returns:
            New experiment ID
        """
        try:
            # Create a new experiment with timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_experiment_name = f"{experiment_name}_restored_{timestamp}"
            
            logger.info(f"Creating new experiment '{new_experiment_name}' to replace deleted '{experiment_name}'")
            experiment_id = mlflow.create_experiment(new_experiment_name)
            mlflow.set_experiment(new_experiment_name)
            
            logger.info(f"Successfully created replacement experiment: {new_experiment_name}")
            return experiment_id
            
        except Exception as e:
            logger.error(f"Failed to create replacement experiment: {e}")
            raise Exception(f"Cannot create replacement experiment for '{experiment_name}'. Error: {e}")
    
    def create_sector_experiment(self, sector: str) -> str:
        """
        Create sector-specific experiment.
        
        Args:
            sector: Sector name (e.g., 'technology', 'healthcare')
            
        Returns:
            Experiment ID
        """
        experiment_name = f"pairs_trading/{sector}"
        return self.set_experiment(experiment_name)
    
    def start_run(self, run_name: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> mlflow.ActiveRun:
        """
        Start a new MLflow run.
        
        Args:
            run_name: Optional name for the run
            tags: Optional tags for the run
            
        Returns:
            Active MLflow run
        """
        try:
            run = mlflow.start_run(run_name=run_name, tags=tags)
            logger.info(f"Started MLflow run: {run.info.run_id}")
            return run
        except Exception as e:
            logger.error(f"Error starting run: {e}")
            raise
    
    def log_parameters(self, params: Dict[str, Any]):
        """
        Log parameters to current run.
        
        Args:
            params: Dictionary of parameters to log
        """
        try:
            mlflow.log_params(params)
            logger.info(f"Logged {len(params)} parameters")
        except Exception as e:
            logger.error(f"Error logging parameters: {e}")
            raise
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """
        Log metrics to current run.
        
        Args:
            metrics: Dictionary of metrics to log
            step: Optional step number for the metrics
        """
        try:
            mlflow.log_metrics(metrics, step=step)
            logger.info(f"Logged {len(metrics)} metrics")
        except Exception as e:
            logger.error(f"Error logging metrics: {e}")
            raise
    
    def log_model(self, model, model_name: str, model_type: str = "pytorch"):
        """
        Log model to current run.
        
        Args:
            model: The model to log
            model_name: Name for the model
            model_type: Type of model ('pytorch', 'sklearn', etc.)
        """
        try:
            if model_type == "pytorch":
                mlflow.pytorch.log_model(model, model_name)
            else:
                mlflow.log_model(model, model_name)
            
            logger.info(f"Logged {model_type} model: {model_name}")
        except Exception as e:
            logger.error(f"Error logging model: {e}")
            raise
    
    def log_artifacts(self, local_path: str, artifact_path: Optional[str] = None):
        """
        Log artifacts to current run.
        
        Args:
            local_path: Path to the artifact file/directory
            artifact_path: Optional path within the run's artifact directory
        """
        try:
            mlflow.log_artifact(local_path, artifact_path)
            logger.info(f"Logged artifact: {local_path}")
        except Exception as e:
            logger.error(f"Error logging artifact: {e}")
            raise
    
    def log_dict(self, data: Dict[str, Any], artifact_file: str):
        """
        Log dictionary as JSON artifact.
        
        Args:
            data: Dictionary to log
            artifact_file: Name of the artifact file
        """
        try:
            mlflow.log_dict(data, artifact_file)
            logger.info(f"Logged dictionary as {artifact_file}")
        except Exception as e:
            logger.error(f"Error logging dictionary: {e}")
            raise
    
    def register_model(self, model_uri: str, model_name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """
        Register model in the model registry.
        
        Args:
            model_uri: URI of the model to register
            model_name: Name for the registered model
            tags: Optional tags for the model
            
        Returns:
            Model version
        """
        try:
            model_details = mlflow.register_model(
                model_uri=model_uri,
                name=model_name,
                tags=tags
            )
            logger.info(f"Registered model {model_name} version {model_details.version}")
            return model_details.version
        except Exception as e:
            logger.error(f"Error registering model: {e}")
            raise
    
    def get_latest_model(self, model_name: str, stage: str = "Production") -> Optional[str]:
        """
        Get the latest model version for a given stage.
        
        Args:
            model_name: Name of the model
            stage: Stage of the model (Production, Staging, Archived)
            
        Returns:
            Model URI or None if not found
        """
        try:
            model_versions = self.client.get_latest_versions(model_name, stages=[stage])
            if model_versions:
                return f"models:/{model_name}/{stage}"
            return None
        except Exception as e:
            logger.error(f"Error getting latest model: {e}")
            return None
    
    def load_model(self, model_uri: str):
        """
        Load a model from MLflow.
        
        Args:
            model_uri: URI of the model to load
            
        Returns:
            Loaded model
        """
        try:
            model = mlflow.pytorch.load_model(model_uri)
            logger.info(f"Loaded model from {model_uri}")
            return model
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def transition_model_stage(self, model_name: str, version: str, stage: str):
        """
        Transition model to a different stage.
        
        Args:
            model_name: Name of the model
            version: Model version
            stage: Target stage (Production, Staging, Archived)
        """
        try:
            self.client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage
            )
            logger.info(f"Transitioned {model_name} version {version} to {stage}")
        except Exception as e:
            logger.error(f"Error transitioning model stage: {e}")
            raise
    
    def get_experiment_runs(self, experiment_name: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Get runs from an experiment.
        
        Args:
            experiment_name: Name of the experiment
            max_results: Maximum number of results to return
            
        Returns:
            List of run information
        """
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                return []
            
            runs = self.client.search_runs(
                experiment_ids=[experiment.experiment_id],
                max_results=max_results
            )
            
            run_info = []
            for run in runs:
                run_info.append({
                    'run_id': run.info.run_id,
                    'status': run.info.status,
                    'start_time': run.info.start_time,
                    'end_time': run.info.end_time,
                    'metrics': run.data.metrics,
                    'params': run.data.params,
                    'tags': run.data.tags
                })
            
            return run_info
        except Exception as e:
            logger.error(f"Error getting experiment runs: {e}")
            return []
    
    def cleanup_old_runs(self, experiment_name: str, days_old: int = 30):
        """
        Clean up old runs from an experiment.
        
        Args:
            experiment_name: Name of the experiment
            days_old: Delete runs older than this many days
        """
        try:
            # This is a placeholder for cleanup functionality
            # MLflow doesn't have built-in cleanup, but we can implement it
            logger.info(f"Cleanup functionality for {experiment_name} (older than {days_old} days)")
            # TODO: Implement cleanup logic
        except Exception as e:
            logger.error(f"Error cleaning up runs: {e}")
    
    def get_model_performance_history(self, model_name: str) -> List[Dict[str, Any]]:
        """
        Get performance history for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            List of performance records
        """
        try:
            model_versions = self.client.search_model_versions(f"name='{model_name}'")
            
            performance_history = []
            for version in model_versions:
                if version.run_id:
                    run = self.client.get_run(version.run_id)
                    performance_history.append({
                        'version': version.version,
                        'stage': version.current_stage,
                        'creation_timestamp': version.creation_timestamp,
                        'last_updated_timestamp': version.last_updated_timestamp,
                        'metrics': run.data.metrics,
                        'run_id': version.run_id
                    })
            
            return performance_history
        except Exception as e:
            logger.error(f"Error getting model performance history: {e}")
            return []


# Convenience functions for common operations
def get_mlflow_manager(config_path: str = "config/config.yaml") -> MLflowManager:
    """
    Get MLflow manager instance.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        MLflowManager instance
    """
    return MLflowManager(config_path)


def log_training_run(model, metrics: Dict[str, float], params: Dict[str, Any], 
                    model_name: str, sector: str = "technology", 
                    run_name: Optional[str] = None) -> str:
    """
    Convenience function to log a complete training run.
    
    Args:
        model: Trained model
        metrics: Training metrics
        params: Training parameters
        model_name: Name for the model
        sector: Sector name
        run_name: Optional run name
        
    Returns:
        Run ID
    """
    manager = get_mlflow_manager()
    
    # Set sector experiment
    manager.create_sector_experiment(sector)
    
    # Start run
    with manager.start_run(run_name=run_name) as run:
        # Log parameters
        manager.log_parameters(params)
        
        # Log metrics
        manager.log_metrics(metrics)
        
        # Log model
        manager.log_model(model, model_name)
        
        # Log additional info
        manager.log_dict({
            'sector': sector,
            'training_date': datetime.now().isoformat(),
            'model_type': 'gru_garch_hybrid'
        }, 'training_info.json')
        
        return run.info.run_id


if __name__ == "__main__":
    # Test the MLflow manager
    try:
        manager = MLflowManager()
        print("[OK] MLflow manager initialized successfully")
        
        # Test experiment creation
        experiment_id = manager.create_sector_experiment("technology")
        print(f"[OK] Created experiment: {experiment_id}")
        
        # Test run creation
        with manager.start_run(run_name="test_run") as run:
            manager.log_parameters({"test_param": "test_value"})
            manager.log_metrics({"test_metric": 0.95})
            print(f"[OK] Test run completed: {run.info.run_id}")
        
        print("[OK] All tests passed!")
        
    except Exception as e:
        print(f"[FAIL] Test failed: {e}") 