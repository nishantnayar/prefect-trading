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
def mock_trading_client():
    """Fixture for a mocked Alpaca TradingClient."""
    with patch('alpaca.trading.client.TradingClient') as mock_client:
        instance = mock_client.return_value
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
        instance.get_account.return_value = mock_account

        # Mock positions response
        mock_position = MagicMock()
        mock_position.symbol = 'AAPL'
        mock_position.qty = '10'
        # ... add other position attributes if needed
        instance.get_all_positions.return_value = [mock_position]

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
        instance.get_orders.return_value = [mock_order]

        yield mock_client

@pytest.fixture
def mock_data_client():
    """Fixture for a mocked Alpaca StockHistoricalDataClient."""
    with patch('alpaca.data.historical.StockHistoricalDataClient') as mock_client:
        yield mock_client

@patch('prefect.blocks.system.Secret')
def test_portfolio_manager_initialization(MockSecret, mock_trading_client, mock_data_client):
    """Test that the PortfolioManager initializes correctly."""
    MockSecret.load.return_value.get.return_value = "fake_key"
    manager = PortfolioManager()
    assert manager.trading_client is not None
    assert manager.data_client is not None
    mock_trading_client.assert_called_once()
    mock_data_client.assert_called_once()


@patch('prefect.blocks.system.Secret')
def test_get_account_info(MockSecret, mock_trading_client, mock_data_client):
    """Test fetching account information."""
    MockSecret.load.return_value.get.return_value = "fake_key"
    manager = PortfolioManager()
    account_info = manager.get_account_info()

    assert account_info is not None
    assert account_info['id'] == 'test_account_id'
    assert account_info['status'] == 'ACTIVE'
    assert account_info['portfolio_value'] == 100000.0


@patch('prefect.blocks.system.Secret')
def test_get_positions(MockSecret, mock_trading_client, mock_data_client):
    """Test fetching positions."""
    MockSecret.load.return_value.get.return_value = "fake_key"
    manager = PortfolioManager()
    positions = manager.get_positions()

    assert positions is not None
    assert len(positions) == 1
    assert positions[0]['symbol'] == 'AAPL'


@patch('prefect.blocks.system.Secret')
def test_get_orders(MockSecret, mock_trading_client, mock_data_client):
    """Test fetching orders."""
    MockSecret.load.return_value.get.return_value = "fake_key"
    manager = PortfolioManager()
    orders = manager.get_orders(status="closed")

    assert orders is not None
    assert len(orders) == 1
    assert orders[0]['status'] == 'filled'

@patch('prefect.blocks.system.Secret')
def test_get_portfolio_summary(MockSecret, mock_trading_client, mock_data_client):
    """Test getting a full portfolio summary."""
    MockSecret.load.return_value.get.return_value = "fake_key"
    manager = PortfolioManager()
    summary = manager.get_portfolio_summary()

    assert summary is not None
    assert 'metrics' in summary
    assert 'positions' in summary
    assert 'recent_activity' in summary
    assert summary['metrics']['total_value'] == 100000.0
    assert len(summary['positions']) == 1
    assert len(summary['recent_activity']) > 0 