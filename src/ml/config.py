"""
MLflow Configuration Manager for GARCH-GRU Pairs Trading System

This module handles MLflow configuration, experiment setup, and model registry management.
"""

import os
import yaml
import mlflow
from mlflow.tracking import MlflowClient
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLflowConfig:
    """
    MLflow configuration manager for the pairs trading system.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize MLflow configuration.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config_path = config_path or "config/config.yaml"
        self.config = self._load_config()
        # Don't setup MLflow immediately - do it lazily when needed
        self._mlflow_initialized = False
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file with environment variable substitution."""
        try:
            with open(self.config_path, 'r') as file:
                content = file.read()
            
            # Handle environment variable substitution
            content = self._substitute_env_vars(content)
            
            config = yaml.safe_load(content)
            return config
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found. Using defaults.")
            return {}
        except Exception as e:
            logger.error(f"Error parsing configuration file: {e}")
            return {}
    
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
    
    def _setup_mlflow(self):
        """Setup MLflow tracking and registry."""
        if self._mlflow_initialized:
            return
            
        try:
            mlflow_config = self.config.get('mlflow', {})
            
            # Set tracking URI with proper fallback
            tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
            if not tracking_uri:
                tracking_uri = mlflow_config.get('tracking_uri', 'http://localhost:5000')
            
            # Validate tracking URI
            if not tracking_uri or tracking_uri.startswith('${'):
                tracking_uri = 'http://localhost:5000'
                logger.warning(f"Invalid MLFLOW_TRACKING_URI, using default: {tracking_uri}")
            
            mlflow.set_tracking_uri(tracking_uri)
            
            # Set registry URI with proper fallback
            registry_uri = os.getenv('MLFLOW_REGISTRY_URI')
            if not registry_uri:
                registry_uri = mlflow_config.get('registry_uri', tracking_uri)
            
            # Validate registry URI
            if not registry_uri or registry_uri.startswith('${'):
                registry_uri = tracking_uri
                logger.warning(f"Invalid MLFLOW_REGISTRY_URI, using tracking URI: {registry_uri}")
            
            mlflow.set_registry_uri(registry_uri)
            
            # Set experiment name
            experiment_name = os.getenv('MLFLOW_EXPERIMENT_NAME')
            if not experiment_name:
                experiment_name = mlflow_config.get('experiment_name', 'pairs_trading')
            
            mlflow.set_experiment(experiment_name)
            
            self._mlflow_initialized = True
            logger.info(f"MLflow configured - Tracking URI: {tracking_uri}, Registry URI: {registry_uri}")
            logger.info(f"Experiment: {experiment_name}")
            
        except Exception as e:
            logger.error(f"Error setting up MLflow: {e}")
            # Don't raise the exception, just log it
            # This allows the application to continue even if MLflow is not available
    
    def _ensure_mlflow_initialized(self):
        """Ensure MLflow is initialized before use."""
        if not self._mlflow_initialized:
            self._setup_mlflow()
    
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
        self._ensure_mlflow_initialized()
        try:
            return mlflow.get_experiment_by_name(mlflow.get_experiment().name).name
        except Exception as e:
            logger.error(f"Error getting experiment name: {e}")
            return 'pairs_trading'
    
    def create_experiment(self, experiment_name: str) -> str:
        """
        Create a new MLflow experiment.
        
        Args:
            experiment_name: Name of the experiment
            
        Returns:
            Experiment ID
        """
        self._ensure_mlflow_initialized()
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
        self._ensure_mlflow_initialized()
        return MlflowClient()
    
    def list_experiments(self) -> list:
        """List all experiments."""
        self._ensure_mlflow_initialized()
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
        self._ensure_mlflow_initialized()
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
        self._ensure_mlflow_initialized()
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
        self._ensure_mlflow_initialized()
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
        self._ensure_mlflow_initialized()
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
        self._ensure_mlflow_initialized()
        try:
            client = self.get_client()
            client.delete_model_version(name=model_name, version=version)
            logger.info(f"Successfully deleted {model_name} v{version}")
            return True
        except Exception as e:
            logger.error(f"Error deleting {model_name} v{version}: {e}")
            return False


# Global MLflow configuration instance - don't initialize immediately
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


def get_rebaselining_config() -> Dict[str, Any]:
    """Get rebaselining configuration."""
    return mlflow_config.get_rebaselining_config()


def get_performance_thresholds() -> Dict[str, float]:
    """Get performance thresholds for model evaluation."""
    return mlflow_config.get_performance_thresholds() 