# Prefect Trading System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Prefect 3.4.0](https://img.shields.io/badge/prefect-3.4.0-green.svg)](https://www.prefect.io/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-12+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A comprehensive trading system built with **Prefect** for automated market data collection, processing, and analysis, featuring a modern **Streamlit**-based user interface for real-time monitoring and portfolio management.

## 🚀 Features

### 📊 Data Collection & Processing
- **Multi-Source Integration**
  - Yahoo Finance data collection with company information
  - Alpaca market data integration (paper and live trading)
  - Real-time market data via WebSocket
  - News API integration for market headlines

- **Automated Workflows**
  - Hourly data processing (9AM-3PM EST weekdays)
  - End-of-Day (EOD) processing (6PM EST weekdays)
  - Symbol maintenance and delisting checks
  - Real-time market data streaming (9:30AM EST weekdays)

### 🎨 User Interface
- **Modern Streamlit Dashboard**
  - Real-time market data visualization with auto-refresh
  - Portfolio overview with performance metrics
  - Market overview with major indices and tech leaders
  - Recent trading activity tracking
  - Market news feed with article previews
  - Interactive symbol selector
  - Responsive design for all devices

### 🗄️ Database & Storage
- **PostgreSQL Integration**
  - Comprehensive market data storage
  - Company information and officer data
  - News articles with full metadata
  - Optimized queries with proper indexing
  - Connection pooling and error handling

### ⚙️ System Management
- **Prefect Orchestration**
  - Scheduled workflow execution
  - Task dependency management
  - Comprehensive logging and monitoring
  - Secret management for API credentials
  - Error handling and retry logic

## 📁 Project Structure

```
prefect-trading/
├── 📁 config/                    # Configuration files
│   ├── config.yaml              # Application configuration
│   └── streamlit_style.css      # UI styling
├── 📁 docs/                     # Documentation
│   ├── api.md                   # API documentation
│   ├── architecture.md          # System architecture
│   ├── development.md           # Development guide
│   ├── setup.md                 # Setup instructions
│   ├── testing.md               # Testing documentation
│   └── ui.md                    # UI documentation
├── 📁 src/                      # Source code
│   ├── 📁 data/                 # Data collection and processing
│   │   ├── 📁 sources/          # Data source integrations
│   │   │   ├── alpaca_daily_loader.py
│   │   │   ├── alpaca_historical_loader.py
│   │   │   ├── alpaca_websocket.py
│   │   │   ├── hourly_persistence.py
│   │   │   ├── news.py
│   │   │   ├── symbol_manager.py
│   │   │   └── yahoo_finance_loader.py
│   │   └── yahoo_raw_data.csv
│   ├── 📁 database/             # Database connectivity and operations
│   │   ├── 📁 migrations/       # Database schema migrations
│   │   ├── database_connectivity.py
│   │   └── 📁 sql/
│   ├── 📁 scripts/              # Utility scripts
│   ├── 📁 ui/                   # User interface components
│   │   ├── 📁 components/       # Reusable UI components
│   │   ├── home.py              # Main dashboard page
│   │   └── streamlit_app.py     # Streamlit application
│   └── 📁 utils/                # Utility functions
├── 📁 test/                     # Test suite
│   ├── 📁 unit/                 # Unit tests
│   ├── 📁 integration/          # Integration tests
│   ├── 📁 e2e/                  # End-to-end tests
│   └── conftest.py              # Test configuration
├── main.py                      # Main entry point with Prefect flows
├── prefect.yaml                 # Prefect workflow configuration
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── pytest.ini                  # Pytest configuration
└── README.md                   # This file
```

## 🛠️ Prerequisites

- **Python 3.9** or higher
- **PostgreSQL 12** or higher
- **Prefect 3.4.0** or higher
- **Alpaca API** credentials
- **Yahoo Finance API** access
- **NewsAPI** credentials (optional but recommended)

## ⚡ Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/your-username/prefect-trading.git
cd prefect-trading

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### 2. Configuration
```bash
# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Set up Prefect blocks
python -c "
from prefect.blocks.system import String
String(value='your_alpaca_key').save(name='alpaca-api-key')
String(value='your_alpaca_secret').save(name='alpaca-secret-key')
String(value='your_news_api_key').save(name='newsapi')
"
```

### 3. Database Setup
```bash
# Create database
createdb trading_db

# Run migrations
psql -d trading_db -f src/database/migrations/001_initial_schema/001_create_tables.sql
# ... (run all migration files in order)
```

### 4. Start the System
```bash
# Start Prefect server
prefect server start

# Deploy workflows
prefect deploy

# Start the Streamlit UI
streamlit run src/ui/streamlit_app.py
```

## 🎯 Usage

### Running Workflows
```python
from main import hourly_process_flow, eod_process_flow, market_data_websocket_flow

# Start hourly processing
hourly_process_flow()

# Start end-of-day processing
eod_process_flow()

# Start real-time data collection
market_data_websocket_flow()
```

### Using the Dashboard
1. Open `http://localhost:8501` in your browser
2. Navigate through the dashboard sections:
   - **Home**: Overview of portfolio and market data
   - **Analysis**: Data analysis and trading signals
   - **Settings**: System configuration

### Monitoring
- **Prefect UI**: `http://localhost:4200` - Monitor workflow execution
- **Streamlit Dashboard**: `http://localhost:8501` - View real-time data
- **Logs**: Check `logs/trading_system.log` for detailed logs

## ⚙️ Configuration

### Environment Variables
```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_db
DB_USER=your_username
DB_PASSWORD=your_password

# APIs
ALPACA_API_KEY=your_api_key
ALPACA_SECRET_KEY=your_secret_key
NEWS_API_KEY=your_news_api_key

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### Prefect Configuration
The system uses Prefect for workflow orchestration with three main deployments:
- **hourly-process-flow**: Runs every hour during market hours
- **eod-data-ingestion**: Runs daily at market close
- **market-data-websocket**: Runs at market open for real-time data

## 🧪 Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### Code Quality
```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/

# Run pre-commit hooks
pre-commit run --all-files
```

### Development Workflow
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and add tests
3. Run quality checks: `pre-commit run --all-files`
4. Submit pull request

## 📚 Documentation

- **[API Documentation](docs/api.md)**: External and internal API usage
- **[Architecture](docs/architecture.md)**: System design and components
- **[Development Guide](docs/development.md)**: Development practices and workflows
- **[Setup Guide](docs/setup.md)**: Installation and configuration
- **[Testing Guide](docs/testing.md)**: Testing strategies and implementation
- **[UI Documentation](docs/ui.md)**: User interface components and features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive tests for new features
- Update documentation for API changes
- Ensure UI components are responsive and accessible
- Implement proper error handling

## 🐛 Troubleshooting

### Common Issues
- **Database Connection**: Verify PostgreSQL is running and credentials are correct
- **API Errors**: Check API keys and rate limits
- **Prefect Issues**: Ensure Prefect server is running and workflows are deployed
- **UI Problems**: Check Streamlit dependencies and CSS file paths

### Getting Help
- Check the [documentation](docs/) for detailed guides
- Review [GitHub Issues](https://github.com/your-repo/issues) for known problems
- Contact the development team for support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Prefect](https://www.prefect.io/) for workflow orchestration
- [Streamlit](https://streamlit.io/) for the user interface
- [Alpaca](https://alpaca.markets/) for market data
- [Yahoo Finance](https://finance.yahoo.com/) for financial data
- [NewsAPI](https://newsapi.org/) for market news

## 📊 Project Status

- **Version**: 1.0.0
- **Status**: Active Development
- **Last Updated**: December 2024
- **Python Support**: 3.9+
- **Database**: PostgreSQL 12+

## Streamlit UI Testing (Simplified)

All Streamlit UI tests are now located in a single file:

- `test/unit/ui/test_simple_streamlit.py`

### How to Run All Tests

From the project root, run:

```bash
python scripts/run_tests.py simple
```

This will:
- Set up the test environment
- Run all basic Streamlit UI tests
- Check code coverage (minimum 20%)

### Troubleshooting

If you see an error like:

```
error: unrecognized arguments: --cov=src/ui --cov-report=term-missing ...
```

You need to install the `pytest-cov` plugin:

```bash
pip install pytest-cov
```

### Notes
- All other UI test files have been removed for simplicity.
- Add new Streamlit UI tests to `test_simple_streamlit.py`.
- The test runner script (`scripts/run_tests.py`) is now the only way to run UI tests.

---

For more details, see the rest of this README and the `docs/` directory. 