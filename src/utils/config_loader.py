"""
Configuration Loader Utility

This module provides a robust way to load configuration files that works
in both local development and Prefect deployment environments.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def find_config_file(config_name: str = "config.yaml") -> Optional[Path]:
    """
    Find the configuration file by searching multiple possible locations.
    
    Args:
        config_name: Name of the config file (default: config.yaml)
        
    Returns:
        Path to the config file if found, None otherwise
    """
    # List of possible config file locations in order of preference
    possible_paths = [
        # Relative to current working directory
        Path.cwd() / "config" / config_name,
        Path.cwd() / config_name,
        
        # Relative to project root (assuming we're in src/ or a subdirectory)
        Path.cwd().parent / "config" / config_name,
        Path.cwd().parent.parent / "config" / config_name,
        
        # Relative to this file
        Path(__file__).parent.parent.parent / "config" / config_name,
        
        # Environment variable
        Path(os.environ.get("CONFIG_PATH", "")) / config_name if os.environ.get("CONFIG_PATH") else None,
        
        # Common deployment paths
        Path("/app/config") / config_name,
        Path("/opt/app/config") / config_name,
    ]
    
    # Filter out None values
    possible_paths = [p for p in possible_paths if p is not None]
    
    # Try each path
    for config_path in possible_paths:
        if config_path.exists():
            logger.info(f"Found config file at: {config_path}")
            return config_path
    
    logger.warning(f"Config file '{config_name}' not found in any of the expected locations")
    return None


def load_config(config_name: str = "config.yaml", default_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file with fallback to defaults.
    
    Args:
        config_name: Name of the config file
        default_config: Default configuration to use if file not found
        
    Returns:
        Configuration dictionary
    """
    config_path = find_config_file(config_name)
    
    if config_path is None:
        logger.warning(f"Using default configuration (config file '{config_name}' not found)")
        return default_config or {}
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            logger.info(f"Successfully loaded configuration from {config_path}")
            return config
    except Exception as e:
        logger.error(f"Error loading configuration from {config_path}: {e}")
        logger.warning("Using default configuration due to load error")
        return default_config or {}


def get_config_section(section_name: str, config_name: str = "config.yaml", default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Load a specific section from the configuration file.
    
    Args:
        section_name: Name of the section to load
        config_name: Name of the config file
        default: Default value for the section if not found
        
    Returns:
        Configuration section dictionary
    """
    config = load_config(config_name)
    section = config.get(section_name, default or {})
    logger.debug(f"Loaded config section '{section_name}'")
    return section


# Convenience functions for common config sections
def get_variance_stability_config() -> Dict[str, Any]:
    """Get variance stability configuration section."""
    return get_config_section("variance_stability", default={
        "arch_test_pvalue_threshold": 0.0,
        "rolling_std_cv_threshold": 2.0,
        "ljung_box_pvalue_threshold": 0.001,
        "test_window": 30,
        "arch_lags": 5,
        "ljung_box_lags": 10
    })


def get_sectors_config() -> Dict[str, Any]:
    """Get sectors configuration section."""
    return get_config_section("sectors", default={
        "active": ["Technology"],
        "available": ["Technology", "Healthcare", "Financial Services"]
    })


def get_mlflow_config() -> Dict[str, Any]:
    """Get MLflow configuration section."""
    return get_config_section("mlflow", default={
        "tracking_uri": "http://localhost:5000",
        "registry_uri": "http://localhost:5000",
        "experiment_name": "pairs_trading",
        "artifact_root": "file:./mlruns"
    })


def get_websocket_config() -> Dict[str, Any]:
    """Get WebSocket configuration section."""
    return get_config_section("websocket", default={
        "mode": "alpaca",
        "symbols": ["AAPL"]
    }) 