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

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit functions for UI testing."""
    mock_st = {
        'title': Mock(),
        'subheader': Mock(),
        'metric': Mock(),
        'dataframe': Mock(),
        'info': Mock(),
        'warning': Mock(),
        'success': Mock(),
        'error': Mock(),
        'caption': Mock(),
        'divider': Mock(),
        'button': Mock(return_value=False),
        'write': Mock(),
        'plotly_chart': Mock(),
        'columns': Mock(),
        'rerun': Mock(),
    }
    
    # Configure columns mock to return context managers
    def create_context_mock():
        mock = Mock()
        mock.__enter__ = Mock(return_value=mock)
        mock.__exit__ = Mock(return_value=None)
        return mock
    
    def columns_side_effect(num_cols):
        if isinstance(num_cols, list):
            return [create_context_mock() for _ in range(len(num_cols))]
        else:
            return [create_context_mock() for _ in range(num_cols)]
    
    mock_st['columns'].side_effect = columns_side_effect
    
    return mock_st 