"""
Direct tests for src/ui/portfolio.py functions

This test suite provides coverage for the portfolio UI component by directly
testing the functions without importing the entire module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

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
    
    # Configure column mocks - return different numbers based on call
    def columns_side_effect(num_cols):
        if isinstance(num_cols, list):
            return [Mock() for _ in range(len(num_cols))]
        else:
            return [Mock() for _ in range(num_cols)]
    
    # Make the mock columns support context manager protocol
    def create_context_mock():
        mock = Mock()
        mock.__enter__ = Mock(return_value=mock)
        mock.__exit__ = Mock(return_value=None)
        return mock
    
    def columns_side_effect_with_context(num_cols):
        if isinstance(num_cols, list):
            return [create_context_mock() for _ in range(len(num_cols))]
        else:
            return [create_context_mock() for _ in range(num_cols)]
    
    mock_st['columns'].side_effect = columns_side_effect_with_context
    
    # Configure button mock
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
        'account_number': '123456789',
        'status': 'ACTIVE',
        'currency': 'USD',
        'buying_power': 50000.0,
        'cash': 25000.0,
        'portfolio_value': 100000.0,
        'initial_margin': 20000.0,
        'maintenance_margin': 10000.0,
        'pattern_day_trader': False,
        'trading_blocked': False,
        'daytrade_count': 2,
        'daytrading_buying_power': 25000.0
    }

@pytest.fixture
def sample_positions():
    """Sample positions for testing."""
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

class TestDisplayAccountOverview:
    """Test the display_account_overview function."""
    
    def test_display_account_overview_basic(self, mock_streamlit, sample_account_info):
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
                portfolio_module.display_account_overview(sample_account_info)
                
                # Verify title was called
                mock_streamlit['subheader'].assert_called_with("💰 Account Overview")
                
                # Verify metrics were called
                assert mock_streamlit['metric'].call_count >= 4  # At least 4 account metrics
    
    def test_display_account_overview_empty_data(self, mock_streamlit):
        """Test account overview with empty data."""
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
                portfolio_module.display_account_overview({})
                
                # Verify title was called
                mock_streamlit['subheader'].assert_called_with("💰 Account Overview")
                
                # Verify metrics were called (should handle empty data gracefully)
                assert mock_streamlit['metric'].call_count >= 4


class TestDisplayPositionsTable:
    """Test the display_positions_table function."""
    
    def test_display_positions_table_with_positions(self, mock_streamlit, sample_positions):
        """Test positions table display with data."""
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
                portfolio_module.display_positions_table(sample_positions)
                
                # Verify subheader was called
                mock_streamlit['subheader'].assert_called_with("📊 Current Positions")
                
                # Verify dataframe was called
                mock_streamlit['dataframe'].assert_called()
    
    def test_display_positions_table_empty(self, mock_streamlit):
        """Test positions table display with no positions."""
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
                portfolio_module.display_positions_table([])
                
                # Verify subheader was called
                mock_streamlit['subheader'].assert_called_with("📊 Current Positions")
                
                # Verify info message was shown
                mock_streamlit['info'].assert_called_with("No open positions found.")
                
                # Verify dataframe was not called
                mock_streamlit['dataframe'].assert_not_called()


class TestDisplayPortfolioAllocation:
    """Test the display_portfolio_allocation function."""
    
    def test_display_portfolio_allocation_with_positions(self, mock_streamlit, sample_positions):
        """Test portfolio allocation display with data."""
        # Mock plotly
        with patch('plotly.express.pie') as mock_pie:
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
                portfolio_module.display_portfolio_allocation(sample_positions)

                # Verify subheader was called
                mock_streamlit['subheader'].assert_any_call("📈 Portfolio Allocation")
    
    def test_display_portfolio_allocation_empty(self, mock_streamlit):
        """Test portfolio allocation display with no positions."""
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
                portfolio_module.display_portfolio_allocation([])
                
                # Verify subheader was called
                mock_streamlit['subheader'].assert_called_with("📈 Portfolio Allocation")
                
                # Verify info message was shown
                mock_streamlit['info'].assert_called_with("No positions to display allocation for.")
                
                # Verify plotly chart was not called
                mock_streamlit['plotly_chart'].assert_not_called()


class TestDisplayTradingHistory:
    """Test the display_trading_history function."""
    
    def test_display_trading_history_with_orders(self, mock_streamlit):
        """Test trading history display with data."""
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
            orders = [{
                'symbol': 'AAPL',
                'side': 'buy',
                'filled_qty': 100,
                'filled_avg_price': 140.0,
                'filled_at': '2024-01-15T10:30:00Z',
                'status': 'filled'
            }]

            portfolio_module.display_trading_history(orders)

            # Verify subheader was called
            mock_streamlit['subheader'].assert_any_call("📝 Trading History")

            # Verify dataframe was called for recent trades
            mock_streamlit['dataframe'].assert_called()

            # Verify metrics were called for performance
            assert mock_streamlit['metric'].call_count >= 4  # At least 4 performance metrics
    
    def test_display_trading_history_empty(self, mock_streamlit):
        """Test trading history display with no orders."""
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
                portfolio_module.display_trading_history([])
                
                # Verify subheader was called
                mock_streamlit['subheader'].assert_called_with("📝 Trading History")
                
                # Verify info message was shown
                mock_streamlit['info'].assert_called_with("No trading history available.")
                
                # Verify dataframe was not called
                mock_streamlit['dataframe'].assert_not_called()


class TestDisplayRiskMetrics:
    """Test the display_risk_metrics function."""
    
    def test_display_risk_metrics_normal(self, mock_streamlit, sample_account_info, sample_positions):
        """Test risk metrics display with normal data."""
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
                portfolio_module.display_risk_metrics(sample_account_info, sample_positions)
                
                # Verify subheader was called
                mock_streamlit['subheader'].assert_any_call("⚠️ Risk Analysis")
                mock_streamlit['subheader'].assert_any_call("Risk Warnings")
                
                # Verify metrics were called
                assert mock_streamlit['metric'].call_count >= 4  # At least 4 risk metrics
    
    def test_display_risk_metrics_no_warnings(self, mock_streamlit):
        """Test risk metrics with no risk warnings."""
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
                # Use account with low risk metrics
                low_risk_account = {
                    'portfolio_value': 100000.0,
                    'initial_margin': 10000.0,  # 10% margin utilization
                    'maintenance_margin': 5000.0,
                    'pattern_day_trader': False,
                    'trading_blocked': False
                }
                
                # Use 10 positions, each with $10,000 market value (10% each)
                low_concentration_positions = [
                    {
                        'symbol': f'SYM{i}',
                        'qty': 100,
                        'side': 'long',
                        'current_price': 100.0,
                        'cost_basis': 90.0,
                        'market_value': 10000.0,
                        'unrealized_pl': 1000.0,
                        'unrealized_plpc': 0.1
                    } for i in range(10)
                ]
                
                portfolio_module.display_risk_metrics(low_risk_account, low_concentration_positions)
                
                # Verify success message was shown
                mock_streamlit['success'].assert_called_with("✅ No significant risk warnings detected")
    
    def test_display_risk_metrics_logic_direct(self, mock_streamlit):
        """Test risk metrics logic directly without importing the module."""
        # Mock the PortfolioManager import
        with patch('src.data.sources.portfolio_manager.PortfolioManager'):
            # Import the function directly
            import importlib.util
            spec = importlib.util.spec_from_file_location("portfolio", "src/ui/portfolio.py")
            portfolio_module = importlib.util.module_from_spec(spec)
            
            # Mock the PortfolioManager before executing the module
            portfolio_module.PortfolioManager = Mock()
            spec.loader.exec_module(portfolio_module)
            
            # Test the function with data that should trigger no warnings
            low_risk_account = {
                'portfolio_value': 100000.0,
                'initial_margin': 10000.0,  # 10% margin utilization
                'maintenance_margin': 5000.0,
                'pattern_day_trader': False,
                'trading_blocked': False
            }
            
            # Use 10 positions, each with $10,000 market value (10% each)
            low_concentration_positions = [
                {
                    'symbol': f'SYM{i}',
                    'qty': 100,
                    'side': 'long',
                    'current_price': 100.0,
                    'cost_basis': 90.0,
                    'market_value': 10000.0,
                    'unrealized_pl': 1000.0,
                    'unrealized_plpc': 0.1
                } for i in range(10)
            ]
            
            # Call the function
            portfolio_module.display_risk_metrics(low_risk_account, low_concentration_positions)
            
            # Verify the success message was called
            mock_streamlit['success'].assert_called_with("✅ No significant risk warnings detected")
            
            # Verify subheaders were called
            mock_streamlit['subheader'].assert_any_call("⚠️ Risk Analysis")
            mock_streamlit['subheader'].assert_any_call("Risk Warnings")
            
            # Verify metrics were called
            assert mock_streamlit['metric'].call_count >= 4  # At least 4 risk metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 