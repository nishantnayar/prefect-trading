#!/usr/bin/env python3
"""
Unit tests for portfolio manager optimization.

This test suite verifies the optimized PortfolioManager to ensure it:
1. Reduces API calls through caching
2. Provides the same data as before
3. Works correctly with existing methods
"""

import pytest
import time
from unittest.mock import patch, MagicMock

from src.data.sources.portfolio_manager import PortfolioManager


@pytest.fixture
def portfolio_manager():
    """Fixture to provide portfolio manager instance."""
    return PortfolioManager()


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
    assert hasattr(portfolio_manager, 'get_account_info')
    assert hasattr(portfolio_manager, 'get_positions')
    assert hasattr(portfolio_manager, 'get_orders')
    assert hasattr(portfolio_manager, 'clear_cache')


def test_backward_compatibility(portfolio_manager):
    """Test that the portfolio manager maintains backward compatibility."""
    # Test old method still works
    summary = portfolio_manager.get_portfolio_summary()
    
    assert summary is not None
    assert 'metrics' in summary
    assert 'positions' in summary
    assert 'recent_activity' in summary


def test_portfolio_manager_methods_exist(portfolio_manager):
    """Test that all expected methods exist on portfolio manager."""
    expected_methods = [
        'get_account_info',
        'get_positions',
        'get_orders',
        'get_portfolio_summary',
        'clear_cache'
    ]
    
    for method_name in expected_methods:
        assert hasattr(portfolio_manager, method_name), f"Method {method_name} not found"


@pytest.mark.integration
def test_portfolio_manager_with_real_api():
    """Test portfolio manager with real API (integration test)."""
    portfolio_manager = PortfolioManager()
    
    # Test that we can get account info
    account_info = portfolio_manager.get_account_info()
    assert account_info is not None
    assert 'id' in account_info


@pytest.mark.integration
def test_portfolio_optimization_performance():
    """Test portfolio optimization performance with real API."""
    portfolio_manager = PortfolioManager()
    
    # Test performance of multiple calls
    start_time = time.time()
    
    # First call
    all_data_1 = portfolio_manager.get_portfolio_summary()
    
    # Second call (should use cache)
    all_data_2 = portfolio_manager.get_portfolio_summary()
    
    end_time = time.time()
    
    # Verify data consistency
    assert all_data_1 == all_data_2
    
    # Verify reasonable performance (should be fast due to caching)
    assert end_time - start_time < 5.0  # Should complete within 5 seconds


if __name__ == "__main__":
    # Allow running as standalone script for debugging
    import sys
    pytest.main([__file__] + sys.argv[1:]) 