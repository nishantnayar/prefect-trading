"""
Environment Variable Loader
==========================

A simple, robust environment variable loader using python-dotenv.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Don't import decouple at module level to avoid stack overflow
# We'll import it only when needed in the function
DECOUPLE_AVAILABLE = None  # Will be set to True/False when first needed


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


def load_env_file_with_decouple(env_file_path: str = None) -> bool:
    """
    Load environment variables using decouple with explicit path to avoid stack overflow.
    
    Args:
        env_file_path: Path to the .env file. If None, looks for config/.env
        
    Returns:
        bool: True if file was loaded successfully, False otherwise
    """
    global DECOUPLE_AVAILABLE
    
    # Try to import decouple only when needed
    if DECOUPLE_AVAILABLE is None:
        try:
            from decouple import Config, RepositoryEnv
            DECOUPLE_AVAILABLE = True
        except ImportError:
            DECOUPLE_AVAILABLE = False
    
    if not DECOUPLE_AVAILABLE:
        # Fallback to python-dotenv if decouple is not available
        return load_env_file(env_file_path)
    
    try:
        if env_file_path is None:
            # Look for .env file in config directory relative to project root
            project_root = Path(__file__).parent.parent.parent
            env_file_path = project_root / "config" / ".env"
        
        env_file = Path(env_file_path)
        
        if not env_file.exists():
            return False
            
        # Use decouple with explicit path to avoid stack overflow
        from decouple import Config, RepositoryEnv
        config = Config(repository=RepositoryEnv(str(env_file)))
        
        # Load all variables from the .env file into os.environ
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Use decouple's config to get the value (handles quotes, etc.)
                    try:
                        env_value = config(key, default=value)
                        os.environ[key] = env_value
                    except Exception:
                        # Fallback to raw value if decouple fails
                        os.environ[key] = value
        
        return True
        
    except Exception as e:
        # Fallback to python-dotenv if decouple fails
        return load_env_file(env_file_path)


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