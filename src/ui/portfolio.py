"""
Comprehensive Portfolio Page

This module provides a detailed portfolio view with:
- Account overview and balance
- Current positions with performance
- Portfolio allocation and risk metrics
- Trading history and performance
- Position analysis and charts
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/.env', override=True)

from src.data.sources.portfolio_manager import PortfolioManager
from src.ui.components.date_display import format_datetime_est_to_cst


def display_account_overview(account_info: Dict):
    """Display comprehensive account overview.
    
    Args:
        account_info: Account information from Alpaca
    """
    st.subheader("💰 Account Overview")
    
    # Create three columns for account metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Portfolio Value", 
            f"${account_info.get('portfolio_value', 0):,.2f}",
            help="Total value of all positions plus cash"
        )
        st.metric(
            "Cash", 
            f"${account_info.get('cash', 0):,.2f}",
            help="Available cash in account"
        )
    
    with col2:
        st.metric(
            "Buying Power", 
            f"${account_info.get('buying_power', 0):,.2f}",
            help="Available buying power including margin"
        )
        st.metric(
            "Equity", 
            f"${account_info.get('equity', 0):,.2f}",
            help="Account equity (portfolio value minus any margin debt)"
        )
    
    with col3:
        st.metric(
            "Day Trading Power", 
            f"${account_info.get('daytrading_buying_power', 0):,.2f}",
            help="Available day trading buying power"
        )
        st.metric(
            "Margin Used", 
            f"${account_info.get('initial_margin', 0):,.2f}",
            help="Initial margin requirement for current positions"
        )
    
    # Account status and restrictions
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = account_info.get('status', 'unknown')
        status_color = "green" if status == "ACTIVE" else "red"
        st.markdown(f"**Account Status:** <span style='color:{status_color}'>{status}</span>", unsafe_allow_html=True)
        
        pattern_day_trader = account_info.get('pattern_day_trader', False)
        pdt_status = "⚠️ Pattern Day Trader" if pattern_day_trader else "✅ Regular Account"
        st.markdown(f"**Account Type:** {pdt_status}")
    
    with col2:
        trading_blocked = account_info.get('trading_blocked', False)
        trading_status = "❌ Trading Blocked" if trading_blocked else "✅ Trading Enabled"
        st.markdown(f"**Trading Status:** {trading_status}")
        
        shorting_enabled = account_info.get('shorting_enabled', False)
        shorting_status = "✅ Shorting Enabled" if shorting_enabled else "❌ Shorting Disabled"
        st.markdown(f"**Shorting:** {shorting_status}")
    
    with col3:
        daytrade_count = account_info.get('daytrade_count', 0)
        st.metric("Day Trades Today", daytrade_count, help="Number of day trades used today")
        
        multiplier = account_info.get('multiplier', 1)
        st.metric("Margin Multiplier", f"{multiplier}x", help="Account margin multiplier")


def display_positions_table(positions: List[Dict]):
    """Display positions in a detailed table format.
    
    Args:
        positions: List of position dictionaries
    """
    st.subheader("📊 Current Positions")
    
    if not positions:
        st.info("No open positions found.")
        return
    
    # Convert positions to DataFrame for better display
    df = pd.DataFrame(positions)
    
    # Calculate additional metrics
    df['total_cost'] = df['cost_basis'] * df['qty']
    df['market_value'] = df['market_value'].abs()
    df['unrealized_pl_pct'] = df['unrealized_plpc'] * 100
    
    # Format the display
    display_df = df[['symbol', 'qty', 'side', 'current_price', 'cost_basis', 
                     'market_value', 'unrealized_pl', 'unrealized_pl_pct']].copy()
    
    display_df.columns = ['Symbol', 'Quantity', 'Side', 'Current Price', 'Cost Basis', 
                         'Market Value', 'Unrealized P&L', 'P&L %']
    
    # Format currency columns
    for col in ['Current Price', 'Cost Basis', 'Market Value', 'Unrealized P&L']:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}")
    
    # Format percentage column
    display_df['P&L %'] = display_df['P&L %'].apply(lambda x: f"{x:+.2f}%")
    
    # Color code the P&L
    def color_pnl(val):
        try:
            pnl = float(val.replace('$', '').replace(',', ''))
            color = 'green' if pnl > 0 else 'red' if pnl < 0 else 'black'
            return f'color: {color}'
        except:
            return ''
    
    # Apply styling
    styled_df = display_df.style.applymap(color_pnl, subset=['Unrealized P&L', 'P&L %'])
    
    st.dataframe(styled_df, use_container_width=True)
    
    # Summary metrics
    total_positions = len(positions)
    total_market_value = sum(pos.get('market_value', 0) for pos in positions)
    total_unrealized_pl = sum(pos.get('unrealized_pl', 0) for pos in positions)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Positions", total_positions)
    with col2:
        st.metric("Total Market Value", f"${total_market_value:,.2f}")
    with col3:
        st.metric("Total Unrealized P&L", f"${total_unrealized_pl:,.2f}")
    with col4:
        avg_pnl_pct = (total_unrealized_pl / total_market_value * 100) if total_market_value > 0 else 0
        st.metric("Avg P&L %", f"{avg_pnl_pct:+.2f}%")


def display_portfolio_allocation(positions: List[Dict]):
    """Display portfolio allocation charts.
    
    Args:
        positions: List of position dictionaries
    """
    st.subheader("📈 Portfolio Allocation")
    
    if not positions:
        st.info("No positions to display allocation for.")
        return
    
    # Calculate allocation data
    total_value = sum(pos.get('market_value', 0) for pos in positions)
    
    if total_value == 0:
        st.info("No market value in positions.")
        return
    
    # Prepare data for pie chart
    allocation_data = []
    for pos in positions:
        symbol = pos['symbol']
        market_value = pos.get('market_value', 0)
        allocation_pct = (market_value / total_value) * 100
        allocation_data.append({
            'Symbol': symbol,
            'Market Value': market_value,
            'Allocation %': allocation_pct
        })
    
    df = pd.DataFrame(allocation_data)
    
    # Create pie chart
    fig = px.pie(
        df, 
        values='Market Value', 
        names='Symbol',
        title='Portfolio Allocation by Position',
        hover_data=['Allocation %']
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
    
    # Display allocation table
    st.subheader("Allocation Details")
    allocation_df = df.sort_values('Market Value', ascending=False)
    allocation_df['Market Value'] = allocation_df['Market Value'].apply(lambda x: f"${x:,.2f}")
    allocation_df['Allocation %'] = allocation_df['Allocation %'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(allocation_df, use_container_width=True)


def display_trading_history(orders: List[Dict]):
    """Display trading history and performance.
    
    Args:
        orders: List of order dictionaries
    """
    st.subheader("📝 Trading History")
    
    if not orders:
        st.info("No trading history available.")
        return
    
    # Filter for filled orders only
    filled_orders = [order for order in orders if order.get('filled_at')]
    
    if not filled_orders:
        st.info("No filled orders found.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(filled_orders)
    
    # Calculate trade metrics
    df['trade_value'] = df['filled_qty'] * df['filled_avg_price']
    df['date'] = pd.to_datetime(df['filled_at']).dt.date
    
    # Group by date for daily performance
    daily_performance = df.groupby('date').agg({
        'trade_value': 'sum',
        'filled_qty': 'sum',
        'symbol': 'count'
    }).reset_index()
    daily_performance.columns = ['Date', 'Total Value', 'Total Shares', 'Number of Trades']
    
    # Display recent trades
    st.subheader("Recent Trades")
    recent_trades = df.head(10)[['symbol', 'side', 'filled_qty', 'filled_avg_price', 
                                'trade_value', 'filled_at']].copy()
    recent_trades.columns = ['Symbol', 'Side', 'Shares', 'Price', 'Value', 'Date']
    
    # Format columns
    recent_trades['Price'] = recent_trades['Price'].apply(lambda x: f"${x:,.2f}")
    recent_trades['Value'] = recent_trades['Value'].apply(lambda x: f"${x:,.2f}")
    recent_trades['Date'] = pd.to_datetime(recent_trades['Date']).dt.strftime('%Y-%m-%d %H:%M')
    
    st.dataframe(recent_trades, use_container_width=True)
    
    # Performance metrics
    st.subheader("Trading Performance")
    
    total_trades = len(filled_orders)
    total_volume = sum(order.get('trade_value', 0) for order in filled_orders)
    avg_trade_size = total_volume / total_trades if total_trades > 0 else 0
    
    # Calculate win rate (simplified - you might want more sophisticated logic)
    buy_orders = [order for order in filled_orders if order.get('side') == 'buy']
    sell_orders = [order for order in filled_orders if order.get('side') == 'sell']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Trades", total_trades)
    with col2:
        st.metric("Total Volume", f"${total_volume:,.2f}")
    with col3:
        st.metric("Avg Trade Size", f"${avg_trade_size:,.2f}")
    with col4:
        st.metric("Buy/Sell Ratio", f"{len(buy_orders)}/{len(sell_orders)}")


def display_risk_metrics(account_info: Dict, positions: List[Dict]):
    """Display risk metrics and analysis.
    
    Args:
        account_info: Account information
        positions: List of positions
    """
    st.subheader("⚠️ Risk Analysis")
    
    # Calculate risk metrics
    portfolio_value = account_info.get('portfolio_value', 0)
    margin_used = account_info.get('initial_margin', 0)
    maintenance_margin = account_info.get('maintenance_margin', 0)
    
    # Margin utilization
    margin_ratio = (margin_used / portfolio_value * 100) if portfolio_value > 0 else 0
    maintenance_ratio = (maintenance_margin / portfolio_value * 100) if portfolio_value > 0 else 0
    
    # Position concentration
    if positions:
        total_position_value = sum(pos.get('market_value', 0) for pos in positions)
        largest_position = max(positions, key=lambda x: x.get('market_value', 0))
        largest_position_pct = (largest_position.get('market_value', 0) / total_position_value * 100) if total_position_value > 0 else 0
    else:
        largest_position_pct = 0
    
    # Display risk metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Margin Utilization", 
            f"{margin_ratio:.1f}%",
            help="Percentage of portfolio value used as margin"
        )
    
    with col2:
        st.metric(
            "Maintenance Margin", 
            f"{maintenance_ratio:.1f}%",
            help="Maintenance margin requirement as percentage of portfolio"
        )
    
    with col3:
        st.metric(
            "Largest Position", 
            f"{largest_position_pct:.1f}%",
            help="Percentage of portfolio in largest single position"
        )
    
    with col4:
        pattern_day_trader = account_info.get('pattern_day_trader', False)
        pdt_status = "Yes" if pattern_day_trader else "No"
        st.metric(
            "Pattern Day Trader", 
            pdt_status,
            help="Account flagged as pattern day trader"
        )
    
    # Risk warnings
    st.subheader("Risk Warnings")
    
    warnings = []
    if margin_ratio > 50:
        warnings.append("⚠️ High margin utilization (>50%)")
    if largest_position_pct > 20:
        warnings.append("⚠️ High position concentration (>20%)")
    if pattern_day_trader:
        warnings.append("⚠️ Pattern day trader restrictions apply")
    if account_info.get('trading_blocked', False):
        warnings.append("❌ Trading is currently blocked")
    
    if warnings:
        for warning in warnings:
            st.warning(warning)
    else:
        st.success("✅ No significant risk warnings detected")


def render_portfolio():
    """Main function to render the comprehensive portfolio page."""
    st.title("💼 Portfolio Management")
    
    # Add refresh button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write("")  # Spacer
    with col2:
        if st.button("🔄 Refresh Data", help="Refresh all portfolio data"):
            st.rerun()
    
    try:
        # Initialize portfolio manager
        portfolio_manager = PortfolioManager()
        
        # Get portfolio data
        portfolio_summary = portfolio_manager.get_portfolio_summary()
        
        if not portfolio_summary:
            st.error("Unable to fetch portfolio data. Please check your Alpaca API credentials.")
            return
        
        metrics = portfolio_summary.get('metrics', {})
        positions = portfolio_summary.get('positions', [])
        recent_activity = portfolio_summary.get('recent_activity', [])
        
        # Get account info for detailed display
        account_info = portfolio_manager.get_account_info()
        
        # Display account overview
        display_account_overview(account_info)
        
        st.divider()
        
        # Display positions
        display_positions_table(positions)
        
        st.divider()
        
        # Display portfolio allocation
        display_portfolio_allocation(positions)
        
        st.divider()
        
        # Display trading history
        orders = portfolio_manager.get_orders("closed")
        display_trading_history(orders)
        
        st.divider()
        
        # Display risk metrics
        display_risk_metrics(account_info, positions)
        
        # Last updated timestamp
        st.divider()
        last_updated = portfolio_summary.get('last_updated', 'Unknown')
        st.caption(f"Last updated: {last_updated}")
        
    except Exception as e:
        st.error(f"Error loading portfolio data: {str(e)}")
        st.info("Please ensure your Alpaca API credentials are properly configured.")


if __name__ == "__main__":
    render_portfolio() 