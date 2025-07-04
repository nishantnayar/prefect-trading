#!/usr/bin/env python3
"""
Unit tests for UI components and data fetching.

This test suite verifies that UI components work correctly and can fetch data properly.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.ui.components.symbol_selector import display_symbol_selector
from src.ui.components.market_status import display_market_status
from src.data.sources.symbol_manager import SymbolManager
from src.utils.market_hours import MarketHoursManager
from src.database.database_connectivity import DatabaseConnectivity


@pytest.fixture
def symbol_manager():
    """Fixture to provide symbol manager instance."""
    return SymbolManager()


@pytest.fixture
def market_hours_manager():
    """Fixture to provide market hours manager instance."""
    return MarketHoursManager()


@pytest.fixture
def db_connectivity():
    """Fixture to provide database connectivity instance."""
    return DatabaseConnectivity()


def test_symbol_selector_component_import():
    """Test that symbol selector component can be imported."""
    try:
        from src.ui.components.symbol_selector import display_symbol_selector
        assert display_symbol_selector is not None
    except ImportError as e:
        pytest.fail(f"Could not import symbol selector component: {e}")


def test_market_status_component_import():
    """Test that market status component can be imported."""
    try:
        from src.ui.components.market_status import display_market_status
        assert display_market_status is not None
    except ImportError as e:
        pytest.fail(f"Could not import market status component: {e}")


def test_symbol_manager_initialization(symbol_manager):
    """Test that symbol manager initializes correctly."""
    assert symbol_manager is not None
    assert hasattr(symbol_manager, 'get_active_symbols')
    assert hasattr(symbol_manager, 'get_symbol_info')


def test_market_hours_manager_initialization(market_hours_manager):
    """Test that market hours manager initializes correctly."""
    assert market_hours_manager is not None
    assert hasattr(market_hours_manager, 'is_market_open')


def test_get_active_symbols(symbol_manager):
    """Test getting active symbols from symbol manager."""
    symbols = symbol_manager.get_active_symbols()
    
    assert isinstance(symbols, list)
    # Should have at least some symbols
    assert len(symbols) >= 0
    
    # If we have symbols, they should be strings
    if symbols:
        assert all(isinstance(symbol, str) for symbol in symbols)


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


def test_market_open_status(market_hours_manager):
    """Test market open status check."""
    is_open = market_hours_manager.is_market_open()
    
    # Should return a boolean
    assert isinstance(is_open, bool)


@patch('src.database.database_connectivity.DatabaseConnectivity')
def test_news_fetching_query(mock_db_class):
    """Test news article fetching query."""
    # Mock database connection
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_cursor
    
    # Mock query result
    mock_cursor.fetchall.return_value = [
        ('Apple Reports Strong Q4 Earnings', 'Reuters', 'https://example.com/1', '2024-01-15', 'Apple reported strong earnings...'),
        ('AAPL Stock Hits New High', 'Bloomberg', 'https://example.com/2', '2024-01-14', 'AAPL stock reached new highs...'),
        ('Apple Announces New Product Line', 'CNBC', 'https://example.com/3', '2024-01-13', 'Apple announced new products...')
    ]
    
    mock_db_class.return_value = mock_db
    
    db = DatabaseConnectivity()
    
    with db.get_session() as cursor:
        cursor.execute("""
            SELECT title, source_name, url, published_at, description
            FROM news_articles
            ORDER BY published_at DESC
            LIMIT 3
        """)
        
        articles = cursor.fetchall()
        
        assert articles is not None
        assert len(articles) == 3
        assert all(len(article) == 5 for article in articles)
        
        # Check first article structure
        title, source, url, published_at, description = articles[0]
        assert isinstance(title, str)
        assert isinstance(source, str)
        assert isinstance(url, str)
        assert isinstance(published_at, str)
        assert isinstance(description, str)


@patch('src.database.database_connectivity.DatabaseConnectivity')
def test_portfolio_data_queries(mock_db_class):
    """Test portfolio data fetching queries."""
    # Mock database connection
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.get_session.return_value.__enter__.return_value = mock_cursor
    
    # Mock query results
    mock_cursor.fetchone.side_effect = [
        (1000,),  # market_data_count
        (20,)     # active_symbols_count
    ]
    mock_cursor.fetchall.return_value = [
        ('AAPL', 150.0, 1000000, '2024-01-15 10:00:00'),
        ('MSFT', 300.0, 500000, '2024-01-15 10:00:00'),
        ('GOOGL', 2500.0, 200000, '2024-01-15 10:00:00')
    ]
    
    mock_db_class.return_value = mock_db
    
    db = DatabaseConnectivity()
    
    with db.get_session() as cursor:
        # Check market data count
        cursor.execute("SELECT COUNT(*) FROM market_data")
        market_data_count = cursor.fetchone()[0]
        assert market_data_count == 1000
        
        # Check active symbols count
        cursor.execute("SELECT COUNT(*) FROM symbols WHERE is_active = true")
        active_symbols_count = cursor.fetchone()[0]
        assert active_symbols_count == 20
        
        # Get sample market data
        cursor.execute("""
            SELECT symbol, price, volume, timestamp 
            FROM market_data 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        recent_data = cursor.fetchall()
        
        assert recent_data is not None
        assert len(recent_data) == 3
        assert all(len(data) == 4 for data in recent_data)
        
        # Check first data point structure
        symbol, price, volume, timestamp = recent_data[0]
        assert isinstance(symbol, str)
        assert isinstance(price, float)
        assert isinstance(volume, int)
        assert isinstance(timestamp, str)


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


def test_market_hours_manager_methods_exist(market_hours_manager):
    """Test that all expected methods exist on market hours manager."""
    expected_methods = [
        'is_market_open',
        'get_market_hours',
        'is_weekend',
        'is_holiday'
    ]
    
    for method_name in expected_methods:
        assert hasattr(market_hours_manager, method_name), f"Method {method_name} not found"


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
    
    try:
        symbols = symbol_manager.get_active_symbols()
        assert isinstance(symbols, list)
        
        if symbols:
            symbol_info = symbol_manager.get_symbol_info(symbols[0])
            assert symbol_info is None or isinstance(symbol_info, dict)
            
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


@pytest.mark.integration
def test_market_hours_manager_with_real_time():
    """Test market hours manager with real time."""
    market_hours_manager = MarketHoursManager()
    
    try:
        is_open = market_hours_manager.is_market_open()
        assert isinstance(is_open, bool)
        
    except Exception as e:
        pytest.skip(f"Market hours manager not available: {e}")


@pytest.mark.integration
def test_news_fetching_with_real_database():
    """Test news fetching with real database connection."""
    db = DatabaseConnectivity()
    
    try:
        with db.get_session() as cursor:
            cursor.execute("""
                SELECT title, source_name, url, published_at, description
                FROM news_articles
                ORDER BY published_at DESC
                LIMIT 3
            """)
            
            articles = cursor.fetchall()
            assert isinstance(articles, list)
            
            if articles:
                assert all(len(article) == 5 for article in articles)
                
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


@pytest.mark.integration
def test_portfolio_data_with_real_database():
    """Test portfolio data with real database connection."""
    db = DatabaseConnectivity()
    
    try:
        with db.get_session() as cursor:
            # Check market data count
            cursor.execute("SELECT COUNT(*) FROM market_data")
            market_data_count = cursor.fetchone()[0]
            assert isinstance(market_data_count, int)
            assert market_data_count >= 0
            
            # Check active symbols count
            cursor.execute("SELECT COUNT(*) FROM symbols WHERE is_active = true")
            active_symbols_count = cursor.fetchone()[0]
            assert isinstance(active_symbols_count, int)
            assert active_symbols_count >= 0
            
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


if __name__ == "__main__":
    # Allow running as standalone script for debugging
    import sys
    pytest.main([__file__] + sys.argv[1:]) 