"""
Company Information Component
Handles display of company details from yahoo_company_info and yahoo_company_officers tables
"""

import streamlit as st
import pandas as pd
from src.database.database_connectivity import DatabaseConnectivity


def format_large_number(value):
    """Format large numbers into readable format (B, T, etc.)"""
    if not value or value == 0:
        return 'N/A'
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    elif value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.1f}M"
    elif value >= 1e3:
        return f"${value/1e3:.1f}K"
    else:
        return f"${value:,.0f}"


def format_compensation(value):
    """Format compensation values for officers table"""
    if pd.isna(value) or value == 0:
        return 'N/A'
    if value >= 1e6:
        return f"${value/1e6:.1f}M"
    elif value >= 1e3:
        return f"${value/1e3:.1f}K"
    else:
        return f"${value:,.0f}"


def get_company_data(symbol):
    """Fetch comprehensive company data from database"""
    try:
        db = DatabaseConnectivity()
        with db.get_session() as cursor:
            # Get detailed company info
            cursor.execute("""
                SELECT * FROM yahoo_company_info 
                WHERE symbol = %s
            """, (symbol,))
            company_info = cursor.fetchone()
            
            # Get column names for dynamic access
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'yahoo_company_info' 
                ORDER BY ordinal_position
            """)
            column_names = [row[0] for row in cursor.fetchall()]
            
            # Get company officers
            cursor.execute("""
                SELECT 
                    name, title, year_born, fiscal_year, total_pay, exercised_value,
                    unexercised_value
                FROM yahoo_company_officers 
                WHERE symbol = %s
                ORDER BY total_pay DESC NULLS LAST
                LIMIT 10
            """, (symbol,))
            officers = cursor.fetchall()
            
        if company_info:
            # Create a dictionary for easy access
            company_data = dict(zip(column_names, company_info))
            return company_data, officers
        else:
            return None, None
            
    except Exception as e:
        st.error(f"Error fetching company data: {str(e)}")
        return None, None


def display_company_overview(company_data, symbol):
    """Display company overview section"""
    if not company_data:
        st.info("No company information available")
        return
    
    st.subheader("🏢 Company Overview")
    
    # Create columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Basic company info
        company_name = company_data.get('longName') or company_data.get('shortName') or symbol
        st.write(f"**Company:** {company_name}")
        st.write(f"**Sector:** {company_data.get('sector', 'N/A')}")
        st.write(f"**Industry:** {company_data.get('industry', 'N/A')}")
        st.write(f"**Exchange:** {company_data.get('exchange', 'N/A')}")
        
        # Current price and market data
        current_price = company_data.get('currentPrice')
        if current_price:
            st.write(f"**Current Price:** ${current_price:.2f}")
        
        market_cap = company_data.get('marketCap')
        if market_cap:
            st.write(f"**Market Cap:** {format_large_number(market_cap)}")
        
        # Financial metrics
        enterprise_value = company_data.get('enterpriseValue')
        if enterprise_value:
            st.write(f"**Enterprise Value:** {format_large_number(enterprise_value)}")
        
        trailing_pe = company_data.get('trailingPE')
        if trailing_pe:
            st.write(f"**P/E Ratio:** {trailing_pe:.2f}")
        
        dividend_yield = company_data.get('dividendYield')
        if dividend_yield:
            st.write(f"**Dividend Yield:** {dividend_yield:.2%}")
        
        beta = company_data.get('beta')
        if beta:
            st.write(f"**Beta:** {beta:.2f}")
    
    with col2:
        # 52-week range
        week_high = company_data.get('fiftyTwoWeekHigh')
        week_low = company_data.get('fiftyTwoWeekLow')
        if week_high and week_low:
            st.write(f"**52-Week High:** ${week_high:.2f}")
            st.write(f"**52-Week Low:** ${week_low:.2f}")
        
        # Moving averages
        fifty_day = company_data.get('fiftyDayAverage')
        if fifty_day:
            st.write(f"**50-Day Avg:** ${fifty_day:.2f}")
        
        two_hundred_day = company_data.get('twoHundredDayAverage')
        if two_hundred_day:
            st.write(f"**200-Day Avg:** ${two_hundred_day:.2f}")
        
        # Volume and shares
        shares_outstanding = company_data.get('sharesOutstanding')
        if shares_outstanding:
            if shares_outstanding >= 1e9:
                shares_display = f"{shares_outstanding/1e9:.2f}B"
            else:
                shares_display = f"{shares_outstanding:,.0f}"
            st.write(f"**Shares Outstanding:** {shares_display}")


def display_company_officers(officers):
    """Display company officers section"""
    if not officers:
        return
    
    st.subheader("👥 Company Officers")
    
    # Create a DataFrame for better display
    officers_df = pd.DataFrame(officers, columns=[
        'Name', 'Title', 'Year Born', 'Fiscal Year', 
        'Total Pay', 'Exercised Value', 'Unexercised Value'
    ])
    
    # Apply formatting to compensation columns
    officers_df['Total Pay'] = officers_df['Total Pay'].apply(format_compensation)
    officers_df['Exercised Value'] = officers_df['Exercised Value'].apply(format_compensation)
    officers_df['Unexercised Value'] = officers_df['Unexercised Value'].apply(format_compensation)
    
    # Display officers table
    st.dataframe(
        officers_df[['Name', 'Title', 'Total Pay', 'Exercised Value', 'Unexercised Value']],
        use_container_width=True,
        hide_index=True
    )


def render_company_info(symbol):
    """Main function to render company information"""
    company_data, officers = get_company_data(symbol)
    
    if company_data:
        display_company_overview(company_data, symbol)
        display_company_officers(officers)
    else:
        st.info("No company information available for this symbol") 