"""
Symbol Selector Component
Handles sector and symbol selection for analysis
"""

import streamlit as st
from src.database.database_connectivity import DatabaseConnectivity


def get_available_sectors():
    """Get available sectors from database"""
    try:
        db = DatabaseConnectivity()
        with db.get_session() as cursor:
            cursor.execute("""
                SELECT DISTINCT sector 
                FROM yahoo_company_info 
                WHERE sector IS NOT NULL AND sector != ''
                ORDER BY sector
            """)
            sectors = [row[0] for row in cursor.fetchall()]
        return sectors
    except Exception as e:
        st.error(f"Error loading sectors: {str(e)}")
        return []


def get_symbols_by_sectors(selected_sectors):
    """Get symbols based on selected sectors"""
    if not selected_sectors:
        return []
    
    try:
        db = DatabaseConnectivity()
        with db.get_session() as cursor:
            # Create placeholders for the IN clause
            placeholders = ','.join(['%s'] * len(selected_sectors))
            cursor.execute(f"""
                SELECT symbol 
                FROM yahoo_company_info 
                WHERE sector IN ({placeholders}) AND symbol IN (
                    SELECT symbol FROM symbols WHERE is_active = true
                )
                ORDER BY symbol
            """, selected_sectors)
            symbols = [row[0] for row in cursor.fetchall()]
        return symbols
    except Exception as e:
        st.error(f"Error loading symbols: {str(e)}")
        return []


def render_sector_selection():
    """Render sector selection interface"""
    st.subheader("🔍 Select Sector & Symbol")
    
    # Get available sectors
    sectors = get_available_sectors()
    
    if not sectors:
        st.warning("No sectors found in database")
        return None, None
    
    # Sector selection - full width
    st.write("**Step 1: Select Sectors**")
    selected_sectors = st.multiselect(
        "Choose sectors (select multiple):",
        options=sectors,
        default=["Technology"] if "Technology" in sectors else sectors[:1],  # Default to Technology
        help="Select one or more sectors to filter symbols"
    )
    
    return selected_sectors, sectors


def render_symbol_selection(selected_sectors):
    """Render symbol selection interface"""
    st.write("**Step 2: Select Symbol**")
    
    # Get symbols based on selected sectors
    if not selected_sectors:
        st.info("Please select at least one sector")
        return None
    
    symbols = get_symbols_by_sectors(selected_sectors)
    
    if symbols:
        selected_symbol = st.selectbox(
            "Choose a symbol to analyze:",
            options=symbols,
            index=0
        )
        
        if selected_symbol:
            st.session_state.selected_symbol = selected_symbol
            return selected_symbol
    else:
        sectors_text = ", ".join(selected_sectors)
        st.warning(f"No symbols found for sectors: {sectors_text}")
        return None


def render_symbol_selector():
    """Main function to render symbol selector"""
    selected_sectors, sectors = render_sector_selection()
    
    if selected_sectors:
        selected_symbol = render_symbol_selection(selected_sectors)
        return selected_symbol
    
    return None 