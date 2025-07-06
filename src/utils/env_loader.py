"""
Environment Variable Loader
==========================

A simple, robust environment variable loader using python-dotenv.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_env_file(env_file_path: str = None) -> bool:
    """
    Load environment variables from a .env file.
    
    Args:
        env_file_path: Path to the .env file. If None, looks for config/.env
        
    Returns:
        bool: True if file was loaded successfully, False otherwise
    """
    try:
        if env_file_path is None:
            # Look for .env file in config directory relative to project root
            project_root = Path(__file__).parent.parent.parent
            env_file_path = project_root / "config" / ".env"
        
        env_file = Path(env_file_path)
        
        if not env_file.exists():
            return False
            
        # Use python-dotenv to load the environment file
        load_dotenv(env_file)
        return True
        
    except Exception as e:
        # Silently fail to prevent issues
        return False


def get_env(key: str, default: str = None) -> str:
    """
    Get an environment variable with a default value.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        str: Environment variable value or default
    """
    return os.getenv(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """
    Get a boolean environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        bool: Boolean value of environment variable
    """
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')


def get_env_int(key: str, default: int = 0) -> int:
    """
    Get an integer environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        int: Integer value of environment variable
    """
    try:
        return int(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default 