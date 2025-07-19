"""
Shared Database Fixtures
=======================

Common database fixtures and utilities for testing.
"""

import pytest
from unittest.mock import Mock, MagicMock
from contextlib import contextmanager


@pytest.fixture
def mock_database_connection():
    """Mock database connection for testing."""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


@pytest.fixture
def mock_connection_pool():
    """Mock connection pool for testing."""
    mock_pool = Mock()
    mock_connection = Mock()
    mock_cursor = Mock()
    mock_connection.cursor.return_value = mock_cursor
    
    mock_pool.getconn.return_value = mock_connection
    return mock_pool, mock_connection, mock_cursor


@pytest.fixture
def sample_symbol_data():
    """Sample symbol data for testing."""
    return {
        'symbol': 'AAPL',
        'name': 'Apple Inc.',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'market_cap': 2500000000000,
        'pe_ratio': 25.5,
        'dividend_yield': 0.5,
        'beta': 1.2
    }


@pytest.fixture
def sample_market_data():
    """Sample market data for testing."""
    return {
        'symbol': 'AAPL',
        'timestamp': '2024-01-01T00:00:00Z',
        'open': 149.50,
        'high': 151.00,
        'low': 149.00,
        'close': 150.25,
        'volume': 50000000,
        'vwap': 150.10
    }


@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing."""
    return {
        'portfolio_id': 'test_portfolio_001',
        'name': 'Test Portfolio',
        'cash': 10000.00,
        'total_value': 50000.00,
        'positions': [
            {'symbol': 'AAPL', 'quantity': 100, 'avg_price': 150.00},
            {'symbol': 'GOOGL', 'quantity': 50, 'avg_price': 2800.00}
        ]
    }


@contextmanager
def mock_database_session():
    """Context manager for mocking database sessions."""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    
    try:
        yield mock_conn, mock_cursor
    finally:
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


@pytest.fixture
def database_error_scenarios():
    """Common database error scenarios for testing."""
    return {
        'connection_failed': Exception("Connection failed"),
        'query_failed': Exception("Query execution failed"),
        'pool_exhausted': Exception("Connection pool exhausted"),
        'timeout': Exception("Database timeout"),
        'permission_denied': Exception("Permission denied")
    } 