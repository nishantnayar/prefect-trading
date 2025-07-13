"""
Trading Dashboard Home Page

This module provides the main trading dashboard interface with optimized layouts
for displaying market information, portfolio status, and trading tools.

The dashboard is designed to be space-efficient while maintaining readability
and providing quick access to essential trading information.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone
from src.ui.components.symbol_selector import display_symbol_selector, display_sector_selector
from src.ui.components.date_display import get_current_cst_formatted, format_datetime_est_to_cst
from src.ui.components.market_status import display_market_status
from src.database.database_connectivity import DatabaseConnectivity
from src.data.sources.portfolio_manager import PortfolioManager
from src.utils.data_recycler_utils import get_latest_price

# Load environment variables
load_dotenv('config/.env', override=True)

# Shared portfolio manager instance
_portfolio_manager = None

def get_portfolio_manager():
    """Get or create a shared portfolio manager instance."""
    global _portfolio_manager
    if _portfolio_manager is None:
        _portfolio_manager = PortfolioManager()
    return _portfolio_manager

def clear_portfolio_manager():
    """Clear the shared portfolio manager instance (useful for refresh)."""
    global _portfolio_manager
    if _portfolio_manager is not None:
        _portfolio_manager.clear_cache()
    _portfolio_manager = None

def get_greeting() -> str:
    """Get appropriate greeting based on time of day.
    
    Returns:
        str: Greeting message based on current time
    """
    current_hour = datetime.now(timezone('US/Central')).hour

    if 5 <= current_hour < 12:
        return "Good Morning"
    elif 12 <= current_hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"


def display_header(user_name: str):
    """Display the optimized header section with greeting, time, and market status.
    
    The header is organized in three columns for efficient space usage:
    - Left: Dashboard title and greeting
    - Middle: Current time
    - Right: Market status
    
    Args:
        user_name: Name of the current user
    """
    greeting = get_greeting()
    
    # Create a more compact header with three columns
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🏠 Trading Dashboard")
        st.write(f"{greeting}, {user_name}!")
    
    with col2:
        st.write(f"🕒 {get_current_cst_formatted()}")
    
    with col3:
        display_market_status()


def display_portfolio_summary():
    """Display an optimized portfolio summary section with real Alpaca data.
    
    Shows key metrics in a single row with additional metrics in an expander:
    - Primary metrics: Total Value, Daily P&L, Open Positions, Win Rate
    - Secondary metrics (in expander): Avg. Trade, Risk/Reward, Max Drawdown, Pending Orders
    """
    st.subheader("📊 Portfolio Overview")
    
    try:
        # Get real portfolio data
        portfolio_manager = get_portfolio_manager()
        portfolio_summary = portfolio_manager.get_portfolio_summary()
        
        if not portfolio_summary:
            st.error("Unable to fetch portfolio data")
            return
        
        metrics = portfolio_summary.get('metrics', {})
        positions = portfolio_summary.get('positions', [])
        
        # Format metrics for display
        total_value = metrics.get('total_value', 0)
        daily_pnl = metrics.get('daily_pnl', 0)
        total_positions = metrics.get('total_positions', 0)
        win_rate = metrics.get('win_rate', 0)
        
        # Calculate daily P&L percentage
        daily_pnl_pct = (daily_pnl / total_value * 100) if total_value > 0 else 0
        
        # Create a single row of key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Value", 
                f"${total_value:,.2f}", 
                f"{daily_pnl_pct:+.2f}%", 
                delta_color="normal" if daily_pnl_pct >= 0 else "inverse"
            )
        with col2:
            st.metric(
                "Daily P&L", 
                f"${daily_pnl:,.2f}", 
                f"{daily_pnl_pct:+.2f}%", 
                delta_color="normal" if daily_pnl >= 0 else "inverse"
            )
        with col3:
            st.metric(
                "Open Positions", 
                str(total_positions), 
                help="Number of current positions"
            )
        with col4:
            st.metric(
                "Win Rate", 
                f"{win_rate:.1f}%", 
                help="Percentage of profitable trades"
            )
        
        # Add a small expander for additional metrics
        with st.expander("Additional Metrics"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_trade_size = metrics.get('avg_trade_size', 0)
                st.metric(
                    "Avg. Trade", 
                    f"${avg_trade_size:,.2f}", 
                    help="Average trade size"
                )
            with col2:
                margin_ratio = metrics.get('margin_ratio', 0)
                st.metric(
                    "Margin Used", 
                    f"{margin_ratio:.1f}%", 
                    help="Percentage of portfolio using margin"
                )
            with col3:
                buying_power = metrics.get('buying_power', 0)
                st.metric(
                    "Buying Power", 
                    f"${buying_power:,.2f}", 
                    help="Available buying power"
                )
            with col4:
                # Get pending orders
                orders = portfolio_manager.get_orders("open")
                pending_orders = len(orders)
                st.metric(
                    "Pending Orders", 
                    str(pending_orders), 
                    help="Number of open orders"
                )
    
    except Exception as e:
        st.error(f"Error loading portfolio data: {str(e)}")
        # Fallback to dummy data if there's an error
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Value", "$125,432.89", "+2.3%", delta_color="normal")
        with col2:
            st.metric("Daily P&L", "$1,234.56", "+1.2%", delta_color="normal")
        with col3:
            st.metric("Open Positions", "12", "-2", delta_color="inverse")
        with col4:
            st.metric("Win Rate", "68%", "+2%", delta_color="normal")


def display_market_overview():
    """Display a comprehensive market overview section.
    
    Shows market information in three columns:
    - Major Indices: S&P 500, NASDAQ, DOW
    - Tech Leaders: AAPL, MSFT, GOOGL
    - Market Breadth: Advancers, Decliners, New Highs
    """
    st.subheader("🌍 Market Overview")
    
    # Create three columns for different market segments
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Major Indices**")
        st.metric("S&P 500", "4,783.45", "+0.8%", delta_color="normal")
        st.metric("NASDAQ", "16,742.38", "+1.2%", delta_color="normal")
        st.metric("DOW", "37,305.16", "+0.5%", delta_color="normal")
    
    with col2:
        st.write("**Tech Leaders**")
        st.metric("AAPL", "185.92", "+1.5%", delta_color="normal")
        st.metric("MSFT", "374.58", "+2.1%", delta_color="normal")
        st.metric("GOOGL", "140.93", "+0.9%", delta_color="normal")
    
    with col3:
        st.write("**Market Breadth**")
        st.metric("Advancers", "2,345", "+156", delta_color="normal")
        st.metric("Decliners", "1,234", "-89", delta_color="normal")
        st.metric("New Highs", "45", "+12", delta_color="normal")


def display_recent_activity():
    """Display recent trading activity in a structured format with real data.
    
    Shows recent trades with:
    - Action type (Buy/Sell/Limit)
    - Symbol and shares
    - Price
    - Time
    """
    st.subheader("📝 Recent Activity")
    
    try:
        # Get real trading activity
        portfolio_manager = get_portfolio_manager()
        recent_orders = portfolio_manager.get_orders("closed")[:5]  # Last 5 orders
        
        if not recent_orders:
            st.info("No recent trading activity found.")
            return
        
        # Format recent activity
        for order in recent_orders:
            if order.get('filled_at'):
                col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
                with col1:
                    st.write(f"**{order['side'].upper()}**")
                with col2:
                    st.write(f"{order['symbol']} ({order['filled_qty']} shares)")
                with col3:
                    st.write(f"@ ${order['filled_avg_price']:.2f}")
                with col4:
                    time_str = order['filled_at'].strftime('%I:%M %p') if order['filled_at'] else 'N/A'
                    st.write(time_str)
    
    except Exception as e:
        st.error(f"Error loading recent activity: {str(e)}")
        # Fallback to dummy data
        activities = [
            {"action": "Buy", "symbol": "AAPL", "shares": 100, "price": 185.50, "time": "10:15 AM"},
            {"action": "Sell", "symbol": "MSFT", "shares": 50, "price": 374.20, "time": "10:30 AM"},
            {"action": "Limit", "symbol": "GOOGL", "shares": 75, "price": 140.00, "time": "10:45 AM"}
        ]
        
        for activity in activities:
            col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
            with col1:
                st.write(f"**{activity['action']}**")
            with col2:
                st.write(f"{activity['symbol']} ({activity['shares']} shares)")
            with col3:
                st.write(f"@ ${activity['price']:.2f}")
            with col4:
                st.write(f"{activity['time']}")


def display_quick_actions():
    """Display quick action buttons in a compact grid layout.
    
    Shows common trading actions with icons and descriptions:
    - New Trade
    - Market Scan
    - Risk Analysis
    - Reports
    """
    st.subheader("⚡ Quick Actions")
    
    # Create a grid of action buttons with descriptions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 New Trade", use_container_width=True):
            st.info("New trade functionality coming soon!")
        st.caption("Open a new trading position")
        
        if st.button("🔍 Market Scan", use_container_width=True):
            st.info("Market scan functionality coming soon!")
        st.caption("Scan for trading opportunities")
    
    with col2:
        if st.button("📊 Risk Analysis", use_container_width=True):
            st.info("Risk analysis functionality coming soon!")
        st.caption("Analyze portfolio risk")
        
        if st.button("📑 Reports", use_container_width=True):
            st.info("Reports functionality coming soon!")
        st.caption("View detailed reports")


def display_market_news():
    """Display market news in a compact, expandable format.
    
    Shows the 3 most recent news articles from the database with:
    - Title (as expander header)
    - Source and publication time
    - Truncated description
    - Link to full article
    """
    st.subheader("📰 Market News")
    
    try:
        db = DatabaseConnectivity()
        with db.get_session() as cursor:
            # Fetch the 3 most recent news articles
            query = """
                SELECT title, source_name, url, published_at, description
                FROM news_articles
                ORDER BY published_at DESC
                LIMIT 3
            """
            cursor.execute(query)
            articles = cursor.fetchall()
            
            if not articles:
                st.info("No recent news articles available.")
                return
            
            # Create a more compact news display
            for article in articles:
                title, source, url, published_at, description = article
                
                # Format the published date
                published_str = format_datetime_est_to_cst(published_at) if published_at else "Unknown date"
                
                # Create a container with expander for each article
                with st.expander(f"**{title}**"):
                    st.markdown(f"*{source} • {published_str}*")
                    if description:
                        st.markdown(f"{description[:150]}...")  # Shorter description
                    st.markdown(f"[Read full article]({url})")
    
    except Exception as e:
        st.error("Error fetching news articles. Please try again later.")
        st.error(str(e))


def display_open_orders():
    """Display open (accepted) orders in a structured format."""
    st.subheader("🟢 Open Orders")
    try:
        portfolio_manager = get_portfolio_manager()
        open_orders = portfolio_manager.get_orders("open")
        if not open_orders:
            st.info("No open orders found.")
            return
        for order in open_orders:
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
            with col1:
                st.write(f"**{order['symbol']}**")
            with col2:
                st.write(f"{order['side'].upper()}")
            with col3:
                st.write(f"{order['qty']} shares")
            with col4:
                price = order.get('limit_price') or order.get('filled_avg_price') or 0
                st.write(f"@ ${price:.2f}")
            with col5:
                st.write(f"Status: {order['status'].capitalize()}")
    except Exception as e:
        st.error(f"Error loading open orders: {str(e)}")


def render_home():
    """Main function to render the optimized home page.
    
    The page is organized into several sections:
    1. Header with greeting and market status
    2. Portfolio summary with key metrics
    3. Two-column layout for:
       - Market overview and recent activity
       - Quick actions and market news
    4. Symbol analysis section with detailed metrics
    """
    user_name = os.getenv("USER_NAME", "Trader")
    
    # Display header with greeting and market status
    display_header(user_name)
    
    # Display portfolio summary
    display_portfolio_summary()
    
    st.divider()
    
    # Create two columns for main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Market Overview
        display_market_overview()
        st.divider()
        # Recent Activity
        display_recent_activity()
        st.divider()
        # Open Orders
        display_open_orders()
    
    with col2:
        # Quick Actions
        display_quick_actions()
        st.divider()
        # Market News
        display_market_news()
    
    st.divider()
    
    # Symbol Selection and Analysis
    st.subheader("📊 Symbol Analysis")
    
    # Add sector selection
    selected_sectors = display_sector_selector()
    
    # Symbol selection with sector filtering
    selected_symbol = display_symbol_selector(sectors=selected_sectors)
    if selected_symbol:
        st.session_state.selected_symbol = selected_symbol
        
        # Show selected symbol info
        st.success(f"✅ Selected: **{selected_symbol}** - Use the Analysis page for detailed analysis")
        
        # Get dynamic current price
        price, price_source = get_latest_price(selected_symbol)
        price_display = f"${price:.2f}" if price is not None else "N/A"
        price_caption = f"(from {'Real-Time' if price_source == 'market_data' else 'Historical' if price_source == 'market_data_historical' else 'Unknown'})"
        
        # Create columns for symbol details
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Price", price_display, help=price_caption)
        with col2:
            st.metric("Volume", "45.2M", "+12%")
        with col3:
            st.metric("Market Cap", "$2.9T", "0%")
