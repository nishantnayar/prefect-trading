"""
Test configuration and fixtures for the trading system.
"""

import os
import sys
from pathlib import Path

# Add src to Python path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Set environment variable to suppress Jupyter deprecation warning
os.environ["JUPYTER_PLATFORM_DIRS"] = "1"

# Import pytest for fixtures
import pytest
from unittest.mock import Mock

# Import shared fixtures
from test.fixtures.database_fixtures import (
    mock_database_connection,
    mock_connection_pool,
    sample_symbol_data,
    sample_market_data,
    sample_portfolio_data,
    mock_database_session,
    database_error_scenarios
)

from test.fixtures.mock_fixtures import (
    mock_streamlit,
    mock_alpaca_api,
    mock_yahoo_api,
    mock_mlflow,
    mock_requests,
    mock_pandas,
    mock_numpy,
    mock_torch,
    mock_environment_variables,
    mock_config
)

# Re-export fixtures for easy access
__all__ = [
    'mock_database_connection',
    'mock_connection_pool', 
    'sample_symbol_data',
    'sample_market_data',
    'sample_portfolio_data',
    'mock_database_session',
    'database_error_scenarios',
    'mock_streamlit',
    'mock_alpaca_api',
    'mock_yahoo_api',
    'mock_mlflow',
    'mock_requests',
    'mock_pandas',
    'mock_numpy',
    'mock_torch',
    'mock_environment_variables',
    'mock_config'
] 