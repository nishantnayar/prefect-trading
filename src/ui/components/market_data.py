"""
Market Data Component
Handles display of market data, OHLC charts, and statistics
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.database.database_connectivity import DatabaseConnectivity


def get_consolidated_market_data(symbol):
    """Get consolidated market data from both tables with proper deduplication"""
    try:
        db = DatabaseConnectivity()
        with db.get_session() as cursor:
            # Get consolidated data from both tables with deduplication
            cursor.execute("""
                WITH combined_data AS (
                    SELECT 
                        timestamp as date,
                        open,
                        high,
                        low,
                        close,
                        volume,
                        'recent' as data_source,
                        ROW_NUMBER() OVER (PARTITION BY timestamp ORDER BY timestamp DESC) as rn
                    FROM market_data 
                    WHERE symbol = %s
                    
                    UNION ALL
                    
                    SELECT 
                        timestamp as date,
                        open,
                        high,
                        low,
                        close,
                        volume,
                        'historical' as data_source,
                        ROW_NUMBER() OVER (PARTITION BY timestamp ORDER BY timestamp DESC) as rn
                    FROM market_data_historical 
                    WHERE symbol = %s
                )
                SELECT 
                    date,
                    open,
                    high,
                    low,
                    close,
                    volume,
                    data_source
                FROM combined_data
                WHERE rn = 1
                ORDER BY date DESC
            """, (symbol, symbol))
            
            consolidated_data = cursor.fetchall()
            
        if consolidated_data:
            df = pd.DataFrame(consolidated_data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Source'])
            
            # Convert date column to datetime
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Remove duplicates based on date (keep most recent data)
            df = df.drop_duplicates(subset=['Date'], keep='first')
            
            # Sort by date for proper charting
            df = df.sort_values('Date')
            
            return df
        else:
            return None
            
    except Exception as e:
        st.error(f"Error fetching market data: {str(e)}")
        return None


def display_data_summary(df):
    """Display data summary metrics"""
    if df is None or df.empty:
        st.info("No market data available")
        return
    
    st.subheader("📊 Data Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Days", len(df))
        st.metric("Data Points", f"{len(df):,}")
    
    with col2:
        recent_data = df[df['Source'] == 'recent']
        historical_data = df[df['Source'] == 'historical']
        st.metric("Recent Data Points", len(recent_data))
        st.metric("Historical Data Points", len(historical_data))
    
    with col3:
        st.metric("Latest Close", f"${df['Close'].iloc[-1]:.2f}")
        if 'Volume' in df.columns:
            st.metric("Latest Volume", f"{df['Volume'].iloc[-1]:,}")
        else:
            st.metric("Data Points", f"{len(df):,}")
    
    with col4:
        price_change = df['Close'].iloc[-1] - df['Close'].iloc[-2] if len(df) > 1 else 0
        price_change_pct = (price_change / df['Close'].iloc[-2]) * 100 if len(df) > 1 else 0
        st.metric("Latest Change", f"${price_change:.2f} ({price_change_pct:.2f}%)")


def create_ohlc_chart(chart_data, symbol):
    """Create OHLC candlestick chart"""
    if chart_data.empty:
        st.info("No OHLC data available for charting")
        return None
    
    # Calculate dynamic y-axis range based on all OHLC data
    min_price = min(chart_data['Low'].min(), chart_data['Open'].min(), chart_data['Close'].min())
    max_price = max(chart_data['High'].max(), chart_data['Open'].max(), chart_data['Close'].max())
    price_range = max_price - min_price
    
    # Add padding to y-axis (10% on each side)
    y_padding = price_range * 0.1
    y_min = max(0, min_price - y_padding)  # Don't go below 0
    y_max = max_price + y_padding
    
    # Create the candlestick chart
    fig = go.Figure()
    
    # Add candlestick trace
    fig.add_trace(go.Candlestick(
        x=chart_data['Date'],
        open=chart_data['Open'],
        high=chart_data['High'],
        low=chart_data['Low'],
        close=chart_data['Close'],
        name='OHLC',
        increasing_line_color='#26A69A',  # Green for up days
        decreasing_line_color='#EF5350',  # Red for down days
        increasing_fillcolor='#26A69A',
        decreasing_fillcolor='#EF5350',
        line=dict(width=1),
        whiskerwidth=0
    ))
    
    # Update layout with dynamic y-axis
    fig.update_layout(
        title=f'{symbol} OHLC Candlestick Chart',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        yaxis=dict(
            range=[y_min, y_max],
            tickformat='.2f',
            tickprefix='$',
            gridcolor='lightgray',
            gridwidth=0.5
        ),
        xaxis=dict(
            gridcolor='lightgray',
            gridwidth=0.5,
            tickformat='%Y-%m-%d',
            tickangle=45
        ),
        hovermode='x unified',
        showlegend=False,
        height=600,
        margin=dict(l=50, r=50, t=50, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Add data range annotations on the chart
    start_date = chart_data['Date'].min()
    end_date = chart_data['Date'].max()
    total_days = len(chart_data)
    
    # Add annotation for data range in top-left corner
    fig.add_annotation(
        x=0.02,  # 2% from left
        y=0.98,  # 98% from bottom (top)
        xref='paper',
        yref='paper',
        text=f"Data Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}<br>Total Days: {total_days}",
        showarrow=False,
        font=dict(size=12, color='gray'),
        bgcolor='rgba(255, 255, 255, 0.8)',
        bordercolor='lightgray',
        borderwidth=1,
        align='left'
    )
    
    # Add price range annotation in top-right corner
    fig.add_annotation(
        x=0.98,  # 98% from left (right)
        y=0.98,  # 98% from bottom (top)
        xref='paper',
        yref='paper',
        text=f"Price Range: ${min_price:.2f} - ${max_price:.2f}<br>Y-Axis: ${y_min:.2f} - ${y_max:.2f}",
        showarrow=False,
        font=dict(size=12, color='gray'),
        bgcolor='rgba(255, 255, 255, 0.8)',
        bordercolor='lightgray',
        borderwidth=1,
        align='right'
    )
    
    # Custom hover template for OHLC data
    # Calculate daily changes for hover display
    chart_data['Daily_Change'] = chart_data['Close'] - chart_data['Open']
    chart_data['Daily_Change_Pct'] = (chart_data['Daily_Change'] / chart_data['Open']) * 100
    
    # Create custom hover text
    hover_text = []
    for _, row in chart_data.iterrows():
        change_text = f"${row['Daily_Change']:.2f} ({row['Daily_Change_Pct']:.2f}%)"
        hover_info = (
            f"<b>Date:</b> {row['Date'].strftime('%Y-%m-%d')}<br>" +
            f"<b>Open:</b> ${row['Open']:.2f}<br>" +
            f"<b>High:</b> ${row['High']:.2f}<br>" +
            f"<b>Low:</b> ${row['Low']:.2f}<br>" +
            f"<b>Close:</b> ${row['Close']:.2f}<br>" +
            f"<b>Change:</b> {change_text}"
        )
        
        # Add Volume to hover text if available
        if 'Volume' in chart_data.columns:
            hover_info += f"<br><b>Volume:</b> {row['Volume']:,}"
        
        hover_text.append(hover_info)
    
    # Update candlestick with custom hover text
    fig.data[0].hovertext = hover_text
    fig.data[0].hoverinfo = 'text'
    
    return fig


def display_ohlc_statistics(chart_data):
    """Display OHLC statistics"""
    if chart_data.empty:
        return
    
    # Group data by date to get proper daily statistics
    chart_data['Date_Only'] = chart_data['Date'].dt.date
    
    # Define aggregation columns based on what's available
    agg_columns = {
        'Open': 'first',  # First open of the day
        'High': 'max',    # Highest high of the day
        'Low': 'min',     # Lowest low of the day
        'Close': 'last'   # Last close of the day
    }
    
    # Add Volume aggregation only if Volume column exists
    if 'Volume' in chart_data.columns:
        agg_columns['Volume'] = 'sum'  # Total volume for the day
    
    daily_data = chart_data.groupby('Date_Only').agg(agg_columns).reset_index()
    
    # Calculate proper daily changes
    daily_data['Daily_Change'] = daily_data['Close'] - daily_data['Open']
    daily_data['Daily_Change_Pct'] = (daily_data['Daily_Change'] / daily_data['Open']) * 100
    
    st.subheader("📊 OHLC Statistics")
    
    # Display OHLC statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Highest High", f"${daily_data['High'].max():.2f}")
        st.metric("Lowest Low", f"${daily_data['Low'].min():.2f}")
    
    with col2:
        st.metric("Average Daily Range", f"${(daily_data['High'] - daily_data['Low']).mean():.2f}")
        st.metric("Max Daily Range", f"${(daily_data['High'] - daily_data['Low']).max():.2f}")
    
    with col3:
        up_days = len(daily_data[daily_data['Daily_Change'] > 0])
        down_days = len(daily_data[daily_data['Daily_Change'] < 0])
        total_days = len(daily_data)
        st.metric("Up Days", f"{up_days} ({up_days/total_days*100:.1f}%)")
        st.metric("Down Days", f"{down_days} ({down_days/total_days*100:.1f}%)")
    
    with col4:
        avg_gain = daily_data[daily_data['Daily_Change'] > 0]['Daily_Change'].mean()
        avg_loss = abs(daily_data[daily_data['Daily_Change'] < 0]['Daily_Change'].mean())
        st.metric("Avg Daily Gain", f"${avg_gain:.2f}" if not pd.isna(avg_gain) else "$0.00")
        st.metric("Avg Daily Loss", f"${avg_loss:.2f}" if not pd.isna(avg_loss) else "$0.00")
    
    # Add price range info
    min_price = min(daily_data['Low'].min(), daily_data['Open'].min(), daily_data['Close'].min())
    max_price = max(daily_data['High'].max(), daily_data['Open'].max(), daily_data['Close'].max())
    st.caption(f"Price Range: ${min_price:.2f} - ${max_price:.2f}")


def render_market_data(symbol):
    """Main function to render market data and charts"""
    df = get_consolidated_market_data(symbol)
    
    if df is not None and df.empty == False:
        display_data_summary(df)
        
        # OHLC Candlestick Chart
        st.subheader("📈 OHLC Candlestick Chart (Consolidated)")
        
        # Select columns for chart data, including Volume if available
        chart_columns = ['Date', 'Open', 'High', 'Low', 'Close']
        if 'Volume' in df.columns:
            chart_columns.append('Volume')
        
        chart_data = df[chart_columns].sort_values('Date')
        fig = create_ohlc_chart(chart_data, symbol)
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            display_ohlc_statistics(chart_data)
    else:
        st.info("No market data available for this symbol") 