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
   
   # Get company officers
   ticker.officers
   ```

### 3. News API

#### Configuration
```python
from newsapi import NewsApiClient
from prefect.blocks.system import Secret

# Load API key from Prefect secrets
api_key = Secret.load("newsapi").get()
newsapi = NewsApiClient(api_key=api_key)
```

#### Available Methods

1. **Top Headlines**
   ```python
   # Get top headlines
   headlines = newsapi.get_top_headlines(
       q='stock market',
       category='business',
       language='en',
       country='us'
   )
   ```

2. **Everything Search**
   ```python
   # Search for articles
   articles = newsapi.get_everything(
       q='AAPL',
       from_param='2024-01-01',
       to='2024-12-31',
       language='en',
       sort_by='relevancy'
   )
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
   
   # Get news articles
   db.get_news_articles(limit=10)
   ```

2. **Data Storage**
   ```python
   # Store market data
   db.store_market_data(data)
   
   # Store company information
   db.store_company_info(company_data)
   
   # Store news articles
   db.store_news_articles(articles)
   ```

### 2. WebSocket API

#### Connection

```python
from src.data.sources.alpaca_websocket import websocket_connection

# Start WebSocket connection
asyncio.run(websocket_connection())
```

#### Available Events

1. **Trade Events**
   ```python
   async def on_trade(trade):
       # Handle trade data
       print(f"Trade: {trade.symbol} @ {trade.price}")
   ```

2. **Quote Events**
   ```python
   async def on_quote(quote):
       # Handle quote data
       print(f"Quote: {quote.symbol} bid={quote.bid} ask={quote.ask}")
   ```

### 3. Data Loader APIs

#### Alpaca Daily Loader
```python
from src.data.sources.alpaca_daily_loader import AlpacaDailyLoader

loader = AlpacaDailyLoader()
data = loader.get_previous_day_data(symbols=['AAPL', 'MSFT'])
loader.store_market_data(data)
```

#### Yahoo Finance Loader
```python
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader

loader = YahooFinanceDataLoader()
company_info = loader.load_ticker_info_chunk(['AAPL', 'MSFT'])
loader.store_company_info(company_info)
```

#### News Loader
```python
from src.data.sources.news import NewsLoader

loader = NewsLoader()
articles = loader.fetch_and_store_news(
    query='stock market',
    category='business',
    language='en',
    country='us'
)
```

## Error Handling

### API Rate Limits

1. **Alpaca API**
   - 200 requests per minute for market data
   - 100 requests per minute for trading operations

2. **Yahoo Finance API**
   - 2,000 requests per hour per IP
   - 100 requests per minute per IP

3. **News API**
   - 1,000 requests per day (free tier)
   - 100 requests per minute

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
   - Use Prefect secrets for sensitive data
   - Implement request validation

## Examples

### Complete Market Data Collection
```python
from src.data.sources.alpaca_daily_loader import AlpacaDailyLoader
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader
from src.data.sources.news import NewsLoader

# Initialize loaders
alpaca_loader = AlpacaDailyLoader()
yahoo_loader = YahooFinanceDataLoader()
news_loader = NewsLoader()

# Collect data
alpaca_data = alpaca_loader.get_previous_day_data(['AAPL', 'MSFT'])
yahoo_data = yahoo_loader.load_ticker_info_chunk(['AAPL', 'MSFT'])
news_articles = news_loader.fetch_and_store_news()

# Store data
alpaca_loader.store_market_data(alpaca_data)
yahoo_loader.store_company_info(yahoo_data)
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

### Database Operations
```python
from src.database.database_connectivity import DatabaseConnectivity

db = DatabaseConnectivity()

# Get recent market data
with db.get_session() as cursor:
    cursor.execute("""
        SELECT * FROM market_data 
        WHERE symbol = %s 
        ORDER BY timestamp DESC 
        LIMIT 100
    """, ('AAPL',))
    data = cursor.fetchall()

# Get recent news
with db.get_session() as cursor:
    cursor.execute("""
        SELECT title, source_name, published_at 
        FROM news_articles 
        ORDER BY published_at DESC 
        LIMIT 10
    """)
    news = cursor.fetchall()
``` 