# Portfolio Management

## Overview

The Portfolio Management system provides comprehensive portfolio tracking and analysis using real-time data from your Alpaca trading account. It replaces the dummy data previously shown on the home page with actual account information, positions, and performance metrics.

## Features

### 1. Real-Time Portfolio Data
- **Account Overview**: Portfolio value, cash, buying power, equity
- **Current Positions**: All open positions with real-time pricing and P&L
- **Trading History**: Recent orders and performance metrics
- **Risk Analysis**: Margin utilization, position concentration, and risk warnings

### 2. Portfolio Dashboard (Home Page)
The home page now displays:
- Real portfolio value and daily P&L
- Actual number of open positions
- Calculated win rate from trading history
- Recent trading activity from your account
- Additional metrics like margin usage and buying power

### 3. Comprehensive Portfolio Page
A dedicated portfolio page provides:
- **Account Overview**: Detailed account information and status
- **Position Table**: Complete list of positions with P&L calculations
- **Portfolio Allocation**: Pie chart showing position distribution
- **Trading History**: Detailed order history and performance metrics
- **Risk Analysis**: Comprehensive risk metrics and warnings

## Setup

### 1. Alpaca API Configuration
Ensure your Alpaca API credentials are properly configured in `config/.env`:

```bash
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret_key
```

### 2. Testing the Connection
Run the test script to verify your setup:

```bash
python scripts/test_portfolio.py
```

This will test:
- API connection to Alpaca
- Account information retrieval
- Position data fetching
- Portfolio metrics calculation

## Usage

### Home Page
The home page automatically displays your real portfolio data:
- Portfolio overview with key metrics
- Recent trading activity
- Quick access to portfolio details

### Portfolio Page
Navigate to the "Portfolio" page in the sidebar for detailed analysis:

1. **Account Overview**: View account balance, buying power, and status
2. **Positions**: See all current positions with P&L
3. **Allocation**: Visual representation of portfolio distribution
4. **Trading History**: Review recent trades and performance
5. **Risk Analysis**: Monitor risk metrics and warnings

## Portfolio Metrics

### Key Metrics Displayed
- **Total Value**: Portfolio value including cash and positions
- **Daily P&L**: Unrealized profit/loss for current positions
- **Open Positions**: Number of active positions
- **Win Rate**: Percentage of profitable trades
- **Buying Power**: Available funds for new trades
- **Margin Used**: Percentage of portfolio using margin

### Risk Metrics
- **Margin Utilization**: Percentage of portfolio using margin
- **Position Concentration**: Largest position as percentage of portfolio
- **Pattern Day Trader Status**: PDT restrictions and warnings
- **Trading Status**: Account trading permissions

## Data Sources

### Alpaca API Integration
The portfolio system integrates with Alpaca's API to fetch:
- Account information and balance
- Current positions and pricing
- Order history and fills
- Real-time market data for calculations

### Data Refresh
- Home page refreshes every 10 seconds
- Portfolio page loads fresh data on each visit
- All data is fetched directly from Alpaca API

## Error Handling

### Fallback Behavior
If the Alpaca API is unavailable or credentials are invalid:
- Home page shows error message with fallback to dummy data
- Portfolio page displays error with troubleshooting tips
- Test script provides detailed error information

### Common Issues
1. **Invalid API Credentials**: Check your Alpaca API key and secret
2. **Network Issues**: Verify internet connection and API accessibility
3. **Account Status**: Ensure your Alpaca account is active
4. **Rate Limits**: Alpaca API has rate limits for data requests

## Technical Implementation

### PortfolioManager Class
Located in `src/data/sources/portfolio_manager.py`:
- Manages Alpaca API connections
- Fetches account and position data
- Calculates portfolio metrics
- Provides data for UI components

### UI Components
- **Home Page**: `src/ui/home.py` - Updated to use real data
- **Portfolio Page**: `src/ui/portfolio.py` - New comprehensive portfolio view
- **Main App**: `src/ui/streamlit_app.py` - Updated navigation

### Dependencies
- `alpaca-py`: Alpaca API client
- `plotly`: Chart generation for portfolio allocation
- `pandas`: Data processing and analysis
- `streamlit`: UI framework

## Future Enhancements

### Planned Features
1. **Historical Performance**: Portfolio performance over time
2. **Sector Analysis**: Position allocation by sector
3. **Performance Charts**: Interactive charts for portfolio growth
4. **Trade Analysis**: Detailed analysis of individual trades
5. **Risk Alerts**: Real-time risk notifications
6. **Portfolio Rebalancing**: Tools for portfolio optimization

### Integration Opportunities
1. **Database Storage**: Store historical portfolio data locally
2. **Performance Tracking**: Track portfolio performance over time
3. **Automated Alerts**: Set up alerts for portfolio changes
4. **Reporting**: Generate detailed portfolio reports
5. **Backtesting**: Test trading strategies on historical data

## Troubleshooting

### Common Problems

1. **"0 orders found" when you have open orders**
   This is the most common issue and is almost always caused by an **API key mismatch**. You might be viewing one paper account in your web browser, but your `config/.env` file is using keys for a *different* paper account.

   **Solution:**
   - **Log in to your Alpaca paper trading dashboard.**
   - **Navigate to the API Keys section.**
   - **Regenerate your API keys.** You will only see the secret key once, so copy it immediately.
   - **Paste the new API Key and Secret Key** into your `config/.env` file.
   - This guarantees you are using the correct keys for the account you are viewing.

2. **"Unable to fetch portfolio data"**
   - Check that your Alpaca API credentials in `config/.env` are correct.
   - Verify your internet connection.
   - Ensure your Alpaca account is active and that you have agreed to the latest terms of service.

3. **"Error loading portfolio data"**
   - Run the test script for detailed error information: `python scripts/test_portfolio.py`
   - Check the logs in the `logs/` directory for detailed error messages and tracebacks.
   - Make sure the Alpaca API service is operational by checking their status page.

### Getting Help
1. **Run the test script:** `python scripts/test_portfolio.py`
2. Check the logs for detailed error messages.
3. Verify your Alpaca account status and that your API keys match the account you are viewing.
4. Ensure you have run `pip install -r config/requirements.txt` to install all necessary dependencies.

## Security Notes

- API credentials are stored in environment variables
- No sensitive data is logged or displayed
- All API calls use secure HTTPS connections
- Credentials are not stored in the codebase 