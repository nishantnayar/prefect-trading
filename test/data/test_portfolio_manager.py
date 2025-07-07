"""
Unit tests for the PortfolioManager class.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv('config/.env', override=True)

from src.data.sources.portfolio_manager import PortfolioManager

@pytest.fixture
def mock_portfolio_manager():
    """Fixture for a mocked PortfolioManager with all dependencies mocked."""
    with patch('src.data.sources.portfolio_manager.TradingClient') as mock_trading_client, \
         patch('src.data.sources.portfolio_manager.StockHistoricalDataClient') as mock_data_client, \
         patch('src.data.sources.portfolio_manager.Secret') as mock_secret:
        
        # Mock the Secret class
        mock_secret_instance = MagicMock()
        mock_secret_instance.get.return_value = "fake_key"
        mock_secret.load.return_value = mock_secret_instance
        
        # Mock trading client instance
        mock_trading_instance = MagicMock()
        mock_trading_client.return_value = mock_trading_instance
        
        # Mock data client instance
        mock_data_instance = MagicMock()
        mock_data_client.return_value = mock_data_instance
        
        # Mock account response
        mock_account = MagicMock()
        mock_account.id = 'test_account_id'
        mock_account.status = 'ACTIVE'
        mock_account.portfolio_value = '100000'
        mock_account.cash = '50000'
        mock_account.buying_power = '200000'
        # Add other necessary attributes
        for attr in ['regt_buying_power', 'daytrading_buying_power', 'non_marginable_buying_power',
                     'accrued_fees', 'equity', 'last_equity', 'long_market_value', 'short_market_value',
                     'initial_margin', 'maintenance_margin', 'last_maintenance_margin', 'sma']:
            setattr(mock_account, attr, '0')
        mock_trading_instance.get_account.return_value = mock_account

        # Mock positions response
        mock_position = MagicMock()
        mock_position.symbol = 'AAPL'
        mock_position.qty = '10'
        mock_position.side = 'long'
        mock_position.market_value = '1500'
        mock_position.cost_basis = '1400'
        mock_position.unrealized_pl = '100'
        mock_position.unrealized_plpc = '0.07'
        mock_position.unrealized_intraday_pl = '50'
        mock_position.unrealized_intraday_plpc = '0.035'
        mock_position.current_price = '150'
        mock_position.lastday_price = '145'
        mock_position.change_today = '5'
        mock_trading_instance.get_all_positions.return_value = [mock_position]

        # Mock orders response
        mock_order = MagicMock()
        mock_order.id = 'order_1'
        mock_order.symbol = 'AAPL'
        mock_order.side = 'buy'
        mock_order.status = 'filled'
        mock_order.qty = '10'
        mock_order.filled_qty = '10'
        mock_order.filled_avg_price = '150.00'
        mock_order.filled_at = datetime.now()
        mock_order.type = 'market'
        mock_order.time_in_force = 'day'
        mock_trading_instance.get_orders.return_value = [mock_order]

        # Create the PortfolioManager instance
        manager = PortfolioManager()
        
        # Store the mocks for assertions
        manager._mock_trading_client = mock_trading_client
        manager._mock_data_client = mock_data_client
        manager._mock_trading_instance = mock_trading_instance
        manager._mock_data_instance = mock_data_instance
        
        yield manager

def test_portfolio_manager_initialization(mock_portfolio_manager):
    """Test that the PortfolioManager initializes correctly."""
    assert mock_portfolio_manager.trading_client is not None
    assert mock_portfolio_manager.data_client is not None
    mock_portfolio_manager._mock_trading_client.assert_called_once()
    mock_portfolio_manager._mock_data_client.assert_called_once()

def test_get_account_info(mock_portfolio_manager):
    """Test fetching account information."""
    account_info = mock_portfolio_manager.get_account_info()

    assert account_info is not None
    assert account_info['id'] == 'test_account_id'
    assert account_info['status'] == 'ACTIVE'
    assert account_info['portfolio_value'] == 100000.0

def test_get_positions(mock_portfolio_manager):
    """Test fetching positions."""
    positions = mock_portfolio_manager.get_positions()

    assert positions is not None
    assert len(positions) == 1
    assert positions[0]['symbol'] == 'AAPL'

def test_get_orders(mock_portfolio_manager):
    """Test fetching orders."""
    orders = mock_portfolio_manager.get_orders(status="closed")

    assert orders is not None
    assert len(orders) == 1
    assert orders[0]['status'] == 'filled'

def test_get_portfolio_summary(mock_portfolio_manager):
    """Test getting a full portfolio summary."""
    summary = mock_portfolio_manager.get_portfolio_summary()

    assert summary is not None
    assert 'metrics' in summary
    assert 'positions' in summary
    assert 'recent_activity' in summary
    assert summary['metrics']['total_value'] == 100000.0
    assert len(summary['positions']) == 1
    assert len(summary['recent_activity']) > 0 