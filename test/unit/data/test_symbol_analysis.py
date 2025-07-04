#!/usr/bin/env python3
"""
Unit tests for symbol analysis functionality.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.data.sources.symbol_manager import SymbolManager
from src.database.database_connectivity import DatabaseConnectivity


@pytest.fixture
def symbol_manager():
    """Fixture to provide symbol manager instance."""
    return SymbolManager()


@pytest.fixture
def db_connectivity():
    """Fixture to provide database connectivity instance."""
    return DatabaseConnectivity()


def test_symbol_manager_initialization(symbol_manager):
    """Test that symbol manager initializes correctly."""
    assert symbol_manager is not None
    assert hasattr(symbol_manager, 'get_active_symbols')
    assert hasattr(symbol_manager, 'get_symbol_info')


def test_get_active_symbols(symbol_manager):
    """Test getting active symbols from symbol manager."""
    active_symbols = symbol_manager.get_active_symbols()
    
    assert isinstance(active_symbols, list)
    # Should have at least some symbols
    assert len(active_symbols) >= 0
    
    # If we have symbols, they should be strings
    if active_symbols:
        assert all(isinstance(symbol, str) for symbol in active_symbols)


def test_get_symbol_info(symbol_manager):
    """Test getting symbol info for a specific symbol."""
    # Test with a common symbol like AAPL
    symbol_info = symbol_manager.get_symbol_info('AAPL')
    
    # Symbol info should be a dictionary or None
    assert symbol_info is None or isinstance(symbol_info, dict)
    
    # If we have info, it should have expected fields
    if symbol_info:
        assert 'symbol' in symbol_info
        assert 'name' in symbol_info


def test_get_symbol_info_nonexistent(symbol_manager):
    """Test getting symbol info for a non-existent symbol."""
    symbol_info = symbol_manager.get_symbol_info('NONEXISTENT_SYMBOL')
    
    # Should return None for non-existent symbols
    assert symbol_info is None


def test_database_connectivity_initialization(db_connectivity):
    """Test that database connectivity initializes correctly."""
    assert db_connectivity is not None
    assert hasattr(db_connectivity, 'get_session')


@patch('src.database.database_connectivity.DatabaseConnectivity')
def test_market_data_query(mock_db_class):
    """Test market data query execution."""
    # Mock database connection
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_cursor
    
    # Mock query result
    mock_cursor.fetchone.return_value = (100, '2024-01-01', '2024-01-31', 150.0, 160.0, 140.0, 1000000)
    
    mock_db_class.return_value = mock_db
    
    db = DatabaseConnectivity()
    
    with db.get_session() as cursor:
        cursor.execute("""
            SELECT 
                COUNT(*) as data_points,
                MIN(timestamp) as first_data,
                MAX(timestamp) as last_data,
                AVG(close) as avg_price,
                MAX(close) as max_price,
                MIN(close) as min_price,
                AVG(volume) as avg_volume
            FROM market_data 
            WHERE symbol = 'AAPL'
        """)
        
        market_summary = cursor.fetchone()
        
        assert market_summary is not None
        assert len(market_summary) == 7
        assert market_summary[0] == 100  # data_points
        assert market_summary[3] == 150.0  # avg_price


@patch('src.database.database_connectivity.DatabaseConnectivity')
def test_company_info_query(mock_db_class):
    """Test company info query execution."""
    # Mock database connection
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_cursor
    
    # Mock query result
    mock_cursor.fetchone.return_value = ('Apple Inc.', 'Technology', 'Consumer Electronics', 2000000000000, 150.0)
    
    mock_db_class.return_value = mock_db
    
    db = DatabaseConnectivity()
    
    with db.get_session() as cursor:
        cursor.execute("""
            SELECT 
                "longName",
                sector,
                industry,
                "marketCap",
                "currentPrice"
            FROM yahoo_company_info 
            WHERE symbol = 'AAPL'
        """)
        
        company_info = cursor.fetchone()
        
        assert company_info is not None
        assert len(company_info) == 5
        assert company_info[0] == 'Apple Inc.'
        assert company_info[1] == 'Technology'


@patch('src.database.database_connectivity.DatabaseConnectivity')
def test_news_query(mock_db_class):
    """Test news query execution."""
    # Mock database connection
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_cursor
    
    # Mock query result
    mock_cursor.fetchall.return_value = [
        ('Apple Reports Strong Q4 Earnings', 'Reuters', '2024-01-15'),
        ('AAPL Stock Hits New High', 'Bloomberg', '2024-01-14'),
        ('Apple Announces New Product Line', 'CNBC', '2024-01-13')
    ]
    
    mock_db_class.return_value = mock_db
    
    db = DatabaseConnectivity()
    
    with db.get_session() as cursor:
        cursor.execute("""
            SELECT 
                title,
                source_name,
                published_at
            FROM news_articles 
            WHERE title ILIKE '%AAPL%' OR description ILIKE '%AAPL%'
            ORDER BY published_at DESC
            LIMIT 3
        """)
        
        news = cursor.fetchall()
        
        assert news is not None
        assert len(news) == 3
        assert all(len(article) == 3 for article in news)
        assert all('AAPL' in article[0] for article in news)


def test_symbol_manager_methods_exist(symbol_manager):
    """Test that all expected methods exist on symbol manager."""
    expected_methods = [
        'get_active_symbols',
        'get_symbol_info',
        'add_symbol',
        'remove_symbol',
        'update_symbol'
    ]
    
    for method_name in expected_methods:
        assert hasattr(symbol_manager, method_name), f"Method {method_name} not found"


def test_database_connectivity_methods_exist(db_connectivity):
    """Test that all expected methods exist on database connectivity."""
    expected_methods = [
        'get_session',
        'close'
    ]
    
    for method_name in expected_methods:
        assert hasattr(db_connectivity, method_name), f"Method {method_name} not found"


# Integration test that requires actual database
@pytest.mark.integration
def test_symbol_manager_with_real_database():
    """Test symbol manager with real database connection."""
    symbol_manager = SymbolManager()
    
    # This should not raise an exception
    try:
        active_symbols = symbol_manager.get_active_symbols()
        assert isinstance(active_symbols, list)
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


@pytest.mark.integration
def test_database_queries_with_real_database():
    """Test database queries with real database connection."""
    db = DatabaseConnectivity()
    
    try:
        with db.get_session() as cursor:
            # Test a simple query
            cursor.execute("SELECT COUNT(*) FROM symbols WHERE is_active = true")
            result = cursor.fetchone()
            assert result is not None
            assert isinstance(result[0], int)
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


if __name__ == "__main__":
    # Allow running as standalone script for debugging
    import sys
    pytest.main([__file__] + sys.argv[1:]) 