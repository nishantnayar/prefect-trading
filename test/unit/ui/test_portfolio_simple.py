"""
Simple tests for src/ui/portfolio.py

This test suite provides coverage for the portfolio UI component by mocking
external dependencies and testing individual functions.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
from pathlib import Path
import os

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Mock streamlit and other dependencies
@pytest.fixture(autouse=True)
def mock_streamlit():
    """Mock all Streamlit functions."""
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
        'button': Mock(),
        'write': Mock(),
        'plotly_chart': Mock(),
        'columns': Mock(),
        'rerun': Mock()
    }
    
    # Make the mock columns support context manager protocol
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
    mock_st['button'].return_value = False
    
    # Patch streamlit module
    with patch.dict('sys.modules', {'streamlit': Mock(**mock_st)}):
        with patch('streamlit.title', mock_st['title']):
            with patch('streamlit.subheader', mock_st['subheader']):
                with patch('streamlit.metric', mock_st['metric']):
                    with patch('streamlit.dataframe', mock_st['dataframe']):
                        with patch('streamlit.info', mock_st['info']):
                            with patch('streamlit.warning', mock_st['warning']):
                                with patch('streamlit.success', mock_st['success']):
                                    with patch('streamlit.error', mock_st['error']):
                                        with patch('streamlit.caption', mock_st['caption']):
                                            with patch('streamlit.divider', mock_st['divider']):
                                                with patch('streamlit.button', mock_st['button']):
                                                    with patch('streamlit.write', mock_st['write']):
                                                        with patch('streamlit.plotly_chart', mock_st['plotly_chart']):
                                                            with patch('streamlit.columns', mock_st['columns']):
                                                                with patch('streamlit.rerun', mock_st['rerun']):
                                                                    yield mock_st


@pytest.fixture
def sample_account_info():
    """Sample account information for testing."""
    return {
        'portfolio_value': 100000.0,
        'cash': 25000.0,
        'buying_power': 50000.0,
        'equity': 100000.0,
        'daytrading_buying_power': 25000.0,
        'initial_margin': 15000.0,
        'status': 'ACTIVE',
        'pattern_day_trader': False,
        'trading_blocked': False,
        'shorting_enabled': True,
        'daytrade_count': 2,
        'multiplier': 2,
        'maintenance_margin': 10000.0
    }


@pytest.fixture
def sample_positions():
    """Sample positions data for testing."""
    return [
        {
            'symbol': 'AAPL',
            'qty': 100,
            'side': 'long',
            'current_price': 150.0,
            'cost_basis': 140.0,
            'market_value': 15000.0,
            'unrealized_pl': 1000.0,
            'unrealized_plpc': 0.0714
        },
        {
            'symbol': 'GOOGL',
            'qty': 50,
            'side': 'long',
            'current_price': 2800.0,
            'cost_basis': 2900.0,
            'market_value': 140000.0,
            'unrealized_pl': -5000.0,
            'unrealized_plpc': -0.0345
        }
    ]


class TestPortfolioBasic:
    """Basic tests for portfolio functionality."""
    
    def test_portfolio_import(self, mock_streamlit):
        """Test that portfolio module can be imported."""
        # Mock pandas and other dependencies
        with patch('pandas.DataFrame') as mock_pd:
            with patch('plotly.graph_objects.Pie') as mock_pie:
                # Mock the PortfolioManager import
                with patch('src.data.sources.portfolio_manager.PortfolioManager'):
                    # Import the function directly
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("portfolio", "src/ui/portfolio.py")
                    portfolio_module = importlib.util.module_from_spec(spec)
                    
                    # Mock the PortfolioManager before executing the module
                    portfolio_module.PortfolioManager = Mock()
                    spec.loader.exec_module(portfolio_module)
                    
                    # Verify the module was loaded
                    assert hasattr(portfolio_module, 'display_account_overview')
                    assert hasattr(portfolio_module, 'display_positions_table')
                    assert hasattr(portfolio_module, 'display_portfolio_allocation')
                    assert hasattr(portfolio_module, 'display_trading_history')
                    assert hasattr(portfolio_module, 'display_risk_metrics')
                    assert hasattr(portfolio_module, 'render_portfolio')
    
    def test_display_account_overview_basic(self, mock_streamlit):
        """Test basic account overview display."""
        # Mock pandas
        with patch('pandas.DataFrame') as mock_pd:
            # Mock the PortfolioManager import
            with patch('src.data.sources.portfolio_manager.PortfolioManager'):
                # Import the function directly
                import importlib.util
                spec = importlib.util.spec_from_file_location("portfolio", "src/ui/portfolio.py")
                portfolio_module = importlib.util.module_from_spec(spec)
                
                # Mock the PortfolioManager before executing the module
                portfolio_module.PortfolioManager = Mock()
                spec.loader.exec_module(portfolio_module)
                
                # Test the function
                account_info = {
                    'portfolio_value': 100000.0,
                    'cash': 25000.0,
                    'buying_power': 50000.0,
                    'pattern_day_trader': False,
                    'trading_blocked': False
                }
                
                portfolio_module.display_account_overview(account_info)
                
                # Verify subheader was called
                mock_streamlit['subheader'].assert_called_with("💰 Account Overview")
                
                # Verify metrics were called
                assert mock_streamlit['metric'].call_count >= 4  # At least 4 account metrics
    
    def test_display_positions_table_basic(self, mock_streamlit):
        """Test basic positions table display."""
        # Mock pandas
        with patch('pandas.DataFrame') as mock_pd:
            # Mock the PortfolioManager import
            with patch('src.data.sources.portfolio_manager.PortfolioManager'):
                # Import the function directly
                import importlib.util
                spec = importlib.util.spec_from_file_location("portfolio", "src/ui/portfolio.py")
                portfolio_module = importlib.util.module_from_spec(spec)
                
                # Mock the PortfolioManager before executing the module
                portfolio_module.PortfolioManager = Mock()
                spec.loader.exec_module(portfolio_module)
                
                # Test the function
                positions = [
                    {
                        'symbol': 'AAPL',
                        'qty': 100,
                        'current_price': 150.0,
                        'market_value': 15000.0,
                        'unrealized_pl': 1000.0
                    }
                ]
                
                portfolio_module.display_positions_table(positions)
                
                # Verify subheader was called
                mock_streamlit['subheader'].assert_called_with("📊 Current Positions")
                
                # Verify dataframe was called
                mock_streamlit['dataframe'].assert_called()
    
    def test_display_risk_metrics_basic(self, mock_streamlit):
        """Test basic risk metrics display."""
        # Mock pandas
        with patch('pandas.DataFrame') as mock_pd:
            # Mock the PortfolioManager import
            with patch('src.data.sources.portfolio_manager.PortfolioManager'):
                # Import the function directly
                import importlib.util
                spec = importlib.util.spec_from_file_location("portfolio", "src/ui/portfolio.py")
                portfolio_module = importlib.util.module_from_spec(spec)
                
                # Mock the PortfolioManager before executing the module
                portfolio_module.PortfolioManager = Mock()
                spec.loader.exec_module(portfolio_module)
                
                # Test the function
                account_info = {
                    'portfolio_value': 100000.0,
                    'initial_margin': 10000.0,
                    'maintenance_margin': 5000.0,
                    'pattern_day_trader': False,
                    'trading_blocked': False
                }
                
                positions = [
                    {
                        'symbol': 'AAPL',
                        'market_value': 1500.0
                    }
                ]
                
                portfolio_module.display_risk_metrics(account_info, positions)
                
                # Verify subheader was called
                mock_streamlit['subheader'].assert_any_call("⚠️ Risk Analysis")
                mock_streamlit['subheader'].assert_any_call("Risk Warnings")
                
                # Verify metrics were called
                assert mock_streamlit['metric'].call_count >= 4  # At least 4 risk metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 