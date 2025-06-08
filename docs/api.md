# API Documentation

## Overview

The Prefect Trading System integrates with multiple external APIs and provides internal APIs for data access and system control. This document details the API integrations and usage.

## External API Integrations

### 1. Alpaca API

#### Configuration
```python
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient

# Initialize clients
trading_client = TradingClient(api_key, secret_key)
data_client = StockHistoricalDataClient(api_key, secret_key)
```

#### Available Endpoints

1. **Market Data**
   ```python
   # Get historical data
   data_client.get_bars(symbol, timeframe, start, end)
   
   # Get real-time data
   data_client.get_latest_trade(symbol)
   ```

2. **Trading Operations**
   ```python
   # Place order
   trading_client.submit_order(
       symbol="AAPL",
       qty=1,
       side="buy",
       type="market",
       time_in_force="day"
   )
   ```

### 2. Yahoo Finance API

#### Configuration
```python
import yfinance as yf

# Get ticker data
ticker = yf.Ticker("AAPL")
```

#### Available Methods

1. **Historical Data**
   ```python
   # Get historical data
   ticker.history(period="1d", interval="1m")
   ```

2. **Company Information**
   ```python
   # Get company info
   ticker.info
   ```

## Internal APIs

### 1. Database API

#### Connection
```python
from src.database.database_connectivity import DatabaseConnectivity

db = DatabaseConnectivity()
```

#### Available Methods

1. **Data Retrieval**
   ```python
   # Get market data
   db.get_market_data(symbol, start_date, end_date)
   
   # Get symbol list
   db.get_symbols()
   ```

2. **Data Storage**
   ```python
   # Store market data
   db.store_market_data(data)
   
   # Update symbol status
   db.update_symbol_status(symbol, status)
   ```

### 2. WebSocket API

#### Connection
```python
from src.data.alpaca_websocket import websocket_connection

# Start WebSocket connection
asyncio.run(websocket_connection())
```

#### Available Events

1. **Trade Events**
   ```python
   async def on_trade(trade):
       # Handle trade data
       pass
   ```

2. **Quote Events**
   ```python
   async def on_quote(quote):
       # Handle quote data
       pass
   ```

## Error Handling

### API Rate Limits

1. **Alpaca API**
   - 200 requests per minute for market data
   - 100 requests per minute for trading operations

2. **Yahoo Finance API**
   - 2,000 requests per hour per IP
   - 100 requests per minute per IP

### Error Codes

1. **Database Errors**
   - `DB001`: Connection failed
   - `DB002`: Query execution failed
   - `DB003`: Data validation failed

2. **API Errors**
   - `API001`: Rate limit exceeded
   - `API002`: Authentication failed
   - `API003`: Invalid request

## Best Practices

1. **Rate Limiting**
   - Implement exponential backoff
   - Use connection pooling
   - Cache frequently accessed data

2. **Error Handling**
   - Implement retry mechanisms
   - Log all API interactions
   - Monitor API usage

3. **Security**
   - Never expose API keys in code
   - Use environment variables
   - Implement request validation

## Examples

### Complete Market Data Collection
```python
from src.data.sources.alpaca_daily_loader import AlpacaDailyLoader
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader

# Initialize loaders
alpaca_loader = AlpacaDailyLoader()
yahoo_loader = YahooFinanceDataLoader()

# Collect data
alpaca_data = alpaca_loader.run_daily_load()
yahoo_data = yahoo_loader.run()

# Process and store data
db.store_market_data(alpaca_data)
db.store_market_data(yahoo_data)
```

### Real-time Data Processing
```python
async def process_market_data():
    async with websocket_connection() as ws:
        async for message in ws:
            if message.type == "trade":
                await process_trade(message.data)
            elif message.type == "quote":
                await process_quote(message.data)
``` 