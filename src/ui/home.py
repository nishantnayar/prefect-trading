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
from src.ui.components.symbol_selector import display_symbol_selector
from src.ui.components.date_display import get_current_cst_formatted, format_datetime_est_to_cst
from src.ui.components.market_status import display_market_status
from src.database.database_connectivity import DatabaseConnectivity

# Load environment variables
load_dotenv('config/.env', override=True)


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
    """Display an optimized portfolio summary section.
    
    Shows key metrics in a single row with additional metrics in an expander:
    - Primary metrics: Total Value, Daily P&L, Open Positions, Win Rate
    - Secondary metrics (in expander): Avg. Trade, Risk/Reward, Max Drawdown, Pending Orders
    """
    st.subheader("📊 Portfolio Overview")
    
    # Create a single row of key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Value", "$125,432.89", "+2.3%", delta_color="normal")
    with col2:
        st.metric("Daily P&L", "$1,234.56", "+1.2%", delta_color="normal")
    with col3:
        st.metric("Open Positions", "12", "-2", delta_color="inverse")
    with col4:
        st.metric("Win Rate", "68%", "+2%", delta_color="normal")
    
    # Add a small expander for additional metrics
    with st.expander("Additional Metrics"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Avg. Trade", "$342.50", "+$12.30", delta_color="normal")
        with col2:
            st.metric("Risk/Reward", "1:2.5", "0", delta_color="off")
        with col3:
            st.metric("Max Drawdown", "8.5%", "-1.2%", delta_color="normal")
        with col4:
            st.metric("Pending Orders", "3", "0", delta_color="off")


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
    """Display recent trading activity in a structured format.
    
    Shows recent trades with:
    - Action type (Buy/Sell/Limit)
    - Symbol and shares
    - Price
    - Time
    """
    st.subheader("📝 Recent Activity")
    
    # Create a more structured activity list
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
        st.button("📈 New Trade", use_container_width=True)
        st.caption("Open a new trading position")
        
        st.button("🔍 Market Scan", use_container_width=True)
        st.caption("Scan for trading opportunities")
    
    with col2:
        st.button("📊 Risk Analysis", use_container_width=True)
        st.caption("Analyze portfolio risk")
        
        st.button("📑 Reports", use_container_width=True)
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
    
    with col2:
        # Quick Actions
        display_quick_actions()
        st.divider()
        # Market News
        display_market_news()
    
    st.divider()
    
    # Symbol Selection and Analysis
    st.subheader("🔍 Symbol Analysis")
    selected_symbol = display_symbol_selector()
    if selected_symbol:
        st.session_state.selected_symbol = selected_symbol
        
        # Create columns for symbol details
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Price", "$185.92", "+1.5%")
        with col2:
            st.metric("Volume", "45.2M", "+12%")
        with col3:
            st.metric("Market Cap", "$2.9T", "0%")
