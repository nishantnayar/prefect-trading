import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone
from src.ui.components.symbol_selector import display_symbol_selector
from src.ui.components.date_display import get_current_cst_formatted
from src.ui.components.market_status import display_market_status

# Load environment variables
load_dotenv('config/.env', override=True)


def get_greeting() -> str:
    """Get appropriate greeting based on time of day."""
    current_hour = datetime.now(timezone('US/Central')).hour

    if 5 <= current_hour < 12:
        return "Good Morning"
    elif 12 <= current_hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"


def display_header(user_name: str):
    """Display the header section with greeting and time."""
    greeting = get_greeting()
    col1, col2 = st.columns([1, 1])

    with col1:
        st.title("🏠 Trading Dashboard")
        st.write(f"{greeting}, {user_name}!")

    with col2:
        st.write(f"🕒 {get_current_cst_formatted()}")
        display_market_status()


def display_portfolio_summary():
    """Display portfolio summary section."""
    st.subheader("📊 Portfolio Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Value", "$125,432.89", "+2.3%")
    with col2:
        st.metric("Daily P&L", "$1,234.56", "+1.2%")
    with col3:
        st.metric("Open Positions", "12", "-2")
    with col4:
        st.metric("Pending Orders", "3", "0")


def display_market_overview():
    """Display market overview section."""
    st.subheader("🌍 Market Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Major Indices**")
        st.metric("S&P 500", "4,783.45", "+0.8%")
        st.metric("NASDAQ", "16,742.38", "+1.2%")
        st.metric("DOW", "37,305.16", "+0.5%")

    with col2:
        st.write("**Market Movers**")
        st.metric("AAPL", "185.92", "+1.5%")
        st.metric("MSFT", "374.58", "+2.1%")
        st.metric("GOOGL", "140.93", "+0.9%")


def display_recent_activity():
    """Display recent trading activity."""
    st.subheader("📝 Recent Activity")

    # Placeholder for recent trades
    st.write("""
    - Bought 100 shares of AAPL at $185.50
    - Sold 50 shares of MSFT at $374.20
    - Placed limit order for GOOGL at $140.00
    """)


def display_quick_actions():
    """Display quick action buttons."""
    st.subheader("⚡ Quick Actions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.button("New Trade", use_container_width=True)
    with col2:
        st.button("Market Scan", use_container_width=True)
    with col3:
        st.button("Risk Analysis", use_container_width=True)
    with col4:
        st.button("Reports", use_container_width=True)


def display_market_news():
    """Display market news section."""
    st.subheader("📰 Market News")

    # Placeholder for news items
    st.write("""
    - Fed signals potential rate cuts in 2024
    - Tech stocks rally on AI boom
    - Oil prices stabilize after OPEC+ meeting
    """)


def render_home():
    """Main function to render the home page."""
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

    # Symbol Selection
    st.subheader("🔍 Symbol Analysis")
    selected_symbol = display_symbol_selector()
    if selected_symbol:
        st.session_state.selected_symbol = selected_symbol
        st.write(f"Selected symbol: {selected_symbol}")
