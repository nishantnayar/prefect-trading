# Setup and Configuration Guide

## Overview

This guide provides comprehensive setup instructions for the Prefect Trading System, from quick start for new developers to detailed configuration for production environments.

> **📋 Quick Links**: [Architecture Decisions](architecture-decisions.md) | [Development Guide](development.md) | [Testing Guide](testing.md) | [UI Documentation](ui.md) | [API Documentation](api.md)

## Quick Start (30 minutes)

### Prerequisites Check

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher**
- **PostgreSQL 12 or higher**
- **Git**
- **Docker** (optional, for containerized development)

```bash
# Check Python version
python --version

# Check if PostgreSQL is running
psql --version

# Check if Git is installed
git --version
```

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-username/prefect-trading.git
cd prefect-trading

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Install all dependencies
make install-dev

# Or manually:
pip install -r config/requirements.txt
pip install -r config/requirements-dev.txt
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp config/env.example .env

# Edit the .env file with your credentials
# You'll need:
# - Database credentials
# - Alpaca API keys
# - News API key (optional)
```

### Required API Keys

1. **Alpaca Markets** (Required)
   - Sign up at [alpaca.markets](https://alpaca.markets)
   - Get your API key and secret
   - Use paper trading for development

2. **NewsAPI** (Optional)
   - Sign up at [newsapi.org](https://newsapi.org)
   - Get your API key

### Step 4: Database Setup

```bash
# Create database
createdb trading_db

# Run migrations
make db-migrate

# Or manually run each migration file:
psql -d trading_db -f src/database/migrations/001_initial_schema/001_create_tables.sql
psql -d trading_db -f src/database/migrations/001_initial_schema/002_create_market_data.sql
# ... (continue with all migration files)
```

### Step 5: Configure Prefect

```bash
# Start Prefect server
make run-prefect

# In a new terminal, configure Prefect blocks
python -c "
from prefect.blocks.system import String
String(value='your_alpaca_key').save(name='alpaca-api-key')
String(value='your_alpaca_secret').save(name='alpaca-secret-key')
String(value='your_news_api_key').save(name='newsapi')
"
```

### Step 6: Start the Application

```bash
# Start the Streamlit UI
make run-ui

# Or manually:
streamlit run src/ui/streamlit_app.py
```

### Step 7: Verify Installation

1. **Check Prefect UI**: Open [http://localhost:4200](http://localhost:4200)
2. **Check Streamlit UI**: Open [http://localhost:8501](http://localhost:8501)
3. **Run Tests**: `make test` or `python scripts/run_tests.py`

## MLflow Setup (Optional but Recommended)

For enterprise-level model management and periodic rebaselining:

```bash
# Create MLflow database
createdb mlflow_db

# Start MLflow server
mlflow server --backend-store-uri postgresql://postgres:nishant@localhost/mlflow_db --default-artifact-root file:./mlruns --host 0.0.0.0 --port 5000

# Set environment variable
export MLFLOW_TRACKING_URI=http://localhost:5000
```

For more details on MLflow integration, see [Architecture Decisions](architecture-decisions.md).

## Detailed Setup

### Environment Setup

#### Prerequisites
1. Python 3.9 or higher
2. PostgreSQL 12 or higher
3. Git
4. Access to Alpaca API
5. Access to Yahoo Finance API
6. Access to NewsAPI (optional but recommended)

#### Installation Steps

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
   pip install -r config/requirements.txt
   pip install -r config/requirements-dev.txt  # For development
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
   # Run consolidated migrations (recommended)
   make db-migrate-consolidated
   
   # Or run migrations manually
   psql -d trading_db -f src/database/migrations/001_initial_schema_consolidated.sql
   psql -d trading_db -f src/database/migrations/002_data_source_enhancement_consolidated.sql
   psql -d trading_db -f src/database/migrations/003_historical_data_consolidated.sql
   
   # Verify schema matches migrations
   make db-verify
   
   # Quick database health check
   make db-check
   ```

**Understanding Verification Results**:
- **✅ PASSED**: All application tables from migrations are present and correct
- **⚠️ EXTRA TABLES**: These are typically system tables (Prefect, MLflow, etc.) and are expected - not a problem
- **❌ MISSING TABLES**: These indicate actual schema mismatches that need attention
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

# MLflow Configuration
mlflow:
  tracking_uri: ${MLFLOW_TRACKING_URI:http://localhost:5000}
  experiment_name: "pairs_trading"
  model_name: "pairs_trading_gru_garch_technology_v1"

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

## Development Setup

### 1. Install Development Dependencies
```bash
pip install -r config/requirements-dev.txt
```

### 2. Set Up Pre-commit Hooks
```bash
pre-commit install
```

### 3. Run Tests
```bash
# Run all tests
python scripts/run_tests.py

# Run with coverage
pytest --cov=src test/

# Run specific test file
pytest test/unit/test_market_data.py
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

### 3. Access MLflow UI (if configured)
- Open `http://localhost:5000` in your browser
- View experiments and model runs
- Track model performance and artifacts

### 4. View Logs
```bash
# Prefect logs
prefect logs

# Application logs
tail -f logs/trading_system.log
```

## Common Issues and Solutions

### Database Connection Issues

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if needed
sudo systemctl start postgresql

# Check connection
psql -h localhost -U your_username -d trading_db
```

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8501
lsof -i :4200
lsof -i :5000  # MLflow

# Kill the process
kill -9 <PID>
```

### Missing Dependencies

```bash
# Reinstall dependencies
pip install --upgrade -r config/requirements.txt
pip install --upgrade -r config/requirements-dev.txt
```

### API Connection Issues
- Verify API keys are correct
- Check network connectivity
- Validate API endpoints
- Check rate limits

### Prefect Server Issues
- Ensure Prefect server is running
- Check Prefect configuration
- Verify workflow deployments
- Check work pool configuration

### Streamlit UI Issues
- Verify all dependencies are installed
- Check CSS file path
- Ensure database connectivity
- Check auto-refresh settings

### MLflow Issues
- Ensure MLflow server is running
- Check MLFLOW_TRACKING_URI environment variable
- Verify database connectivity for MLflow
- Check artifact storage permissions

### News API Issues
- Verify NewsAPI key is valid
- Check rate limits (1,000 requests/day free tier)
- Ensure proper error handling

## Development Workflow

### 1. Make Changes

```bash
# Create a feature branch
git checkout -b feature/your-feature

# Make your changes
# ...

# Format code
make format

# Run tests
python scripts/run_tests.py
```

### 2. Commit Changes

```bash
# Add changes
git add .

# Commit with conventional commit message
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/your-feature
```

### 3. Create Pull Request

- Go to GitHub and create a pull request
- Ensure all tests pass
- Request code review

## Useful Commands

### Development Commands

```bash
# Run all tests
python scripts/run_tests.py

# Run specific test categories
python scripts/run_tests.py basic
python scripts/run_tests.py database
python scripts/run_tests.py quick

# Format code
make format

# Lint code
make lint

# Check security
make security-check

# Clean up
make clean
```

### Database Commands

```bash
# Reset database
make db-reset

# Run migrations
make db-migrate

# Backup database
make backup

# Restore database
make restore BACKUP_FILE=backup_20241201_143022.sql
```

### Monitoring Commands

```bash
# View logs
make logs

# Check system status
prefect server status

# Monitor workflows
prefect deployment ls
```

## Support

For additional support:
1. Check the [GitHub Issues](https://github.com/your-repo/issues)
2. Review the [Architecture Decisions](architecture-decisions.md) for design rationale
3. Check the [Development Guide](development.md) for coding standards
4. Review the [Testing Guide](testing.md) for testing strategies
5. Check the [Prefect Documentation](https://docs.prefect.io/)
6. Check the [Streamlit Documentation](https://docs.streamlit.io/)
7. Contact the development team 