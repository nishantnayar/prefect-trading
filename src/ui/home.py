import streamlit as st
import os
from dotenv import load_dotenv
from src.ui.components.symbol_selector import display_symbol_selector

# Load environment variables
load_dotenv('config/.env', override=True)


def render_home():
    user_name = os.getenv("USER_NAME")

    st.title("🏠 Home")
    st.write(f"Welcome {user_name} to the Trading System Dashboard.")
    st.header("Introduction")

    st.divider()

    st.header("Market Details")

    st.divider()
    st.header("Asset Details")

    st.subheader("Symbol Selection")
    col1, col2 = st.columns([3, 3])

    with col1:
        selected_symbol = display_symbol_selector()
        if selected_symbol:
            st.session_state.selected_symbol = selected_symbol
    with col2:
        st.write(f"Symbol: {selected_symbol}")

