import streamlit as st
import streamlit_option_menu as option_menu
from pathlib import Path
import sys
from streamlit_autorefresh import st_autorefresh

# 1. Set up project root path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.ui.home import render_home
from src.ui.portfolio import render_portfolio
from src.ui.components.testing_results import render_testing_results
from src.ui.components.symbol_selector import display_symbol_selector_with_analysis

# 2. Page config must be top-level
st.set_page_config(
    page_title="Trading System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None  # Hides the default Streamlit menu
)


# 3. Load custom CSS from external file
def load_css():
    css_file = project_root / "config" / "streamlit_style.css"
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()

# 4. Auto-refresh disabled - using intelligent caching instead
# st_autorefresh(interval=10000)  # Disabled to prevent excessive API calls

# Smart auto-refresh option (uncomment to enable)
# This will refresh every 30 seconds but respect cache timing
# AUTO_REFRESH_ENABLED = True
# if AUTO_REFRESH_ENABLED:
#     st_autorefresh(interval=30000)  # 30 seconds to match cache duration

# 4. Manual refresh button in sidebar
with st.sidebar:
    if st.button("🔄 Refresh All Data", help="Force refresh all portfolio and market data"):
        # Clear cache before rerun
        from src.ui.home import clear_portfolio_manager
        from src.ui.portfolio import clear_portfolio_manager as clear_portfolio_manager_alt
        clear_portfolio_manager()
        clear_portfolio_manager_alt()
        st.rerun()
    
    # Note about refresh functionality
    st.caption("💡 Use the refresh button above to update all data across the app")


def main():
    """Main application entry point."""

    # Sidebar Navigation
    with st.sidebar:
        selected = option_menu.option_menu(
            menu_title="Trading System",
            options=["Home", "Portfolio", "Analysis", "Testing", "Settings"],
            icons=["house", "briefcase", "graph-up", "clipboard-check", "gear"],
            menu_icon="chart-line",
            default_index=0,
        )

    # Routing
    if selected == "Home":
        render_home()
    elif selected == "Portfolio":
        render_portfolio()
    elif selected == "Analysis":
        display_symbol_selector_with_analysis()
    elif selected == "Testing":
        render_testing_results()
    elif selected == "Settings":
        st.title("⚙️ Settings")
        st.write("Configure your system preferences.")


if __name__ == "__main__":
    main()
