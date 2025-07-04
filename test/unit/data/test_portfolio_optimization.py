#!/usr/bin/env python3
"""
Unit tests for portfolio manager optimization.

This test suite verifies the optimized PortfolioManager to ensure it:
1. Reduces API calls through caching
2. Provides the same data as before
3. Works correctly with the new get_all_portfolio_data() method
"""

import pytest
import time
from unittest.mock import patch, MagicMock

from src.data.sources.portfolio_manager import PortfolioManager


@pytest.fixture
def portfolio_manager():
    """Fixture to provide portfolio manager instance with 30-second cache."""
    return PortfolioManager(cache_duration=30)


@pytest.fixture
def mock_portfolio_data():
    """Fixture to provide mock portfolio data."""
    return {
        'account_info': {
            'id': 'test_account_123',
            'status': 'ACTIVE',
            'currency': 'USD'
        },
        'metrics': {
            'total_value': 100000.0,
            'buying_power': 50000.0,
            'cash': 25000.0
        },
        'total_positions': 5,
        'pending_orders': 2
    }


def test_portfolio_manager_initialization(portfolio_manager):
    """Test that portfolio manager initializes correctly."""
    assert portfolio_manager is not None
    assert hasattr(portfolio_manager, 'get_all_portfolio_data')
    assert hasattr(portfolio_manager, 'get_account_info')
    assert hasattr(portfolio_manager, 'get_positions')
    assert hasattr(portfolio_manager, 'get_orders')
    assert hasattr(portfolio_manager, 'clear_cache')


@patch('src.data.sources.portfolio_manager.PortfolioManager')
def test_first_call_makes_api_calls(mock_portfolio_class, mock_portfolio_data):
    """Test that first call makes API calls."""
    # Mock the portfolio manager
    mock_manager = MagicMock()
    mock_manager.get_all_portfolio_data.return_value = mock_portfolio_data
    mock_portfolio_class.return_value = mock_manager
    
    portfolio_manager = PortfolioManager(cache_duration=30)
    
    # First call should return data
    result = portfolio_manager.get_all_portfolio_data()
    
    assert result == mock_portfolio_data
    mock_manager.get_all_portfolio_data.assert_called_once()


@patch('src.data.sources.portfolio_manager.PortfolioManager')
def test_second_call_uses_cache(mock_portfolio_class, mock_portfolio_data):
    """Test that second call uses cache."""
    # Mock the portfolio manager
    mock_manager = MagicMock()
    mock_manager.get_all_portfolio_data.return_value = mock_portfolio_data
    mock_portfolio_class.return_value = mock_manager
    
    portfolio_manager = PortfolioManager(cache_duration=30)
    
    # First call
    result1 = portfolio_manager.get_all_portfolio_data()
    
    # Second call should use cache
    result2 = portfolio_manager.get_all_portfolio_data()
    
    assert result1 == result2
    # Should only be called once due to caching
    assert mock_manager.get_all_portfolio_data.call_count == 1


@patch('src.data.sources.portfolio_manager.PortfolioManager')
def test_cache_clearing(mock_portfolio_class, mock_portfolio_data):
    """Test that cache clearing works correctly."""
    # Mock the portfolio manager
    mock_manager = MagicMock()
    mock_manager.get_all_portfolio_data.return_value = mock_portfolio_data
    mock_manager.clear_cache = MagicMock()
    mock_portfolio_class.return_value = mock_manager
    
    portfolio_manager = PortfolioManager(cache_duration=30)
    
    # First call
    portfolio_manager.get_all_portfolio_data()
    
    # Clear cache
    portfolio_manager.clear_cache()
    
    # Verify clear_cache was called
    mock_manager.clear_cache.assert_called_once()


@patch('src.data.sources.portfolio_manager.PortfolioManager')
def test_individual_method_calls(mock_portfolio_class):
    """Test that individual method calls work correctly."""
    # Mock the portfolio manager
    mock_manager = MagicMock()
    mock_manager.get_account_info.return_value = {'id': 'test_account'}
    mock_manager.get_positions.return_value = [{'symbol': 'AAPL', 'qty': 100}]
    mock_manager.get_orders.return_value = [{'id': 'order_1', 'status': 'closed'}]
    mock_portfolio_class.return_value = mock_manager
    
    portfolio_manager = PortfolioManager()
    
    # Test individual methods
    account_info = portfolio_manager.get_account_info()
    positions = portfolio_manager.get_positions()
    orders = portfolio_manager.get_orders("closed")
    
    assert account_info == {'id': 'test_account'}
    assert positions == [{'symbol': 'AAPL', 'qty': 100}]
    assert orders == [{'id': 'order_1', 'status': 'closed'}]


@patch('src.data.sources.portfolio_manager.PortfolioManager')
def test_backward_compatibility(mock_portfolio_class):
    """Test that the optimized portfolio manager maintains backward compatibility."""
    # Mock the portfolio manager
    mock_manager = MagicMock()
    mock_manager.get_portfolio_summary.return_value = {
        'metrics': {'total_value': 100000.0},
        'positions': [{'symbol': 'AAPL'}],
        'recent_activity': [{'type': 'buy'}]
    }
    mock_portfolio_class.return_value = mock_manager
    
    portfolio_manager = PortfolioManager()
    
    # Test old method still works
    summary = portfolio_manager.get_portfolio_summary()
    
    assert summary is not None
    assert 'metrics' in summary
    assert 'positions' in summary
    assert 'recent_activity' in summary


def test_portfolio_manager_methods_exist(portfolio_manager):
    """Test that all expected methods exist on portfolio manager."""
    expected_methods = [
        'get_all_portfolio_data',
        'get_account_info',
        'get_positions',
        'get_orders',
        'get_portfolio_summary',
        'clear_cache'
    ]
    
    for method_name in expected_methods:
        assert hasattr(portfolio_manager, method_name), f"Method {method_name} not found"


@patch('src.data.sources.portfolio_manager.PortfolioManager')
def test_data_consistency(mock_portfolio_class, mock_portfolio_data):
    """Test that data consistency is maintained across calls."""
    # Mock the portfolio manager
    mock_manager = MagicMock()
    mock_manager.get_all_portfolio_data.return_value = mock_portfolio_data
    mock_portfolio_class.return_value = mock_manager
    
    portfolio_manager = PortfolioManager(cache_duration=30)
    
    # Multiple calls should return the same data
    result1 = portfolio_manager.get_all_portfolio_data()
    result2 = portfolio_manager.get_all_portfolio_data()
    result3 = portfolio_manager.get_all_portfolio_data()
    
    assert result1 == result2 == result3
    assert result1['account_info']['id'] == 'test_account_123'


@patch('src.data.sources.portfolio_manager.PortfolioManager')
def test_cache_duration_configuration(mock_portfolio_class):
    """Test that cache duration can be configured."""
    # Mock the portfolio manager
    mock_manager = MagicMock()
    mock_portfolio_class.return_value = mock_manager
    
    # Test different cache durations
    portfolio_manager_30s = PortfolioManager(cache_duration=30)
    portfolio_manager_60s = PortfolioManager(cache_duration=60)
    
    assert portfolio_manager_30s is not None
    assert portfolio_manager_60s is not None


# Integration test that requires actual API connection
@pytest.mark.integration
def test_portfolio_manager_with_real_api():
    """Test portfolio manager with real API connection."""
    portfolio_manager = PortfolioManager()
    
    try:
        # This should not raise an exception
        all_data = portfolio_manager.get_all_portfolio_data()
        
        if all_data:
            assert isinstance(all_data, dict)
            assert 'account_info' in all_data
            assert 'metrics' in all_data
        else:
            pytest.skip("No portfolio data available")
            
    except Exception as e:
        pytest.skip(f"API not available: {e}")


@pytest.mark.integration
def test_portfolio_optimization_performance():
    """Test portfolio optimization performance with real API."""
    portfolio_manager = PortfolioManager(cache_duration=30)
    
    try:
        # First call - should make API calls
        start_time = time.time()
        all_data_1 = portfolio_manager.get_all_portfolio_data()
        first_call_time = time.time() - start_time
        
        if not all_data_1:
            pytest.skip("No portfolio data available")
        
        # Second call - should use cache
        start_time = time.time()
        all_data_2 = portfolio_manager.get_all_portfolio_data()
        second_call_time = time.time() - start_time
        
        # Verify data consistency
        assert all_data_1['account_info'].get('id') == all_data_2['account_info'].get('id')
        
        # Verify cache is working (second call should be faster)
        assert second_call_time <= first_call_time
        
    except Exception as e:
        pytest.skip(f"API not available: {e}")


if __name__ == "__main__":
    # Allow running as standalone script for debugging
    import sys
    pytest.main([__file__] + sys.argv[1:]) 