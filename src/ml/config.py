"""
MLflow Configuration Manager for GARCH-GRU Pairs Trading System

This module handles MLflow configuration, experiment setup, and model registry management.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import mlflow
from mlflow.tracking import MlflowClient
from loguru import logger


class MLflowConfig:
    """Configuration manager for MLflow integration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize MLflow configuration.
        
        Args:
            config_path: Path to configuration file. If None, uses default config/config.yaml
        """
        self.config_path = config_path or "config/config.yaml"
        self.config = self._load_config()
        self._setup_mlflow()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise
    
    def _setup_mlflow(self):
        """Setup MLflow tracking and registry."""
        mlflow_config = self.config.get('mlflow', {})
        
        # Set tracking URI
        tracking_uri = os.getenv('MLFLOW_TRACKING_URI', mlflow_config.get('tracking_uri', 'http://localhost:5000'))
        mlflow.set_tracking_uri(tracking_uri)
        
        # Set registry URI
        registry_uri = os.getenv('MLFLOW_REGISTRY_URI', mlflow_config.get('registry_uri', 'http://localhost:5000'))
        mlflow.set_registry_uri(registry_uri)
        
        # Set experiment name
        experiment_name = os.getenv('MLFLOW_EXPERIMENT_NAME', mlflow_config.get('experiment_name', 'pairs_trading'))
        mlflow.set_experiment(experiment_name)
        
        logger.info(f"MLflow configured - Tracking URI: {tracking_uri}, Registry URI: {registry_uri}")
        logger.info(f"Experiment: {experiment_name}")
    
    def get_model_registry_config(self) -> Dict[str, Any]:
        """Get model registry configuration."""
        return self.config.get('model_registry', {})
    
    def get_rebaselining_config(self) -> Dict[str, Any]:
        """Get rebaselining configuration."""
        return self.config.get('rebaselining', {})
    
    def get_performance_thresholds(self) -> Dict[str, float]:
        """Get performance thresholds for model evaluation."""
        return self.config.get('performance_thresholds', {})
    
    def get_experiment_name(self) -> str:
        """Get current experiment name."""
        return mlflow.get_experiment_by_name(mlflow.get_experiment().name).name
    
    def create_experiment(self, experiment_name: str) -> str:
        """
        Create a new MLflow experiment.
        
        Args:
            experiment_name: Name of the experiment
            
        Returns:
            Experiment ID
        """
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
                logger.info(f"Created new experiment: {experiment_name} (ID: {experiment_id})")
            else:
                experiment_id = experiment.experiment_id
                logger.info(f"Using existing experiment: {experiment_name} (ID: {experiment_id})")
            
            return experiment_id
        except Exception as e:
            logger.error(f"Error creating experiment {experiment_name}: {e}")
            raise
    
    def get_client(self) -> MlflowClient:
        """Get MLflow client instance."""
        return MlflowClient()
    
    def list_experiments(self) -> list:
        """List all experiments."""
        try:
            client = self.get_client()
            experiments = client.list_experiments()
            return [exp for exp in experiments]
        except Exception as e:
            logger.error(f"Error listing experiments: {e}")
            return []
    
    def list_models(self, filter_string: Optional[str] = None) -> list:
        """
        List registered models.
        
        Args:
            filter_string: Optional filter string for model names
            
        Returns:
            List of registered models
        """
        try:
            client = self.get_client()
            models = client.list_registered_models(filter_string=filter_string)
            return [model for model in models]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def get_model_versions(self, model_name: str) -> list:
        """
        Get all versions of a registered model.
        
        Args:
            model_name: Name of the registered model
            
        Returns:
            List of model versions
        """
        try:
            client = self.get_client()
            versions = client.search_model_versions(f"name='{model_name}'")
            return [version for version in versions]
        except Exception as e:
            logger.error(f"Error getting model versions for {model_name}: {e}")
            return []
    
    def get_latest_model_version(self, model_name: str, stage: str = "Production") -> Optional[Any]:
        """
        Get the latest version of a model in a specific stage.
        
        Args:
            model_name: Name of the registered model
            stage: Model stage (Production, Staging, Archived)
            
        Returns:
            Latest model version or None if not found
        """
        try:
            client = self.get_client()
            latest_version = client.get_latest_versions(model_name, stages=[stage])
            return latest_version[0] if latest_version else None
        except Exception as e:
            logger.error(f"Error getting latest model version for {model_name} in {stage}: {e}")
            return None
    
    def transition_model_stage(self, model_name: str, version: int, stage: str) -> bool:
        """
        Transition a model version to a new stage.
        
        Args:
            model_name: Name of the registered model
            version: Model version number
            stage: Target stage (Production, Staging, Archived)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = self.get_client()
            client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage
            )
            logger.info(f"Successfully transitioned {model_name} v{version} to {stage}")
            return True
        except Exception as e:
            logger.error(f"Error transitioning {model_name} v{version} to {stage}: {e}")
            return False
    
    def delete_model_version(self, model_name: str, version: int) -> bool:
        """
        Delete a specific model version.
        
        Args:
            model_name: Name of the registered model
            version: Model version number
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = self.get_client()
            client.delete_model_version(name=model_name, version=version)
            logger.info(f"Successfully deleted {model_name} v{version}")
            return True
        except Exception as e:
            logger.error(f"Error deleting {model_name} v{version}: {e}")
            return False


# Global MLflow configuration instance
mlflow_config = MLflowConfig()


def get_mlflow_config() -> MLflowConfig:
    """Get the global MLflow configuration instance."""
    return mlflow_config


def setup_mlflow_experiment(experiment_name: str) -> str:
    """
    Setup MLflow experiment for pairs trading.
    
    Args:
        experiment_name: Name of the experiment
        
    Returns:
        Experiment ID
    """
    return mlflow_config.create_experiment(experiment_name)


def get_model_registry_config() -> Dict[str, Any]:
    """Get model registry configuration."""
    return mlflow_config.get_model_registry_config()


def get_performance_thresholds() -> Dict[str, float]:
    """Get performance thresholds for model evaluation."""
    return mlflow_config.get_performance_thresholds() 