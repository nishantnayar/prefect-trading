import streamlit as st
import os
from dotenv import load_dotenv
from src.ui.components.symbol_selector import display_symbol_selector
from src.ui.components.date_display import get_current_cst_formatted
from src.ui.components.market_status import display_market_status
from datetime import datetime
from pytz import timezone

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


def render_home():
    user_name = os.getenv("USER_NAME")
    greeting = get_greeting()

    st.title("🏠 Home")
    st.write(f"{greeting}, {user_name}! ")
    st.write(f"Welcome to the Trading System Dashboard.")
    st.write(f'Current Time is {get_current_cst_formatted()}')

    # Display market status
    display_market_status()

    st.divider()
    st.header("Asset Details")

    st.subheader("Symbol Selection")

    selected_symbol = display_symbol_selector()
    if selected_symbol:
        st.session_state.selected_symbol = selected_symbol

    st.write(f"Select symbol is {selected_symbol}")

