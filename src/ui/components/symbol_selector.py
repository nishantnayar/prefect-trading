import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from loguru import logger

from src.data.sources.symbol_manager import SymbolManager
from src.database.database_connectivity import DatabaseConnectivity
from src.ui.components.date_display import format_date_nice


def display_symbol_selector(sectors: Optional[List[str]] = None) -> str:
    """Display symbol selector component with optional sector filtering.
    
    Args:
        sectors: List of sectors to filter by. If None, uses active sectors from config.
    
    Returns:
        str: Selected symbol or None if no selection
    """
    try:
        # Initialize SymbolManager and get active symbols
        symbol_manager = SymbolManager()
        symbols = symbol_manager.get_active_symbols(sectors=sectors)
        
        if not symbols:
            st.warning("No active symbols found")
            return None
        
        # Get sector summary for display
        sector_summary = symbol_manager.get_sector_summary()
        
        # Create symbol selector with sector info
        if sectors:
            sector_display = ", ".join(sectors)
            selected_symbol = st.selectbox(
                label=f"Select a Symbol (Filtered by: {sector_display})",
                options=symbols,
                index=0 if symbols else None
            )
        else:
            selected_symbol = st.selectbox(
                label="Select a Symbol",
                options=symbols,
                index=0 if symbols else None
            )
        
        return selected_symbol
        
    except Exception as e:
        logger.error(f"Error in symbol selector: {e}")
        st.error("Error loading symbols. Please try again later.")
        return None


def display_sector_selector() -> Optional[List[str]]:
    """Display sector selector component.
    
    Returns:
        Optional[List[str]]: Selected sectors or None if no selection
    """
    try:
        symbol_manager = SymbolManager()
        available_sectors = symbol_manager.get_available_sectors()
        active_sectors = symbol_manager.get_active_sectors()
        
        # Get actual sectors from database
        sector_summary = symbol_manager.get_sector_summary()
        actual_sectors = list(sector_summary.keys())
        
        if not actual_sectors:
            st.warning("No sectors found in database")
            return None
        
        # Create sector selector
        selected_sectors = st.multiselect(
            label="Select Sectors to Filter",
            options=actual_sectors,
            default=active_sectors if active_sectors else actual_sectors[:1],
            help="Select one or more sectors to filter symbols"
        )
        
        return selected_sectors if selected_sectors else None
        
    except Exception as e:
        logger.error(f"Error in sector selector: {e}")
        st.error("Error loading sectors. Please try again later.")
        return None


def display_symbol_analysis(symbol: str) -> None:
    """Display comprehensive symbol analysis.
    
    Args:
        symbol: Stock symbol to analyze
    """
    if not symbol:
        st.warning("Please select a symbol to analyze")
        return
    
    try:
        # Create tabs for different analysis sections (remove News tab)
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Market Data", "🏢 Company Info"])
        
        with tab1:
            display_symbol_overview_with_db(symbol)
        
        with tab2:
            display_market_data_analysis(symbol)
        
        with tab3:
            display_company_info(symbol)
        
    except Exception as e:
        logger.error(f"Error in symbol analysis: {e}")
        st.error("Error loading symbol analysis. Please try again later.")


def get_symbol_overview_data(symbol: str, db) -> dict:
    """Fetch symbol overview and market summary from the database."""
    symbol_manager = SymbolManager()
    symbol_info = symbol_manager.get_symbol_info(symbol)
    market_summary = None
    if symbol_info:
        with db.get_session() as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) as data_points,
                    MIN(timestamp) as first_data,
                    MAX(timestamp) as last_data,
                    AVG(close) as avg_price,
                    MAX(close) as max_price,
                    MIN(close) as min_price,
                    AVG(volume) as avg_volume
                FROM market_data 
                WHERE symbol = %s
            """, (symbol,))
            market_summary = cursor.fetchone()
    return {
        'symbol_info': symbol_info,
        'market_summary': market_summary
    }


def display_symbol_overview(symbol: str, data: dict) -> None:
    """Display symbol overview information using provided data."""
    st.subheader(f"📊 {symbol} Overview")
    try:
        symbol_info = data.get('symbol_info')
        market_summary = data.get('market_summary')
        if symbol_info:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Symbol", symbol_info['symbol'])
                st.metric("Status", "🟢 Active" if symbol_info['is_active'] else "🔴 Inactive")
            with col2:
                st.metric("Name", symbol_info['name'] or "N/A")
                st.metric("Added", format_date_nice(symbol_info['start_date']))
            with col3:
                st.metric("Last Updated", format_date_nice(symbol_info['updated_at']))
                if symbol_info['end_date']:
                    st.metric("End Date", format_date_nice(symbol_info['end_date']))
        if market_summary:
            st.subheader("📈 Market Data Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Data Points", f"{market_summary[0]:,}")
                st.metric("First Data", format_date_nice(market_summary[1]) if market_summary[1] else "N/A")
            with col2:
                st.metric("Last Data", format_date_nice(market_summary[2]) if market_summary[2] else "N/A")
                st.metric("Avg Price", f"${market_summary[3]:.2f}" if market_summary[3] else "N/A")
            with col3:
                st.metric("Max Price", f"${market_summary[4]:.2f}" if market_summary[4] else "N/A")
                st.metric("Min Price", f"${market_summary[5]:.2f}" if market_summary[5] else "N/A")
            with col4:
                st.metric("Avg Volume", f"{market_summary[6]:,.0f}" if market_summary[6] else "N/A")
    except Exception as e:
        logger.error(f"Error in symbol overview: {e}")
        st.error("Error loading symbol overview")


def display_symbol_overview_with_db(symbol: str) -> None:
    db = DatabaseConnectivity()
    data = get_symbol_overview_data(symbol, db)
    display_symbol_overview(symbol, data)


def display_market_data_analysis(symbol: str) -> None:
    """Display market data analysis for the symbol.
    
    Args:
        symbol: Stock symbol
    """
    st.subheader(f"📈 {symbol} Market Data Analysis")
    
    try:
        db = DatabaseConnectivity()
        
        # Get recent market data
        with db.get_session() as cursor:
            cursor.execute("""
                SELECT 
                    timestamp,
                    open,
                    high,
                    low,
                    close,
                    volume
                FROM market_data 
                WHERE symbol = %s
                ORDER BY timestamp DESC
                LIMIT 100
            """, (symbol,))
            
            data = cursor.fetchall()
            
            if data:
                # Convert to DataFrame
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Display recent data
                st.subheader("Recent Market Data")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Calculate and display statistics
                st.subheader("Price Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    current_price = df['close'].iloc[0]
                    prev_price = df['close'].iloc[1] if len(df) > 1 else current_price
                    change = current_price - prev_price
                    change_pct = (change / prev_price * 100) if prev_price != 0 else 0
                    
                    st.metric(
                        "Current Price", 
                        f"${current_price:.2f}",
                        delta=f"{change:+.2f} ({change_pct:+.2f}%)"
                    )
                
                with col2:
                    st.metric("52-Week High", f"${df['high'].max():.2f}")
                    st.metric("52-Week Low", f"${df['low'].min():.2f}")
                
                with col3:
                    st.metric("Average Price", f"${df['close'].mean():.2f}")
                    st.metric("Price Volatility", f"{df['close'].std():.2f}")
                
                with col4:
                    st.metric("Average Volume", f"{df['volume'].mean():,.0f}")
                    st.metric("Max Volume", f"{df['volume'].max():,.0f}")
                
                # Price chart
                st.subheader("Price Chart")
                chart_data = df[['timestamp', 'close']].set_index('timestamp')
                st.line_chart(chart_data)
                
            else:
                st.warning("No market data available for this symbol")
                
    except Exception as e:
        logger.error(f"Error in market data analysis: {e}")
        st.error("Error loading market data analysis")


def display_company_info(symbol: str) -> None:
    """Display company information for the symbol.
    
    Args:
        symbol: Stock symbol
    """
    st.subheader(f"🏢 {symbol} Company Information")
    
    try:
        db = DatabaseConnectivity()
        
        # Get company info from yahoo_company_info table
        with db.get_session() as cursor:
            cursor.execute("""
                SELECT 
                    "longName",
                    sector,
                    industry,
                    "marketCap",
                    "currentPrice",
                    "fiftyTwoWeekHigh",
                    "fiftyTwoWeekLow",
                    "averageVolume",
                    "trailingPE",
                    "forwardPE",
                    "dividendYield",
                    beta,
                    website,
                    "longBusinessSummary"
                FROM yahoo_company_info 
                WHERE symbol = %s
            """, (symbol,))
            
            company_info = cursor.fetchone()
            
            if company_info:
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.subheader("Company Details")
                    
                    # Basic info
                    if company_info[0]:  # longName
                        st.write(f"**Company:** {company_info[0]}")
                    if company_info[1]:  # sector
                        st.write(f"**Sector:** {company_info[1]}")
                    if company_info[2]:  # industry
                        st.write(f"**Industry:** {company_info[2]}")
                    if company_info[12]:  # website
                        st.write(f"**Website:** [{company_info[12]}]({company_info[12]})")
                    
                    # Financial metrics
                    st.subheader("Financial Metrics")
                    
                    if company_info[3]:  # marketCap
                        market_cap = company_info[3]
                        if market_cap >= 1e12:
                            st.write(f"**Market Cap:** ${market_cap/1e12:.2f}T")
                        elif market_cap >= 1e9:
                            st.write(f"**Market Cap:** ${market_cap/1e9:.2f}B")
                        elif market_cap >= 1e6:
                            st.write(f"**Market Cap:** ${market_cap/1e6:.2f}M")
                        else:
                            st.write(f"**Market Cap:** ${market_cap:,.0f}")
                    
                    if company_info[4]:  # currentPrice
                        st.write(f"**Current Price:** ${company_info[4]:.2f}")
                    if company_info[5]:  # fiftyTwoWeekHigh
                        st.write(f"**52-Week High:** ${company_info[5]:.2f}")
                    if company_info[6]:  # fiftyTwoWeekLow
                        st.write(f"**52-Week Low:** ${company_info[6]:.2f}")
                    if company_info[7]:  # averageVolume
                        st.write(f"**Avg Volume:** {company_info[7]:,.0f}")
                    if company_info[8]:  # trailingPE
                        st.write(f"**Trailing P/E:** {company_info[8]:.2f}")
                    if company_info[9]:  # forwardPE
                        st.write(f"**Forward P/E:** {company_info[9]:.2f}")
                    if company_info[10]:  # dividendYield
                        st.write(f"**Dividend Yield:** {company_info[10]:.2%}")
                    if company_info[11]:  # beta
                        st.write(f"**Beta:** {company_info[11]:.2f}")
                
                with col2:
                    st.subheader("Business Summary")
                    if company_info[13]:  # longBusinessSummary
                        st.write(company_info[13])
                    else:
                        st.info("No business summary available")
                
                # Get company officers
                cursor.execute("""
                    SELECT name, title, age, total_pay
                    FROM yahoo_company_officers 
                    WHERE symbol = %s
                    ORDER BY total_pay DESC NULLS LAST
                    LIMIT 10
                """, (symbol,))
                
                officers = cursor.fetchall()
                
                if officers:
                    st.subheader("Key Officers")
                    officers_df = pd.DataFrame(officers, columns=['Name', 'Title', 'Age', 'Total Pay'])
                    officers_df['Total Pay'] = officers_df['Total Pay'].apply(
                        lambda x: f"${x:,.0f}" if pd.notna(x) and x is not None else "Not Available"
                    )
                    st.dataframe(officers_df, use_container_width=True)
                
            else:
                st.warning("No company information available for this symbol")
                
    except Exception as e:
        logger.error(f"Error in company info: {e}")
        st.error("Error loading company information")


def display_symbol_news(symbol: str) -> None:
    """Display news articles related to the symbol.
    
    Args:
        symbol: Stock symbol
    """
    st.subheader(f"📰 {symbol} News")
    
    try:
        db = DatabaseConnectivity()
        
        # Get recent news articles for the symbol
        with db.get_session() as cursor:
            cursor.execute("""
                SELECT 
                    title,
                    source_name,
                    url,
                    published_at,
                    description
                FROM news_articles 
                WHERE title ILIKE %s OR description ILIKE %s
                ORDER BY published_at DESC
                LIMIT 10
            """, (f'%{symbol}%', f'%{symbol}%'))
            
            news_articles = cursor.fetchall()
            
            if news_articles:
                for i, article in enumerate(news_articles):
                    title, source, url, published_at, description = article
                    
                    # Create expander for each article
                    with st.expander(f"{title} - {source}"):
                        if published_at:
                            st.write(f"**Published:** {published_at.strftime('%Y-%m-%d %H:%M')}")
                        
                        if description:
                            st.write(description)
                        
                        if url:
                            st.write(f"**Source:** [{url}]({url})")
            else:
                st.info("No recent news found for this symbol")
                
    except Exception as e:
        logger.error(f"Error in symbol news: {e}")
        st.error("Error loading news articles")


def display_symbol_selector_with_analysis() -> Optional[str]:
    """Display symbol selector with comprehensive analysis.
    
    Uses the symbol already selected on the main page if available,
    otherwise shows a symbol selector.
    
    Returns:
        Optional[str]: Selected symbol or None
    """
    st.title("📊 Analysis")
    st.write("Explore data analysis and trading signals.")
    st.header("🔍 Symbol Analysis")
    
    # Check if a symbol is already selected from the main page
    selected_symbol = st.session_state.get('selected_symbol')
    
    if selected_symbol:
        # Display the currently selected symbol
        st.info(f"📈 Analyzing: **{selected_symbol}**")
        
        # Option to change symbol
        if st.button("🔄 Change Symbol"):
            st.session_state.selected_symbol = None
            st.rerun()
        
        # Display analysis for the selected symbol
        display_symbol_analysis(selected_symbol)
        
    else:
        # No symbol selected, show symbol selector
        st.info("Please select a symbol to analyze")
        selected_symbol = display_symbol_selector()
        
        if selected_symbol:
            st.session_state.selected_symbol = selected_symbol
            st.rerun()
    
    return selected_symbol 