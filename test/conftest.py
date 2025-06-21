import pytest
import os
import sys
from unittest.mock import Mock, patch
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment variables."""
    # Set test environment
    os.environ['TESTING'] = 'true'
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_PORT'] = '5432'
    os.environ['DB_NAME'] = 'test_trading_db'
    os.environ['DB_USER'] = 'test_user'
    os.environ['DB_PASSWORD'] = 'test_password'
    
    yield
    
    # Cleanup
    if 'TESTING' in os.environ:
        del os.environ['TESTING']

@pytest.fixture
def mock_yahoo_api():
    """Mock Yahoo Finance API responses."""
    with patch('requests.get') as mock_get:
        # Setup default mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "chart": {
                "result": [{
                    "meta": {
                        "symbol": "AAPL",
                        "regularMarketPrice": 150.25,
                        "regularMarketVolume": 50000000
                    },
                    "timestamp": [1642248000],
                    "indicators": {
                        "quote": [{
                            "open": [150.0],
                            "high": [152.0],
                            "low": [149.0],
                            "close": [150.25],
                            "volume": [50000000]
                        }]
                    }
                }],
                "error": None
            }
        }
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_alpaca_api():
    """Mock Alpaca API responses."""
    with patch('alpaca.data.historical.StockHistoricalDataClient') as mock_client:
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.get_bars.return_value = {
            "AAPL": [{
                "t": "2024-01-15T09:30:00Z",
                "o": 150.0,
                "h": 152.0,
                "l": 149.0,
                "c": 150.25,
                "v": 50000000
            }]
        }
        yield mock_client

@pytest.fixture
def mock_database():
    """Mock database connectivity."""
    with patch('psycopg2.connect') as mock_connect:
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "AAPL"}]
        mock_connect.return_value = mock_connection
        yield mock_connect

@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing."""
    return {
        "symbol": "AAPL",
        "price": 150.25,
        "volume": 50000000,
        "timestamp": "2024-01-15T09:30:00Z"
    }

@pytest.fixture
def sample_news_data():
    """Sample news data for testing."""
    return {
        "title": "Apple Stock Rises on Strong Earnings",
        "content": "Apple reported strong quarterly earnings...",
        "published_at": "2024-01-15T10:00:00Z",
        "source": "Reuters"
    } 