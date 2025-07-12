# Prefect Trading System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Prefect 3.4.0](https://img.shields.io/badge/prefect-3.4.0-green.svg)](https://www.prefect.io/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-12+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📎 Quick Links
- [Setup Guide](docs/setup.md)
- [Development Guide](docs/development.md)
- [Testing Guide](docs/testing.md)
- [UI Documentation](docs/ui.md)
- [Data Systems](docs/data-systems.md)
- [Architecture Decisions](docs/architecture-decisions.md)
- [API Documentation](docs/api.md)

---

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
  - **5 Main Pages**: Home, Portfolio, Analysis, Testing, Settings
  - **Testing Integration**: Built-in testing results and coverage visualization
  - **Portfolio Management**: Comprehensive portfolio tracking and analysis

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

### 🤖 Machine Learning & Model Management
- **PyTorch GRU Models**
  - Pairs trading signal generation
  - GARCH-GRU hybrid architecture
  - Real-time model inference
  - Comprehensive model training pipeline
- **MLflow Integration**
  - Experiment tracking and model versioning
  - Automated model registry management
  - Performance monitoring and comparison
  - Descriptive run naming and tagging

## 📁 Project Structure

The project follows a clean, organized structure with configuration files centralized and build artifacts contained. For rationale behind major architectural choices, see [Architecture Decisions](docs/architecture-decisions.md).

```
prefect-trading/
├── 📁 config/                    # Configuration files
│   ├── config.yaml              # Application configuration
│   ├── streamlit_style.css      # UI styling
│   ├── pytest.ini              # Pytest configuration
│   ├── prefect.yaml            # Prefect workflow configuration
│   ├── .pre-commit-config.yaml # Pre-commit hooks
│   ├── requirements.txt         # Production dependencies
│   └── requirements-dev.txt     # Development dependencies
├── 📁 build/                    # Build artifacts and reports
│   ├── coverage.json           # Coverage reports
│   ├── test_results.json       # Test results
│   ├── .coverage              # Coverage data
│   └── htmlcov/               # HTML coverage reports
├── 📁 docs/                     # Documentation
│   ├── api.md                   # API documentation and integrations
│   ├── architecture-decisions.md # Architecture decisions and implementation planning
│   ├── data-systems.md          # Data recycler system and GARCH pairs trading
│   ├── development.md           # Development guide
│   ├── setup.md                 # Setup instructions
│   ├── testing.md               # Comprehensive testing guide
│   └── ui.md                    # UI documentation (includes portfolio management)
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
│   ├── 📁 ml/                   # Machine learning components
│   │   ├── gru_model.py         # PyTorch GRU model implementation
│   │   ├── train_gru_models.py  # Training pipeline with MLflow
│   │   └── config.py            # MLflow configuration
│   ├── 📁 ui/                   # User interface components
│   │   ├── 📁 components/       # Reusable UI components
│   │   ├── home.py              # Main dashboard page
│   │   └── streamlit_app.py     # Streamlit application
│   └── 📁 utils/                # Utility functions
├── 📁 test/                     # Test suite
│   ├── 📁 unit/                 # Unit tests
│   │   ├── test_basic_functionality.py
│   │   ├── 📁 database/
│   │   │   └── test_database_connectivity.py
│   │   └── 📁 ui/
│   │       └── test_simple_streamlit.py
│   ├── 📁 integration/          # Integration tests
│   ├── 📁 e2e/                  # End-to-end tests
│   └── conftest.py              # Test configuration
├── 📁 scripts/                  # Development and testing utilities
│   ├── run_tests.py             # Test runner
│   ├── setup_test_env.py        # Test environment setup
│   └── README.md                # Scripts documentation
├── main.py                      # Main entry point with Prefect flows
├── Makefile                     # Build automation
├── README.md                    # This file
└── LICENSE                      # License file
```

### 🎯 Key Benefits of This Structure

- **Clean Root Directory**: Only essential files remain in the project root
- **Centralized Configuration**: All config files are organized in the `config/` directory
- **Contained Build Artifacts**: Test results and coverage reports are stored in `build/`
- **Better Organization**: Related files are grouped together logically
- **Standard Practice**: Follows common Python project conventions
- **Easier Maintenance**: Configuration and build artifacts are clearly separated

## 📦 MLflow Integration & Model Management

This project uses **MLflow** for enterprise-level model management, experiment tracking, and periodic rebaselining of trading models. MLflow is integrated with a dedicated PostgreSQL backend for robust, production-grade tracking and model registry. Rebaselining workflows are scheduled and managed via Prefect, ensuring models remain up-to-date with the latest data and performance metrics.

- MLflow server runs with PostgreSQL backend for persistence
- Model experiments and artifacts are tracked and versioned
- Periodic rebaselining is orchestrated as part of Prefect flows
- **PyTorch GRU Implementation**: New PyTorch-based GRU models with MLflow integration
- See [Architecture Decisions](docs/architecture-decisions.md) for rationale and future plans

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
pip install -r config/requirements.txt
pip install -r config/requirements-dev.txt  # For development
```

### 2. Configuration
```bash
# Set up environment variables
cp config/env.example .env
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

### 4. MLflow Setup
```bash
# Create MLflow database
createdb mlflow_db

# Start MLflow server
mlflow server --backend-store-uri postgresql://postgres:nishant@localhost/mlflow_db --default-artifact-root file:./mlruns --host 0.0.0.0 --port 5000

# Set environment variable
export MLFLOW_TRACKING_URI=http://localhost:5000
```

### 5. Start the System
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
   - **Portfolio**: Detailed portfolio management and analysis
   - **Analysis**: Data analysis and trading signals
   - **Testing**: Test results and coverage visualization
   - **Settings**: System configuration

### Running ML Training
```bash
# Train PyTorch GRU models for all pairs
python -m src.ml.train_gru_models

# View MLflow experiments
# Open http://localhost:5000 in your browser
```

### Monitoring
- **Prefect UI**: `http://localhost:4200` - Monitor workflow execution
- **Streamlit Dashboard**: `http://localhost:8501` - View real-time data
- **MLflow UI**: `http://localhost:5000` - Monitor ML experiments and models
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

## 🧪 Development & Testing

### Current Testing Status

#### Test Suite Status
- ✅ **All Tests Passing**: 309 passed, 7 skipped, 0 failed
- ✅ **Test Categories**: Unit, Integration, E2E, UI, Database, MLflow
- ✅ **Async Support**: Proper pytest-asyncio configuration
- ✅ **Mock Isolation**: Fixed test isolation issues with proper mocking

#### Coverage Overview
- **Overall Project Coverage**: 78%
- **High Coverage Modules (100%)**:
  - Database connectivity (`src/database/database_connectivity.py`)
  - Symbol manager (`src/data/sources/symbol_manager.py`)
  - UI components (`src/ui/components/date_display.py`, `src/ui/components/market_status.py`)
- **Good Coverage Modules (85%+)**:
  - Portfolio management (`src/ui/portfolio.py` - 94%)
  - Home dashboard (`src/ui/home.py` - 85%)
  - Symbol selector (`src/ui/components/symbol_selector.py` - 87%)

#### Recent Testing Improvements
- ✅ **MLflow Manager**: Fixed environment variable substitution in YAML config
- ✅ **UI Component Tests**: Resolved mock isolation issues with `st.columns` and `st.write`
- ✅ **Database Tests**: All database connectivity tests passing with comprehensive mocking
- ✅ **Async Tests**: Proper async test configuration and execution
- ✅ **Test Isolation**: Fixed mock leakage between tests with proper reset mechanisms
- ✅ **AgGrid Integration**: Enhanced testing results display with advanced table functionality
- ✅ **Path Normalization**: Fixed coverage display issues across different operating systems

### MLflow Integration Testing
To test MLflow integration:
- Ensure the MLflow server is running (`mlflow server ...`)
- Set the `MLFLOW_TRACKING_URI` environment variable to your server (e.g., `export MLFLOW_TRACKING_URI=http://localhost:5000`)
- Run the MLflow-related tests:
  ```bash
  pytest test/unit/test_mlflow_manager.py -v
  ```
- For more, see [Testing Guide](docs/testing.md) and [Architecture Decisions](docs/architecture-decisions.md)

### Test Environment Setup

#### Option 1: Automated Setup (Recommended)
```bash
python scripts/setup_test_env.py
```

#### Option 2: Manual Setup
```bash
pip install -r config/requirements-dev.txt
pytest --version  # Verify pytest installation
```

### Running Tests

#### Quick Test Suite
```bash
# Run all tests with coverage (default)
python scripts/run_tests.py

# Run comprehensive test suites
python -m pytest test/unit/ui/test_market_status_comprehensive.py test/unit/ui/test_home_comprehensive.py test/unit/database/test_database_connectivity_comprehensive.py test/unit/ui/test_date_display_comprehensive.py --cov=src --cov-report=json:build/coverage.json --cov-report=term-missing

# Run quick test suite (basic + database)
python scripts/run_tests.py quick

# Run only basic tests
python scripts/run_tests.py basic

# Run only database tests
python scripts/run_tests.py database

# Run Streamlit UI tests
python scripts/run_tests.py simple

# Get help with all options
python scripts/run_tests.py --help
```

#### Individual Test Files
```bash
# Basic functionality tests
pytest test/unit/test_basic_functionality.py -v

# Database connectivity tests
pytest test/unit/database/test_database_connectivity.py -v

# Comprehensive UI tests
pytest test/unit/ui/test_market_status_comprehensive.py -v
pytest test/unit/ui/test_date_display_comprehensive.py -v
pytest test/unit/ui/test_home_comprehensive.py -v

# Streamlit UI tests
pytest test/unit/ui/test_simple_streamlit.py -v
```

#### Coverage Reports
```bash
# Terminal coverage report
pytest test/ -v --cov=src --cov-report=term-missing

# HTML coverage report
pytest test/ -v --cov=src --cov-report=html

# JSON coverage report (for UI display)
pytest test/ -v --cov=src --cov-report=json:build/coverage.json
```

### Test Structure

```
test/
├── conftest.py                          # Pytest configuration and fixtures
├── unit/                                # Unit tests
│   ├── test_basic_functionality.py     # Basic functionality tests
│   ├── database/                       # Database tests
│   │   ├── test_database_connectivity.py
│   │   └── test_database_connectivity_comprehensive.py
│   └── ui/                             # UI tests
│       ├── test_simple_streamlit.py
│       ├── test_home_comprehensive.py
│       ├── test_date_display_comprehensive.py
│       ├── test_market_status_comprehensive.py
│       └── test_testing_results.py
├── integration/                         # Integration tests (future)
├── e2e/                                # End-to-end tests (future)
└── fixtures/                           # Test fixtures (future)
```

### What's Tested

#### Basic Functionality Tests
- ✅ Import verification
- ✅ Environment variable setup
- ✅ Mock fixture functionality
- ✅ Data structure validation
- ✅ Error handling patterns
- ✅ Utility function validation (symbol, price, date)

#### Database Connectivity Tests
- ✅ Class and method existence
- ✅ Simple mock connection and query
- ✅ Error handling pattern
- ✅ Connection pool and transaction concepts
- ✅ Credential validation logic
- ✅ Comprehensive database operations (100% coverage)

#### UI Component Tests
- ✅ Component rendering with mocked Streamlit functions
- ✅ User interaction patterns
- ✅ Data display functionality
- ✅ Responsive design elements
- ✅ Timezone conversions and date formatting
- ✅ Market status display and indicators
- ✅ Error handling and edge cases

#### Comprehensive Test Suites
- ✅ **Date Display**: 30 tests covering timezone conversions, formatting, and edge cases
- ✅ **Market Status**: 29 tests covering UI components, market indicators, and display functions
- ✅ **Home Dashboard**: Complete coverage of dashboard functionality and components
- ✅ **Database Connectivity**: Full coverage of all database operations and error handling

### Testing Philosophy

- **No real database required**: All database tests use comprehensive mocks
- **No external API calls**: No Yahoo, Alpaca, or News API tests
- **Advanced mocking**: Sophisticated mocking for UI components and external dependencies
- **Cross-platform compatibility**: Works on Windows, macOS, and Linux
- **Comprehensive coverage**: Detailed test suites for complex modules
- **UI testing**: Mock-based testing of Streamlit components

### Example Test Output

```
======================================== test session starts ========================================
platform win32 -- Python 3.10.6, pytest-8.4.1, pluggy-1.6.0
collected 317 items

test/unit/test_basic_functionality.py ................ [  5%]
test/unit/test_mlflow_manager.py .. [  6%]
test/unit/test_websocket_symbols.py .... [  7%]
test/unit/ui/test_date_display_comprehensive.py .............................. [ 16%]
test/unit/ui/test_debug_ui.py ................ [ 21%]
test/unit/ui/test_home_comprehensive.py ........................ [ 30%]
test/unit/ui/test_market_status_comprehensive.py ............................. [ 39%]
test/unit/ui/test_portfolio_comprehensive.py ........................ [ 48%]
test/unit/ui/test_portfolio_direct.py ........ [ 51%]
test/unit/ui/test_portfolio_simple.py .... [ 52%]
test/unit/ui/test_simple_streamlit.py ...... [ 54%]
test/unit/ui/test_symbol_selector_comprehensive.py ................ [ 59%]
test/unit/ui/test_testing_results.py ................ [ 64%]
test/unit/data/test_portfolio_manager.py ........ [ 67%]
test/unit/data/test_portfolio_optimization.py .......... [ 71%]
test/unit/data/test_symbol_analysis.py .......... [ 76%]
test/unit/data/test_symbol_manager_comprehensive.py ................ [ 81%]
test/unit/database/test_database_comprehensive.py ........................ [ 89%]
test/unit/database/test_database_connectivity.py ........ [ 92%]
test/unit/database/test_database_connectivity_comprehensive.py ........................ [100%]
test/integration/test_multi_symbol_recycler.py ......... [103%]
test/integration/test_streamlit_integration.py .. [104%]

======================================== 309 passed, 7 skipped in 46.76s =========================================

---------- coverage: platform win32, python 3.10.16-final-0 -----------
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/data/sources/portfolio_manager.py     249     90    64%   76-78, 105-107, 111, 131-132, 171-172, 176-177, 185-187, 225-227, 259-260, 285-287, 295-300, 311-312, 319, 342, 353, 377-379, 391-461, 498-499, 528-530, 535-559
src/data/sources/symbol_manager.py         54      0   100%
src/database/database_connectivity.py      83      0   100%
src/mlflow_manager.py                     205     88    57%   59-64, 88, 116-118, 133-134, 142-144, 174-176, 188-190, 203-205, 220, 223-225, 235-240, 253-255, 277-279, 292-299, 315-317, 328-337, 353, 373-375, 385-391, 403-422, 484-501
src/ui/components/date_display.py          39      0   100%
src/ui/components/market_status.py         52      0   100%
src/ui/components/symbol_selector.py      210     27    87%   115, 119-129, 216-218, 279-284, 308, 332-334, 382-384
src/ui/components/testing_results.py      421    107    75%   69-72, 82-86, 95-104, 113-159, 214, 216, 220, 244-246, 265-266, 300, 302, 306, 388-389, 394-395, 474, 479, 492, 494, 498, 508-509, 513, 563-564, 581, 590-592, 603-604, 628-654, 672-674, 678-680, 684-686, 730-733, 744-745, 752-753, 769, 774-784, 824-825
src/ui/home.py                            228     35    85%   38-40, 100-101, 180-192, 244-245, 261-279, 369-370, 384-385
src/ui/portfolio.py                       216     14    94%   40-42, 157-162, 202-203, 255-256, 444
src/ui/streamlit_app.py                    41      9    78%   48-52, 73, 75, 79, 86
src/utils/market_hours.py                  63     33    48%   26-27, 41-43, 49, 53, 59, 63-64, 68-69, 76-78, 82-90, 94-99, 103-108
src/utils/websocket_config.py             106     29    73%   41-43, 59, 63, 85, 96, 100, 110-111, 117-118, 122-123, 127-128, 133-135, 167-168, 174, 179, 184, 189, 194-197
---------------------------------------------------------------------
TOTAL                                    1967    432    78%
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
3. Run tests: `python scripts/run_tests.py`
4. Run quality checks: `pre-commit run --all-files`
5. Submit pull request

## 📚 Documentation

- **[API Documentation](docs/api.md)**: External and internal API integrations
- **[Architecture Decisions](docs/architecture-decisions.md)**: System design and implementation planning
- **[Data Systems](docs/data-systems.md)**: Data recycler system and GARCH pairs trading
- **[Development Guide](docs/development.md)**: Development practices and workflows
- **[Setup Guide](docs/setup.md)**: Installation and configuration
- **[Testing Guide](docs/testing.md)**: Comprehensive testing strategy and implementation
- **[UI Documentation](docs/ui.md)**: User interface components and portfolio management

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
- Reference [Architecture Decisions](docs/architecture-decisions.md) for rationale behind major design and workflow choices.

## 🐛 Troubleshooting

### Common Issues

#### Database Connection
- Verify PostgreSQL is running and credentials are correct
- Check database migration status

#### API Errors
- Check API keys and rate limits
- Verify API service availability

#### Prefect Issues
- Ensure Prefect server is running and workflows are deployed
- Check workflow deployment status

#### UI Problems
- Check Streamlit dependencies and CSS file paths
- Verify port availability (default: 8501)

#### Testing Issues
If you see an error like:
```
error: unrecognized arguments: --cov=src/ui --cov-report=term-missing ...
```

Install the `pytest-cov` plugin:
```bash
pip install pytest-cov
```

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
- **Last Updated**: June 2025
- **Python Support**: 3.9+
- **Database**: PostgreSQL 12+
- **Test Coverage**: Minimum 20% (basic functionality) 