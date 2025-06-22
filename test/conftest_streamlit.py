"""
Pytest configuration and fixtures for Streamlit tests.

This file provides common fixtures and configuration for testing the Streamlit UI components.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime
from pytz import timezone

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def streamlit_test_environment():
    """Set up test environment for Streamlit tests."""
    # Set test environment variables
    os.environ['TESTING'] = 'true'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_SERVER_PORT'] = '8501'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = 'localhost'
    
    yield
    
    # Cleanup
    if 'TESTING' in os.environ:
        del os.environ['TESTING']


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit functions for testing."""
    with patch('streamlit.set_page_config') as mock_set_page_config, \
         patch('streamlit.sidebar') as mock_sidebar, \
         patch('streamlit.title') as mock_title, \
         patch('streamlit.subheader') as mock_subheader, \
         patch('streamlit.write') as mock_write, \
         patch('streamlit.columns') as mock_columns, \
         patch('streamlit.metric') as mock_metric, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.selectbox') as mock_selectbox, \
         patch('streamlit.expander') as mock_expander, \
         patch('streamlit.caption') as mock_caption, \
         patch('streamlit.markdown') as mock_markdown:
        
        # Mock columns to return mock column objects
        def mock_columns_impl(*args, **kwargs):
            num_cols = args[0] if args else kwargs.get('num_columns', 1)
            return [Mock() for _ in range(num_cols)]
        
        mock_columns.side_effect = mock_columns_impl
        
        # Mock expander context manager
        mock_expander_context = Mock()
        mock_expander.return_value.__enter__.return_value = mock_expander_context
        mock_expander.return_value.__exit__.return_value = None
        
        yield {
            'set_page_config': mock_set_page_config,
            'sidebar': mock_sidebar,
            'title': mock_title,
            'subheader': mock_subheader,
            'write': mock_write,
            'columns': mock_columns,
            'metric': mock_metric,
            'button': mock_button,
            'selectbox': mock_selectbox,
            'expander': mock_expander,
            'caption': mock_caption,
            'markdown': mock_markdown
        }


@pytest.fixture
def mock_streamlit_autorefresh():
    """Mock Streamlit autorefresh functionality."""
    with patch('streamlit_autorefresh.st_autorefresh') as mock_autorefresh:
        yield mock_autorefresh


@pytest.fixture
def mock_streamlit_option_menu():
    """Mock Streamlit option menu."""
    with patch('streamlit_option_menu.option_menu') as mock_option_menu:
        yield mock_option_menu


@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing."""
    return {
        "total_value": 125432.89,
        "daily_pnl": 1234.56,
        "open_positions": 12,
        "win_rate": 68.0,
        "avg_trade": 342.50,
        "risk_reward": "1:2.5",
        "max_drawdown": 8.5,
        "pending_orders": 3
    }


@pytest.fixture
def sample_market_data():
    """Sample market data for testing."""
    return {
        "indices": {
            "sp500": {"value": 4783.45, "change": 0.8},
            "nasdaq": {"value": 16742.38, "change": 1.2},
            "dow": {"value": 37305.16, "change": 0.5}
        },
        "tech_leaders": {
            "AAPL": {"price": 185.92, "change": 1.5},
            "MSFT": {"price": 374.58, "change": 2.1},
            "GOOGL": {"price": 140.93, "change": 0.9}
        },
        "market_breadth": {
            "advancers": 2345,
            "decliners": 1234,
            "new_highs": 45
        }
    }


@pytest.fixture
def sample_activity_data():
    """Sample activity data for testing."""
    return [
        {"action": "Buy", "symbol": "AAPL", "shares": 100, "price": 185.50, "time": "10:15 AM"},
        {"action": "Sell", "symbol": "MSFT", "shares": 50, "price": 374.20, "time": "10:30 AM"},
        {"action": "Limit", "symbol": "GOOGL", "shares": 75, "price": 140.00, "time": "10:45 AM"}
    ]


@pytest.fixture
def sample_news_data():
    """Sample news data for testing."""
    return [
        {
            "title": "Apple Stock Rises on Strong Earnings",
            "content": "Apple reported strong quarterly earnings...",
            "published_at": "2024-01-15T10:00:00Z",
            "source": "Reuters"
        },
        {
            "title": "Market Volatility Expected This Week",
            "content": "Analysts predict increased volatility...",
            "published_at": "2024-01-15T09:30:00Z",
            "source": "Bloomberg"
        }
    ]


@pytest.fixture
def mock_database_connection():
    """Mock database connection for UI tests."""
    with patch('src.database.database_connectivity.DatabaseConnectivity') as mock_db_class:
        mock_db_instance = Mock()
        mock_db_class.return_value = mock_db_instance
        
        # Mock cursor and common database operations
        mock_cursor = Mock()
        mock_db_instance.cursor.return_value = mock_cursor
        
        # Mock common query results
        mock_cursor.fetchall.return_value = [
            {"symbol": "AAPL", "price": 150.25, "volume": 50000000},
            {"symbol": "MSFT", "price": 374.58, "volume": 30000000}
        ]
        mock_cursor.fetchone.return_value = {"count": 100}
        
        yield {
            'db_class': mock_db_class,
            'db_instance': mock_db_instance,
            'cursor': mock_cursor
        }


@pytest.fixture
def mock_market_hours():
    """Mock market hours functionality."""
    with patch('src.utils.market_hours.is_market_open') as mock_is_open, \
         patch('src.utils.market_hours.get_market_hours') as mock_get_hours:
        
        # Default market open
        mock_is_open.return_value = True
        
        # Default market hours
        mock_get_hours.return_value = {
            "open": "09:30",
            "close": "16:00",
            "timezone": "US/Eastern"
        }
        
        yield {
            'is_market_open': mock_is_open,
            'get_market_hours': mock_get_hours
        }


@pytest.fixture
def mock_time_functions():
    """Mock time-related functions."""
    with patch('datetime.now') as mock_now, \
         patch('src.ui.components.date_display.get_current_cst_formatted') as mock_get_time:
        
        # Mock current time
        mock_now.return_value = datetime(2024, 1, 15, 14, 30, 45, tzinfo=timezone('US/Central'))
        
        # Mock formatted time
        mock_get_time.return_value = "2024-01-15 14:30:45 CST"
        
        yield {
            'now': mock_now,
            'get_current_cst_formatted': mock_get_time
        }


@pytest.fixture
def ui_test_data():
    """Comprehensive test data for UI components."""
    return {
        "user_name": "Test Trader",
        "symbols": ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"],
        "selected_symbol": "AAPL",
        "current_time": "2024-01-15 14:30:45 CST",
        "market_status": "Open",
        "portfolio": {
            "total_value": 125432.89,
            "daily_pnl": 1234.56,
            "open_positions": 12,
            "win_rate": 68.0
        },
        "market_data": {
            "sp500": {"value": 4783.45, "change": 0.8},
            "nasdaq": {"value": 16742.38, "change": 1.2},
            "dow": {"value": 37305.16, "change": 0.5}
        },
        "activities": [
            {"action": "Buy", "symbol": "AAPL", "shares": 100, "price": 185.50, "time": "10:15 AM"},
            {"action": "Sell", "symbol": "MSFT", "shares": 50, "price": 374.20, "time": "10:30 AM"}
        ],
        "news": [
            {
                "title": "Apple Stock Rises on Strong Earnings",
                "content": "Apple reported strong quarterly earnings...",
                "published_at": "2024-01-15T10:00:00Z",
                "source": "Reuters"
            }
        ]
    }


@pytest.fixture
def css_file_content():
    """Sample CSS content for testing."""
    return """
    body {
        background-color: #f0f2f6;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .stApp {
        background-color: #ffffff;
    }
    
    .main-header {
        background-color: #1f2937;
        color: white;
        padding: 1rem;
    }
    
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
    }
    """


@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing."""
    with patch('builtins.open') as mock_open, \
         patch('pathlib.Path') as mock_path:
        
        # Mock CSS file reading
        mock_css_content = """
        body { background-color: #f0f2f6; }
        .stApp { background-color: #ffffff; }
        """
        mock_open.return_value.__enter__.return_value.read.return_value = mock_css_content
        
        yield {
            'open': mock_open,
            'path': mock_path
        }


@pytest.fixture
def streamlit_app_context():
    """Context manager for testing Streamlit app in isolation."""
    class StreamlitAppContext:
        def __init__(self):
            self.mocks = {}
        
        def __enter__(self):
            # Set up all necessary mocks
            self.mocks['streamlit'] = patch('streamlit.set_page_config').start()
            self.mocks['sidebar'] = patch('streamlit.sidebar').start()
            self.mocks['autorefresh'] = patch('streamlit_autorefresh.st_autorefresh').start()
            self.mocks['option_menu'] = patch('streamlit_option_menu.option_menu').start()
            self.mocks['file_open'] = patch('builtins.open').start()
            
            # Mock CSS file reading
            mock_css_content = "body { background-color: #f0f2f6; }"
            self.mocks['file_open'].return_value.__enter__.return_value.read.return_value = mock_css_content
            
            return self.mocks
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            # Stop all patches
            for mock in self.mocks.values():
                patch.stopall()
    
    return StreamlitAppContext() 