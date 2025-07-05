#!/usr/bin/env python3
"""
Comprehensive tests for the enhanced symbol selector component.

Robust Mocking/Testing Approach for Streamlit UI Functions with Database Context Managers
========================================================================================

**Rationale:**
- Streamlit UI functions often depend on database access via context managers (e.g., `with db.get_session() as cursor:`).
- Directly testing these functions can be difficult due to the need for a real database and UI rendering.
- To enable isolated, robust tests, we use `unittest.mock.patch` to mock all external dependencies:
    - Patch database and symbol manager classes at the correct import path.
    - Use `MagicMock` to mock context managers (supporting `__enter__`/`__exit__`).
    - Patch Streamlit UI functions (`st.subheader`, `st.columns`, `st.metric`, etc.) to prevent real UI calls and allow assertions.
- This approach allows us to test the logic and integration of UI functions without requiring any production code changes or real database connections.

**Example (for display_symbol_overview_with_db):**

    @patch('src.ui.components.symbol_selector.DatabaseConnectivity')
    @patch('src.ui.components.symbol_selector.SymbolManager')
    @patch('src.ui.components.symbol_selector.st.subheader')
    @patch('src.ui.components.symbol_selector.st.columns')
    @patch('src.ui.components.symbol_selector.st.metric')
    @patch('src.ui.components.symbol_selector.st.error')
    def test_display_symbol_overview_robust(
        mock_error, mock_metric, mock_columns, mock_subheader,
        mock_symbol_manager, mock_db_connectivity
    ):
        # Setup DB and cursor mocks
        mock_db = Mock()
        mock_cursor = MagicMock()
        mock_db_connectivity.return_value = mock_db
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_cursor
        mock_session.__exit__.return_value = None
        mock_db.get_session.return_value = mock_session

        # Setup SymbolManager mock
        mock_symbol_info = {...}
        mock_manager = Mock()
        mock_manager.get_symbol_info.return_value = mock_symbol_info
        mock_symbol_manager.return_value = mock_manager

        # Setup market data summary
        mock_cursor.fetchone.return_value = (...)

        # Setup columns mock to return context managers
        ...

        # Call the function
        from src.ui.components.symbol_selector import display_symbol_overview_with_db
        display_symbol_overview_with_db('AAPL')

        # Assertions
        mock_subheader.assert_any_call('📊 AAPL Overview')
        assert mock_metric.call_count > 0
        mock_columns.assert_called()

Apply this pattern to all tests that require database or UI mocking for robust, isolated testing.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.ui.components.symbol_selector import (
    display_symbol_selector,
    display_symbol_analysis,
    display_symbol_overview,
    display_market_data_analysis,
    display_company_info,
    display_symbol_news,
    display_symbol_selector_with_analysis
)


class TestSymbolSelector:
    """Test the basic symbol selector functionality."""
    
    @patch('src.ui.components.symbol_selector.SymbolManager')
    @patch('src.ui.components.symbol_selector.st.selectbox')
    def test_display_symbol_selector_success(self, mock_selectbox, mock_symbol_manager):
        """Test successful symbol selector display."""
        # Mock SymbolManager
        mock_manager = Mock()
        mock_manager.get_active_symbols.return_value = ['AAPL', 'MSFT', 'GOOGL']
        mock_symbol_manager.return_value = mock_manager
        
        # Mock selectbox
        mock_selectbox.return_value = 'AAPL'
        
        # Import and call the function
        from src.ui.components.symbol_selector import display_symbol_selector
        result = display_symbol_selector()
        
        # Assertions
        assert result == 'AAPL'
        mock_manager.get_active_symbols.assert_called_once()
        mock_selectbox.assert_called_once()
    
    @patch('src.ui.components.symbol_selector.SymbolManager')
    @patch('src.ui.components.symbol_selector.st.warning')
    def test_display_symbol_selector_no_symbols(self, mock_warning, mock_symbol_manager):
        """Test symbol selector with no active symbols."""
        # Mock SymbolManager
        mock_manager = Mock()
        mock_manager.get_active_symbols.return_value = []
        mock_symbol_manager.return_value = mock_manager
        
        # Import and call the function
        from src.ui.components.symbol_selector import display_symbol_selector
        result = display_symbol_selector()
        
        # Assertions
        assert result is None
        mock_warning.assert_called_once_with("No active symbols found")
    
    @patch('src.ui.components.symbol_selector.SymbolManager')
    @patch('src.ui.components.symbol_selector.st.error')
    def test_display_symbol_selector_error(self, mock_error, mock_symbol_manager):
        """Test symbol selector with error."""
        # Mock SymbolManager to raise exception
        mock_symbol_manager.side_effect = Exception("Database error")
        
        # Import and call the function
        from src.ui.components.symbol_selector import display_symbol_selector
        result = display_symbol_selector()
        
        # Assertions
        assert result is None
        mock_error.assert_called_once()


# Standalone robust test for display_symbol_overview_with_db
@patch('src.ui.components.symbol_selector.DatabaseConnectivity')
@patch('src.ui.components.symbol_selector.SymbolManager')
@patch('src.ui.components.symbol_selector.st.subheader')
@patch('src.ui.components.symbol_selector.st.columns')
@patch('src.ui.components.symbol_selector.st.metric')
@patch('src.ui.components.symbol_selector.st.error')
def test_display_symbol_overview_robust(
    mock_error, mock_metric, mock_columns, mock_subheader,
    mock_symbol_manager, mock_db_connectivity
):
    """Robust test for display_symbol_overview_with_db using only mocks."""
    # Setup DB and cursor mocks
    mock_db = Mock()
    mock_cursor = MagicMock()
    mock_db_connectivity.return_value = mock_db
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_cursor
    mock_session.__exit__.return_value = None
    mock_db.get_session.return_value = mock_session

    # Setup SymbolManager mock
    mock_symbol_info = {
        'symbol': 'AAPL',
        'name': 'Apple Inc.',
        'is_active': True,
        'start_date': datetime(2023, 1, 1),
        'end_date': None,
        'updated_at': datetime(2023, 12, 1)
    }
    mock_manager = Mock()
    mock_manager.get_symbol_info.return_value = mock_symbol_info
    mock_symbol_manager.return_value = mock_manager

    # Setup market data summary
    mock_cursor.fetchone.return_value = (
        1000, datetime(2023, 1, 1), datetime(2023, 12, 1),
        150.0, 200.0, 100.0, 5000000
    )

    # Setup columns mock to return context managers
    mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
    mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
    for col in [mock_col1, mock_col2, mock_col3]:
        col.__enter__.return_value = col
        col.__exit__.return_value = None

    # Import and call the function with database connection
    from src.ui.components.symbol_selector import display_symbol_overview_with_db
    display_symbol_overview_with_db('AAPL')

    # Assertions
    mock_subheader.assert_any_call('📊 AAPL Overview')
    assert mock_metric.call_count > 0
    mock_columns.assert_called()


class TestMarketDataAnalysis:
    """Test the market data analysis functionality."""

    @patch('src.ui.components.symbol_selector.DatabaseConnectivity')
    @patch('src.ui.components.symbol_selector.st.subheader')
    @patch('src.ui.components.symbol_selector.st.dataframe')
    @patch('src.ui.components.symbol_selector.st.columns')
    @patch('src.ui.components.symbol_selector.st.metric')
    @patch('src.ui.components.symbol_selector.st.line_chart')
    def test_display_market_data_analysis_success(
        self, mock_line_chart, mock_metric, mock_columns, mock_dataframe, mock_subheader, mock_db_connectivity
    ):
        """Test successful market data analysis display."""
        # Mock database
        mock_db = Mock()
        mock_cursor = MagicMock()
        mock_db_connectivity.return_value = mock_db

        # Correct context manager mocking
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_cursor
        mock_session.__exit__.return_value = None
        mock_db.get_session.return_value = mock_session

        # Mock market data
        mock_data = [
            (datetime(2023, 12, 1, 9, 30), 150.0, 155.0, 149.0, 152.0, 1000000),
            (datetime(2023, 12, 1, 9, 31), 152.0, 156.0, 151.0, 154.0, 1200000),
        ]
        mock_cursor.fetchall.return_value = mock_data

        # Mock columns
        mock_columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]

        # Import and call the function
        from src.ui.components.symbol_selector import display_market_data_analysis
        display_market_data_analysis('AAPL')

        # Assertions
        mock_subheader.assert_any_call("📈 AAPL Market Data Analysis")
        mock_dataframe.assert_called()
        assert mock_metric.call_count > 0
        mock_line_chart.assert_called()

    @patch('src.ui.components.symbol_selector.DatabaseConnectivity')
    @patch('src.ui.components.symbol_selector.st.warning')
    def test_display_market_data_analysis_no_data(self, mock_warning, mock_db_connectivity):
        """Test market data analysis with no data."""
        # Mock database
        mock_db = Mock()
        mock_cursor = MagicMock()
        mock_db_connectivity.return_value = mock_db

        # Correct context manager mocking
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_cursor
        mock_session.__exit__.return_value = None
        mock_db.get_session.return_value = mock_session

        # Mock no data
        mock_cursor.fetchall.return_value = []

        # Import and call the function
        from src.ui.components.symbol_selector import display_market_data_analysis
        display_market_data_analysis('AAPL')

        # Assertions
        mock_warning.assert_called_once_with("No market data available for this symbol")


class TestCompanyInfo:
    """Test the company information functionality."""

    @patch('src.ui.components.symbol_selector.DatabaseConnectivity')
    @patch('src.ui.components.symbol_selector.st.subheader')
    @patch('src.ui.components.symbol_selector.st.write')
    @patch('src.ui.components.symbol_selector.st.columns')
    @patch('src.ui.components.symbol_selector.st.dataframe')
    def test_display_company_info_success(self, mock_dataframe, mock_columns, mock_write, mock_subheader, mock_db_connectivity):
        """Test successful company info display."""
        # Mock database
        mock_db = Mock()
        mock_cursor = MagicMock()
        mock_db_connectivity.return_value = mock_db

        # Correct context manager mocking
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_cursor
        mock_session.__exit__.return_value = None
        mock_db.get_session.return_value = mock_session

        # Mock company info
        mock_company_info = (
            'Apple Inc.',  # longName
            'Technology',  # sector
            'Consumer Electronics',  # industry
            3000000000000,  # marketCap
            150.0,  # currentPrice
            200.0,  # fiftyTwoWeekHigh
            100.0,  # fiftyTwoWeekLow
            5000000,  # averageVolume
            25.0,  # trailingPE
            23.0,  # forwardPE
            0.005,  # dividendYield
            1.2,  # beta
            'https://www.apple.com',  # website
            'Apple Inc. designs, manufactures, and markets smartphones...'  # longBusinessSummary
        )
        mock_cursor.fetchone.return_value = mock_company_info

        # Mock officers data
        mock_officers = [
            ('Tim Cook', 'CEO', 62, 100000000),
            ('Jeff Williams', 'COO', 60, 50000000)
        ]
        mock_cursor.fetchall.return_value = mock_officers

        # Mock columns
        mock_columns.return_value = [MagicMock(), MagicMock()]

        # Import and call the function
        from src.ui.components.symbol_selector import display_company_info
        display_company_info('AAPL')

        # Assertions
        mock_subheader.assert_called()
        assert mock_write.call_count > 0
        mock_dataframe.assert_called()

    @patch('src.ui.components.symbol_selector.DatabaseConnectivity')
    @patch('src.ui.components.symbol_selector.st.warning')
    def test_display_company_info_no_data(self, mock_warning, mock_db_connectivity):
        """Test company info with no data."""
        # Mock database
        mock_db = Mock()
        mock_cursor = MagicMock()
        mock_db_connectivity.return_value = mock_db

        # Correct context manager mocking
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_cursor
        mock_session.__exit__.return_value = None
        mock_db.get_session.return_value = mock_session

        # Mock no company info
        mock_cursor.fetchone.return_value = None

        # Import and call the function
        from src.ui.components.symbol_selector import display_company_info
        display_company_info('AAPL')

        # Assertions
        mock_warning.assert_called_once_with("No company information available for this symbol")


class TestSymbolNews:
    """Test the symbol news functionality."""
    
    @patch('src.ui.components.symbol_selector.DatabaseConnectivity')
    @patch('src.ui.components.symbol_selector.st.subheader')
    @patch('src.ui.components.symbol_selector.st.expander')
    @patch('src.ui.components.symbol_selector.st.write')
    def test_display_symbol_news_success(self, mock_write, mock_expander, mock_subheader, mock_db_connectivity):
        """Test successful symbol news display."""
        # Mock database
        mock_db = Mock()
        mock_cursor = MagicMock()
        mock_db_connectivity.return_value = mock_db
        
        # Correct context manager mocking
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_cursor
        mock_session.__exit__.return_value = None
        mock_db.get_session.return_value = mock_session
        
        # Mock news data
        mock_news = [
            ('Apple Stock Rises on Strong Earnings', 'Reuters', 'https://example.com', 
             datetime(2023, 12, 1, 10, 0), 'Apple reported strong quarterly earnings...'),
            ('Apple Announces New iPhone', 'Bloomberg', 'https://example2.com', 
             datetime(2023, 12, 1, 9, 0), 'Apple unveiled its latest iPhone model...')
        ]
        mock_cursor.fetchall.return_value = mock_news
        
        # Mock expander context manager
        mock_expander_context = MagicMock()
        mock_expander.return_value.__enter__.return_value = mock_expander_context
        mock_expander.return_value.__exit__.return_value = None
        
        # Import and call the function
        from src.ui.components.symbol_selector import display_symbol_news
        display_symbol_news('AAPL')
        
        # Assertions
        mock_subheader.assert_called()
        mock_expander.assert_called()
        assert mock_write.call_count > 0
    
    @patch('src.ui.components.symbol_selector.DatabaseConnectivity')
    @patch('src.ui.components.symbol_selector.st.info')
    def test_display_symbol_news_no_news(self, mock_info, mock_db_connectivity):
        """Test symbol news with no news."""
        # Mock database
        mock_db = Mock()
        mock_cursor = MagicMock()
        mock_db_connectivity.return_value = mock_db
        
        # Correct context manager mocking
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_cursor
        mock_session.__exit__.return_value = None
        mock_db.get_session.return_value = mock_session
        
        # Mock no news
        mock_cursor.fetchall.return_value = []
        
        # Import and call the function
        from src.ui.components.symbol_selector import display_symbol_news
        display_symbol_news('AAPL')
        
        # Assertions
        mock_info.assert_called_once_with("No recent news found for this symbol")


class TestSymbolAnalysis:
    """Test the main symbol analysis functionality."""

    @patch('src.ui.components.symbol_selector.display_symbol_selector')
    @patch('src.ui.components.symbol_selector.display_symbol_analysis')
    @patch('src.ui.components.symbol_selector.st.header')
    def test_display_symbol_selector_with_analysis_success(self, mock_header, mock_display_analysis, mock_display_selector):
        """Test successful symbol selector with analysis."""
        # Mock symbol selector
        mock_display_selector.return_value = 'AAPL'

        # Import and call the function
        from src.ui.components.symbol_selector import display_symbol_selector_with_analysis
        result = display_symbol_selector_with_analysis()

        # Assertions
        assert result == 'AAPL'
        mock_header.assert_called_once_with("🔍 Symbol Analysis")
        mock_display_selector.assert_called_once()
        mock_display_analysis.assert_called_once_with('AAPL')

    @patch('src.ui.components.symbol_selector.display_symbol_selector')
    @patch('src.ui.components.symbol_selector.display_symbol_analysis')
    @patch('src.ui.components.symbol_selector.st.header')
    def test_display_symbol_selector_with_analysis_no_selection(self, mock_header, mock_display_analysis, mock_display_selector):
        """Test symbol selector with analysis when no symbol is selected."""
        # Mock symbol selector
        mock_display_selector.return_value = None

        # Import and call the function
        from src.ui.components.symbol_selector import display_symbol_selector_with_analysis
        result = display_symbol_selector_with_analysis()

        # Assertions
        assert result is None
        mock_header.assert_called_once_with("🔍 Symbol Analysis")
        mock_display_selector.assert_called_once()
        mock_display_analysis.assert_not_called()


class TestSymbolAnalysisIntegration:
    """Integration tests for symbol analysis."""

    @patch('src.ui.components.symbol_selector.st.tabs')
    @patch('src.ui.components.symbol_selector.display_symbol_overview')
    @patch('src.ui.components.symbol_selector.display_market_data_analysis')
    @patch('src.ui.components.symbol_selector.display_company_info')
    @patch('src.ui.components.symbol_selector.display_symbol_news')
    def test_display_symbol_analysis_integration(self, mock_news, mock_company, mock_market, mock_overview, mock_tabs):
        """Test the integration of all symbol analysis components."""
        # Mock tabs
        mock_tab1, mock_tab2, mock_tab3, mock_tab4 = MagicMock(), MagicMock(), MagicMock(), MagicMock()
        mock_tabs.return_value = [mock_tab1, mock_tab2, mock_tab3, mock_tab4]

        # Mock tab context managers
        for tab in [mock_tab1, mock_tab2, mock_tab3, mock_tab4]:
            tab.__enter__ = Mock(return_value=tab)
            tab.__exit__ = Mock(return_value=None)

        # Import and call the function
        from src.ui.components.symbol_selector import display_symbol_analysis
        display_symbol_analysis('AAPL')

        # Assertions
        mock_tabs.assert_called_once_with(["📊 Overview", "📈 Market Data", "🏢 Company Info", "📰 News"])
        mock_overview.assert_called_once_with('AAPL')
        mock_market.assert_called_once_with('AAPL')
        mock_company.assert_called_once_with('AAPL')
        mock_news.assert_called_once_with('AAPL')

    @patch('src.ui.components.symbol_selector.st.warning')
    def test_display_symbol_analysis_no_symbol(self, mock_warning):
        """Test symbol analysis with no symbol provided."""
        # Import and call the function
        from src.ui.components.symbol_selector import display_symbol_analysis
        display_symbol_analysis('')

        # Assertions
        mock_warning.assert_called_once_with("Please select a symbol to analyze")

    @patch('src.ui.components.symbol_selector.st.error')
    def test_display_symbol_analysis_error(self, mock_error):
        """Test symbol analysis with error."""
        # Mock tabs to raise exception
        with patch('src.ui.components.symbol_selector.st.tabs', side_effect=Exception("UI error")):
            # Import and call the function
            from src.ui.components.symbol_selector import display_symbol_analysis
            display_symbol_analysis('AAPL')

            # Assertions
            mock_error.assert_called_once_with("Error loading symbol analysis. Please try again later.")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 