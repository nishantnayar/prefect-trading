# Setup and Configuration Guide

## Environment Setup

### Prerequisites
1. Python 3.9 or higher
2. PostgreSQL 12 or higher
3. Git
4. Access to Alpaca API
5. Access to Yahoo Finance API
6. Access to NewsAPI (optional but recommended)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd prefect-trading
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. **Set Up Environment Variables**
   Create a `.env` file in the project root:
   ```env
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=trading_db
   DB_USER=your_username
   DB_PASSWORD=your_password

   # Alpaca Configuration
   ALPACA_API_KEY=your_api_key
   ALPACA_SECRET_KEY=your_secret_key
   ALPACA_BASE_URL=https://paper-api.alpaca.markets

   # News API Configuration (Optional)
   NEWS_API_KEY=your_news_api_key

   # Prefect Configuration
   PREFECT_API_URL=http://localhost:4200/api

   # Application Settings
   ENVIRONMENT=development
   DEBUG=true
   LOG_LEVEL=INFO
   ```

## Prefect Setup

1. **Install Prefect**
   ```bash
   pip install prefect
   ```

2. **Start Prefect Server**
   ```bash
   prefect server start
   ```

3. **Configure Prefect**
   ```bash
   prefect config set PREFECT_API_URL=http://localhost:4200/api
   ```

4. **Create Prefect Blocks**
   ```python
   from prefect.blocks.system import String
   
   # Create database connection block
   db_connection = String(value="postgresql://user:password@localhost:5432/dbname")
   db_connection.save(name="database-connection")
   
   # Create Alpaca credentials blocks
   alpaca_key = String(value="your_api_key")
   alpaca_key.save(name="alpaca-api-key")
   
   alpaca_secret = String(value="your_secret_key")
   alpaca_secret.save(name="alpaca-secret-key")
   
   # Create News API credentials block (optional)
   news_api_key = String(value="your_news_api_key")
   news_api_key.save(name="newsapi")
   ```

## Database Setup

1. **Create Database**
   ```sql
   CREATE DATABASE trading_db;
   ```

2. **Initialize Schema**
   ```bash
   # Run all migration files in order
   psql -d trading_db -f src/database/migrations/001_initial_schema/001_create_tables.sql
   psql -d trading_db -f src/database/migrations/001_initial_schema/002_create_market_data.sql
   psql -d trading_db -f src/database/migrations/001_initial_schema/003_create_symbols.sql
   psql -d trading_db -f src/database/migrations/001_initial_schema/004_add_constraints.sql
   psql -d trading_db -f src/database/migrations/001_initial_schema/005_create_yahoo_company_info.sql
   psql -d trading_db -f src/database/migrations/001_initial_schema/006_create_yahoo_company_officers.sql
   psql -d trading_db -f src/database/migrations/001_initial_schema/007_create_news_articles.sql
   ```

## Configuration Files

### 1. Prefect Configuration (`prefect.yaml`)
```yaml
name: tradingsystem
prefect-version: 3.4.0

pull:
- prefect.deployments.steps.git_clone:
    repository: https://github.com/nishantnayar/prefect-trading.git
    branch: main

deployments:
- name: hourly-process-flow
  version: 1.0.0
  tags: ["hourly", "data"]
  description: "Ingests hourly market data"
  schedule:
    cron: "1 9-15 * * 1-5"  # Every hour from 9AM-3PM EST Mon-Fri
    timezone: America/New_York
  flow_name: hourly_process_flow
  entrypoint: "main.py:hourly_process_flow"
  parameters: {}
  work_pool:
    name: hourly
    work_queue_name: default

- name: eod-data-ingestion
  version: 1.0.0
  tags: ["eod", "data"]
  description: "Ingests End of Day"
  schedule:
    cron: "0 18 * * 1-5"  # 6PM EST Mon-Fri
    timezone: America/New_York
  flow_name: eod_process_flow
  entrypoint: "main.py:eod_process_flow"
  parameters: {}
  work_pool:
    name: endofday
    work_queue_name: default

- name: market-data-websocket
  version: 1.0.0
  tags: ["realtime", "data"]
  description: "Collects real-time market data via WebSocket"
  schedule:
    cron: "30 9 * * 1-5"  # 9:30AM EST Mon-Fri
    timezone: America/New_York
  flow_name: market_data_websocket_flow
  entrypoint: "main.py:market_data_websocket_flow"
  parameters: {}
  work_pool:
    name: realtime
    work_queue_name: default
```

### 2. Application Configuration (`config/config.yaml`)
```yaml
# Database Configuration
database:
  host: localhost
  port: 5432
  name: trading_system
  user: ${DB_USER}
  password: ${DB_PASSWORD}
  pool_size: 5
  max_overflow: 10

# Alpaca Configuration
alpaca:
  api_key: ${ALPACA_API_KEY}
  secret_key: ${ALPACA_SECRET_KEY}
  base_url: https://paper-api.alpaca.markets
  data_url: "https://data.alpaca.markets"

# Application Settings
app:
  environment: ${ENVIRONMENT}
  debug: ${DEBUG}
  log_level: ${LOG_LEVEL}

# Data Collection Settings
data_collection:
  interval_minutes: 60
  symbols:
    - AAPL
    - MSFT
    - GOOGL
    - AMZN
    - META

# Logging Configuration
logging:
  level: INFO
  format: "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
  log_dir: "${REPO_ROOT}/logs"
  log_file: "trading_system.log"
  rotation: "500 MB"
  retention: "10 days"
  compression: "zip"
  max_age_days: 3
```

## Running the System

### 1. Start Prefect Server
```bash
prefect server start
```

### 2. Deploy Workflows
```bash
prefect deploy
```

### 3. Start Workflows
```bash
# Start hourly processing
prefect deployment run "tradingsystem/hourly-process-flow"

# Start end-of-day processing
prefect deployment run "tradingsystem/eod-data-ingestion"

# Start real-time data collection
prefect deployment run "tradingsystem/market-data-websocket"
```

### 4. Run Streamlit UI
```bash
# Start the Streamlit dashboard
streamlit run src/ui/streamlit_app.py
```

The UI will be available at `http://localhost:8501`

## Monitoring

### 1. Access Prefect UI
- Open `http://localhost:4200` in your browser
- Monitor workflow runs and task execution
- View logs and error messages

### 2. Access Streamlit Dashboard
- Open `http://localhost:8501` in your browser
- View real-time market data
- Monitor portfolio status
- Read market news

### 3. View Logs
```bash
# Prefect logs
prefect logs

# Application logs
tail -f logs/trading_system.log
```

## Development Setup

### 1. Install Development Dependencies
```bash
pip install -r requirements-dev.txt
```

### 2. Set Up Pre-commit Hooks
```bash
pre-commit install
```

### 3. Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_market_data.py
```

### 4. Code Quality Checks
```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check database credentials
   - Ensure database exists
   - Verify connection pooling settings

2. **API Connection Issues**
   - Verify API keys are correct
   - Check network connectivity
   - Validate API endpoints
   - Check rate limits

3. **Prefect Server Issues**
   - Ensure Prefect server is running
   - Check Prefect configuration
   - Verify workflow deployments
   - Check work pool configuration

4. **Streamlit UI Issues**
   - Verify all dependencies are installed
   - Check CSS file path
   - Ensure database connectivity
   - Check auto-refresh settings

5. **News API Issues**
   - Verify NewsAPI key is valid
   - Check rate limits (1,000 requests/day free tier)
   - Ensure proper error handling

### Support

For additional support:
1. Check the [GitHub Issues](https://github.com/your-repo/issues)
2. Review the [Prefect Documentation](https://docs.prefect.io/)
3. Check the [Streamlit Documentation](https://docs.streamlit.io/)
4. Contact the development team 