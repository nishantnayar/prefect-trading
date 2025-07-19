"""
Trading System - Main Application (Modular Version)

A clean, modern Streamlit application for trading analysis and portfolio management.
"""

import streamlit as st
import os
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import our data and database modules
from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.portfolio_manager import PortfolioManager
from src.data.sources.symbol_manager import SymbolManager

# Import modular UI components
from src.ui.components.company_info import render_company_info
from src.ui.components.market_data import render_market_data
from src.ui.components.symbol_selector import render_symbol_selector
from src.ui.components.testing_results import render_testing_results

# Page configuration
st.set_page_config(
    page_title="Trading System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'
if 'selected_symbol' not in st.session_state:
    st.session_state.selected_symbol = None
if 'test_results' not in st.session_state:
    st.session_state.test_results = None


def main():
    """Main application entry point."""
    
    # Load custom CSS
    with open('config/streamlit_style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.title("📈 Trading System")
        st.divider()
        
        # Navigation menu
        page = st.selectbox(
            "Navigation",
            options=['Dashboard', 'Analysis', 'Portfolio', 'Models', 'Testing'],
            index=['Dashboard', 'Analysis', 'Portfolio', 'Models', 'Testing'].index(st.session_state.current_page)
        )
        
        # Update current page
        if page != st.session_state.current_page:
            st.session_state.current_page = page
            st.rerun()
        
        st.divider()
        
        # Refresh button
        if st.button("🔄 Refresh All Data", type="primary"):
            # Clear session state and rerun
            for key in list(st.session_state.keys()):
                if key not in ['current_page', 'selected_symbol', 'test_results', 'test_category', 'test_timestamp']:
                    del st.session_state[key]
            st.rerun()
        
        st.caption("💡 Click refresh to update all data")
    
    # Main content area
    if st.session_state.current_page == 'Dashboard':
        render_dashboard()
    elif st.session_state.current_page == 'Analysis':
        render_analysis()
    elif st.session_state.current_page == 'Portfolio':
        render_portfolio()
    elif st.session_state.current_page == 'Models':
        render_models()
    elif st.session_state.current_page == 'Testing':
        render_testing_results()


def render_dashboard():
    """Render the main dashboard page."""
    st.markdown('<h1 class="main-header">🏠 Trading Dashboard</h1>', unsafe_allow_html=True)
    
    # Get current time
    from datetime import datetime
    from pytz import timezone
    current_time = datetime.now(timezone('US/Central')).strftime('%B %d, %Y at %I:%M %p')
    st.write(f"**Last updated:** {current_time}")
    
    # Portfolio summary
    st.subheader("📊 Portfolio Overview")
    
    try:
        portfolio_manager = PortfolioManager()
        portfolio_summary = portfolio_manager.get_portfolio_summary()
        
        if portfolio_summary:
            metrics = portfolio_summary.get('metrics', {})
            
            # Key metrics in a clean layout
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_value = metrics.get('total_value', 0)
                st.metric("Total Value", f"${total_value:,.2f}")
            
            with col2:
                daily_pnl = metrics.get('daily_pnl', 0)
                st.metric("Daily P&L", f"${daily_pnl:,.2f}")
            
            with col3:
                total_positions = metrics.get('total_positions', 0)
                st.metric("Open Positions", str(total_positions))
            
            with col4:
                win_rate = metrics.get('win_rate', 0)
                st.metric("Win Rate", f"{win_rate:.1f}%")
        
        else:
            st.info("No portfolio data available")
    
    except Exception as e:
        st.error(f"Error loading portfolio data: {str(e)}")
    
    # Market overview
    st.subheader("🌍 Market Overview")
    
    # Simple market data display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Major Indices**")
        st.metric("S&P 500", "4,783.45", "+0.8%")
        st.metric("NASDAQ", "16,742.38", "+1.2%")
    
    with col2:
        st.write("**Tech Leaders**")
        st.metric("AAPL", "185.92", "+1.5%")
        st.metric("MSFT", "374.58", "+2.1%")
    
    with col3:
        st.write("**Market Status**")
        st.success("🟢 Market Open")
        st.info("📈 Bullish Trend")


def render_analysis():
    """Render the symbol analysis page."""
    st.markdown('<h1 class="main-header">📊 Symbol Analysis</h1>', unsafe_allow_html=True)
    
    # Use modular symbol selector
    selected_symbol = render_symbol_selector()
    
    if selected_symbol:
        display_symbol_analysis(selected_symbol)


def display_symbol_analysis(symbol):
    """Display analysis for a selected symbol."""
    st.markdown(f'<h2 class="main-header">📈 Analysis for {symbol}</h2>', unsafe_allow_html=True)
    
    # Use modular components
    render_company_info(symbol)
    render_market_data(symbol)


def render_portfolio():
    """Render the portfolio management page."""
    st.markdown('<h1 class="main-header">💼 Portfolio Management</h1>', unsafe_allow_html=True)
    
    st.info("Portfolio management features coming soon!")
    st.write("This page will include:")
    st.write("- Position management")
    st.write("- Order history")
    st.write("- Performance analytics")
    st.write("- Risk management tools")


def render_models():
    """Render the model performance page."""
    st.markdown('<h1 class="main-header">🤖 Model Performance</h1>', unsafe_allow_html=True)
    
    st.info("Model performance features coming soon!")
    st.write("This page will include:")
    st.write("- Model rankings")
    st.write("- Performance metrics")
    st.write("- Training history")
    st.write("- MLflow integration")


if __name__ == "__main__":
    main() 