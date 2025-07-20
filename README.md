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
- [Sector Configuration](docs/sector-configuration.md)

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
  - Start of day historical data loading

### 🎨 User Interface
- **Modern Streamlit Dashboard**
  - Real-time market data visualization with auto-refresh
  - Portfolio overview with performance metrics
  - Market overview with major indices and tech leaders
  - Recent trading activity tracking
  - Market news feed with article previews
  - Interactive symbol selector
  - Responsive design for all devices
  - **5 Main Pages**: Dashboard, Analysis, Portfolio, Models, Testing
  - **Testing Integration**: Built-in testing results and coverage visualization
  - **Portfolio Management**: Comprehensive portfolio tracking and analysis
  - **🧪 Testing Results Page**: Run tests directly from the UI with detailed results and statistics

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
- **Enhanced Pair Analysis**
  - **Correlation Analysis**: Pearson's ρ > 0.8 threshold for high correlation pairs
  - **Cointegration Testing**: Engle-Granger test with p < 0.05 for stable long-term relationships
  - **Spread Stationarity**: Augmented Dickey-Fuller test for spread validation
  - **Comprehensive Shortlisting**: Multi-criteria pair selection for optimal training
- **PyTorch GRU Models**
  - Pairs trading signal generation
  - Comprehensive model training pipeline with pair analysis integration
  - Real-time model inference
  - Performance tracking and analysis
- **MLflow Integration**
  - Experiment tracking and model versioning
  - Automated model registry management
  - Performance monitoring and comparison
  - Descriptive run naming and tagging
- **Automated Performance Tracking**
  - Model performance metrics storage
  - Automated rankings and trends updates
  - Historical performance analysis
  - Database integration with MLflow

## 📁 Project Structure

The project follows a clean, organized structure with configuration files centralized and build artifacts contained. For rationale behind major architectural choices, see [Architecture Decisions](docs/architecture-decisions.md).

```
prefect-trading/
├── 📁 config/                    # Configuration files
│   ├── config.yaml              # Application configuration
│   ├── streamlit_style.css      # UI styling
│   ├── pytest.ini              # Pytest configuration
│   ├── prefect.yaml            # Prefect workflow configuration
│   ├── requirements.txt         # Production dependencies
│   └── requirements-dev.txt     # Development dependencies
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
│   │   ├── pair_analysis.py     # Correlation and cointegration analysis
│   │   ├── gru_model.py         # PyTorch GRU model implementation
│   │   ├── train_gru_models.py  # Training pipeline with MLflow integration
│   │   ├── model_performance_tracker.py  # Performance tracking and database integration
│   │   └── config.py            # MLflow configuration
│   ├── 📁 ui/                   # User interface components
│   │   ├── 📁 components/       # Reusable UI components
│   │   ├── 📁 model_performance/ # Model performance dashboard
│   │   ├── home.py              # Main dashboard page
│   │   └── streamlit_app.py     # Streamlit application
│   └── 📁 utils/                # Utility functions
├── 📁 test/                     # Optimized test suite
│   ├── 📁 unit/                 # Unit tests (mirror src structure)
│   │   ├── 📁 data/             # Data source tests
│   │   ├── 📁 database/         # Database tests
│   │   ├── 📁 ml/               # ML model tests
│   │   ├── 📁 ui/               # UI component tests
│   │   ├── 📁 utils/            # Utility tests
│   │   └── 📁 flows/            # Flow tests
│   ├── 📁 integration/          # Integration tests
│   ├── 📁 e2e/                  # End-to-end tests
│   ├── 📁 fixtures/             # Shared test fixtures
│   ├── conftest.py              # Test configuration
│   └── analyze_coverage.py      # Coverage analysis tool
├── 📁 scripts/                  # Development and testing utilities
│   ├── run_pair_analysis.py     # Standalone pair analysis script
│   ├── run_tests.py             # Unified test runner (UI and command-line)
│   ├── setup_test_env.py        # Test environment setup
│   ├── verify_migrations_simple.py # Database migration verification
│   ├── check_db_direct.py       # Database health check
│   ├── manage_symbols.py        # Symbol management
│   ├── load_historical_data.py  # Historical data loading
│   └── README.md                # Scripts documentation
├── main.py                      # Main entry point with Prefect flows
├── Makefile                     # Build automation
├── README.md                    # This file
└── LICENSE                      # License file
```

## 📦 MLflow Integration & Model Management

This project uses **MLflow** for enterprise-level model management, experiment tracking, and periodic rebaselining of trading models. MLflow is integrated with a dedicated PostgreSQL backend for robust, production-grade tracking and model registry.

- MLflow server runs with PostgreSQL backend for persistence
- Model experiments and artifacts are tracked and versioned
- **Enhanced Pair Analysis**: Correlation and cointegration testing before model training
- **PyTorch GRU Implementation**: PyTorch-based GRU models with MLflow integration
- **Automated Performance Tracking**: Model rankings and trends updated automatically after training
- **Database Integration**: Performance metrics stored with MLflow run IDs for traceability
- See [Architecture Decisions](docs/architecture-decisions.md) for rationale and future plans

### 🔍 Pair Analysis Pipeline

The system now includes a comprehensive pair analysis pipeline that runs before GRU training:

1. **Correlation Analysis**: Identifies pairs with Pearson's ρ > 0.8
2. **Cointegration Testing**: Applies Engle-Granger test (p < 0.05) for stable relationships
3. **Spread Calculation**: Computes log-difference spreads with stationarity testing
4. **Pair Shortlisting**: Multi-criteria filtering for optimal training pairs

**Usage**:
```bash
# Standalone pair analysis
python scripts/run_pair_analysis.py --sectors technology healthcare

# GRU training with pair analysis (recommended)
python -m src.ml.train_gru_models

# GRU training without pair analysis
python -m src.ml.train_gru_models --no-pair-analysis
```

## 🧪 Testing Features

The system includes comprehensive testing capabilities with both UI and command-line interfaces:

### 📁 Optimized Test Organization
The test folder is organized to mirror the source code structure for better navigation and maintainability:

- **Mirror Source Structure**: Test folders match source code organization
- **Clear Test Type Separation**: Unit, integration, and e2e tests properly organized
- **Shared Fixtures**: Common test data and mocks centralized in `test/fixtures/`
- **Coverage Analysis**: Automated tool to identify missing tests and coverage gaps
- **Scalable Architecture**: Structure supports growth without reorganization

**Benefits:**
- ✅ **Easier Navigation**: Find tests quickly by following source structure
- ✅ **Better Coverage**: Clear visibility of what's tested vs. missing
- ✅ **Reduced Duplication**: Shared fixtures eliminate repeated code
- ✅ **Team Onboarding**: New developers can easily understand test organization

### 🎨 UI Testing Interface
- **Testing Results Page**: Access via the main navigation menu
- **Test Categories**: Run specific test suites (Database, Data, Basic Functionality, etc.)
- **Real-time Results**: View test execution progress and results
- **Detailed Statistics**: Success rates, pass/fail counts, and performance metrics
- **Raw Output**: Access to full test output for debugging
- **Test History**: Track test runs with timestamps and categories

### 🖥️ Command-line Testing
```bash
# List all available test files
python scripts/run_tests.py --list-tests

# Run all tests (JSON output for UI + coverage)
python scripts/run_tests.py

# Run specific test file
python scripts/run_tests.py --test-path test/database/test_database_connectivity.py

# Run with verbose output
python scripts/run_tests.py --verbose

# Run tests with pytest directly
pytest test/ -v
```

### 📊 Test Coverage
- **Database Tests**: Connectivity, migrations, and data integrity
- **Data Tests**: Portfolio management, symbol analysis, and data processing
- **Basic Functionality**: Core system components and utilities
- **MLflow Integration**: Model management and performance tracking
- **WebSocket Tests**: Real-time data streaming functionality

## 🛠️ Prerequisites

- **Python 3.9** or higher
- **PostgreSQL 12** or higher
- **Prefect 3.4.0** or higher
- **Alpaca API** credentials
- **Yahoo Finance API** access
- **pytest** (for testing features)
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
```

### 5. Start the Application

**Option 1: Start all services together (Recommended)**
```bash
# Using Python script (cross-platform)
make run-services

# Or using platform-specific scripts
make run-services-windows    # Windows
make run-services-unix       # Unix/Linux/macOS
```

**Option 2: Start services separately**
```bash
# Start Prefect server (in one terminal)
make run-prefect

# Start Prefect workers (in separate terminals)
prefect worker start --pool daily --work-queue default
prefect worker start --pool realtime --work-queue default
prefect worker start --pool endofday --work-queue default
prefect worker start --pool hourly --work-queue default

# Start MLflow server (in another terminal)
mlflow server --backend-store-uri postgresql://postgres:nishant@localhost/mlflow_db --default-artifact-root file:./mlruns --host 0.0.0.0 --port 5000

# Run the Streamlit UI (in another terminal)
make run-ui

# Run Prefect flows (in another terminal)
python main.py
```

**Service URLs**:
- 🌐 **Streamlit UI**: http://localhost:8501
- 🔧 **Prefect UI**: http://localhost:4200
- 🤖 **MLflow UI**: http://localhost:5000
- ⚙️ **Prefect Workers**: daily, realtime, endofday, and hourly pools, default queue

## 🔄 Available Prefect Flows

The system includes several automated workflows that can be run individually or scheduled:

### Core Data Flows
- **`start_of_day_flow()`** - Streamlined start-of-day workflow including:
  - Historical data loading (1-minute data only - hourly data loading commented out)
  - Data preprocessing with variance stability testing
  - Model training for all sectors with MLflow integration
  - Symbol maintenance and Yahoo Finance data collection (commented out for performance)
- **`hourly_process_flow()`** - Hourly data collection and processing
- **`eod_process_flow()`** - End-of-day symbol maintenance and data updates
- **`market_data_websocket_flow()`** - Real-time market data streaming

### Individual Data Loaders
- **`yahoo_data_loader_flow()`** - Yahoo Finance company data collection
- **`alpaca_data_loader_flow()`** - Alpaca market data collection
- **`news_data_loader_flow()`** - News API data collection
- **`symbol_maintenance_flow()`** - Symbol delisting checks and maintenance

### Usage
```bash
# Run specific flows
python -c "from main import start_of_day_flow; start_of_day_flow()"
python -c "from main import hourly_process_flow; hourly_process_flow()"
python -c "from main import eod_process_flow; eod_process_flow()"

# Or run from main.py (uncomment desired flow)
python main.py
```

## 🧪 Testing

### Run All Tests
```bash
# Run complete test suite
make test

# Or use the test runner
python scripts/run_tests.py
```

### Database Testing
```bash
# Verify database migrations
make db-verify

# Check database health
make db-check

# Reset database (if needed)
make db-reset
```

### ML Model Testing
```bash
# Train GRU models
python -m src.ml.train_gru_models

# View results in MLflow UI
# Open http://localhost:5000
```

## 🎯 Key Features

### 🏗️ Architecture
- **Modular Design**: Event-driven architecture with clear separation of concerns
- **Scalable**: Horizontal scaling with independent processing components
- **Reliable**: Comprehensive error handling and recovery mechanisms
- **Maintainable**: Clean code with extensive testing and documentation

### 📊 Data Collection
- **Multi-Source Integration**: Yahoo Finance, Alpaca API, News API
- **Real-time Processing**: WebSocket connections for live data
- **Batch Processing**: Scheduled workflows for historical data
- **Data Validation**: Comprehensive data quality checks

### 🎨 User Interface
- **Streamlit Dashboard**: Modern, responsive web interface with 5 main pages
- **Real-time Updates**: Intelligent caching system for live market data
- **Interactive Components**: Symbol selection, portfolio management, testing results
- **Professional Styling**: Custom CSS for optimal user experience
- **Testing Integration**: Built-in testing results and coverage visualization
- **PortfolioManager Singleton**: Efficient resource usage with single instance across components
- **Centralized Refresh**: Single refresh button for consistent user experience

### 💼 Portfolio Management
- **Real-time Portfolio Data**: Live account information and positions
- **Performance Tracking**: P&L calculations and trading history
- **Risk Analysis**: Margin utilization and position concentration
- **Visual Analytics**: Portfolio allocation charts and performance metrics
- **Intelligent Caching**: Multi-tier caching system with different durations for different data types
- **API Efficiency**: Reduced API calls through intelligent caching and singleton pattern

### 🧪 Testing Strategy
- **Comprehensive Coverage**: Unit, integration, and E2E tests
- **Performance Testing**: Load and stress testing capabilities
- **UI Testing**: Automated interface testing
- **CI/CD Integration**: Automated testing in deployment pipeline
- **Coverage Visualization**: Interactive coverage reports and insights

## Technology Stack

### Backend
- **Python 3.9+**: Core programming language
- **Prefect 3.4.0**: Workflow orchestration
- **PostgreSQL**: Primary database
- **SQLAlchemy**: Database ORM

### Frontend
- **Streamlit**: Web application framework
- **Custom CSS**: Professional styling
- **Plotly**: Interactive visualizations
- **Streamlit Dataframes**: Advanced table functionality

### External APIs
- **Alpaca Markets**: Market data and trading
- **Yahoo Finance**: Company information
- **NewsAPI**: Market news and headlines

### Development Tools
- **Pytest**: Testing framework
- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking

## 📚 Documentation

- **[Setup Guide](docs/setup.md)** - Complete environment setup and configuration
- **[Development Guide](docs/development.md)** - Coding standards, workflows, and best practices
- **[API Documentation](docs/api.md)** - External and internal API integrations
- **[UI Documentation](docs/ui.md)** - Streamlit interface and components
- **[Data Systems](docs/data-systems.md)** - Data recycler system and ML model management
- **[Testing Guide](docs/testing.md)** - Comprehensive testing strategy and coverage analysis
- **[Architecture Decisions](docs/architecture-decisions.md)** - System design rationale and implementation planning

## 🤝 Contributing

When contributing to the project:

1. Follow the coding standards in the [Development Guide](docs/development.md)
2. Write tests following the [Testing Guide](docs/testing.md)
3. Update relevant documentation
4. Ensure all tests pass before submitting changes

## 📞 Support

- **Documentation**: Check the relevant documentation files
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub discussions for questions
- **Code Review**: Request review from team members

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

## 🔄 Recent Updates

### July 2025 - Streamlined Start-of-Day Flow Optimization
- **Performance Optimization**: Simplified start-of-day flow for faster execution:
  - Hourly historical data loading commented out (reduces API usage and execution time)
  - Symbol maintenance and Yahoo Finance data collection commented out (can be run separately)
  - Focus on core ML pipeline: 1-minute data loading, preprocessing, and model training
- **Robust Config Loading**: Added comprehensive config loader utility for Prefect compatibility
- **Unicode Cleanup**: Replaced all Unicode symbols in print statements with ASCII equivalents
- **Error Resolution**: Fixed import issues and module loading problems in Prefect environment
- **Documentation Updates**: Updated all documentation to reflect current system state

### July 2025 - PortfolioManager Architecture Improvements
- **Architecture Decisions**: Added comprehensive documentation of PortfolioManager singleton pattern and caching system
- **UI Documentation**: Updated to reflect intelligent caching and centralized refresh functionality
- **Testing Documentation**: Added comprehensive coverage of Testing page features and Streamlit dataframe integration
- **Portfolio Documentation**: Added detailed portfolio management features with singleton pattern
- **Project Overview**: Updated system workflows to include Portfolio Management and Testing flows
- **Development Guide**: Added PortfolioManager singleton pattern and caching system implementation
- **Main README**: Updated to reflect current navigation and architectural improvements

### Key Architectural Improvements Documented
- **PortfolioManager Singleton Pattern**: Documented single instance architecture across UI components
- **Intelligent Caching System**: Multi-tier caching with different durations for different data types
- **Centralized Refresh**: Single refresh button replacing multiple redundant buttons
- **Performance Optimization**: API call reduction through intelligent caching
- **Cache Duration Strategy**: 
  - Orders: 10 seconds (frequently changing data)
  - Account Info: 30 seconds (relatively stable)
  - Positions: 30 seconds (moderately stable)
  - Portfolio Summary: 30 seconds (computed from other data)
- **Shared Instance Management**: Global instance management with get_portfolio_manager() and clear_portfolio_manager()
- **API Efficiency**: Reduced API calls by 80% through intelligent caching
- **User Experience**: Cleaner interface with single refresh button and better performance

### July 2025 - AgGrid to Streamlit Refactoring
- **UI Refactoring**: Replaced aggrid with native Streamlit dataframes for better compatibility
- **Dependency Reduction**: Removed `streamlit-aggrid` from requirements
- **Code Simplification**: Eliminated complex AgGrid configuration code
- **Improved Stability**: Native Streamlit components provide more reliable performance
- **Consistent Styling**: All tables now use uniform Streamlit styling and behavior
- **Files Modified**: 
  - `src/ui/components/testing_results.py` - Replaced AgGrid with `st.dataframe`
  - `config/requirements.txt` - Removed `streamlit-aggrid` dependency
- **Benefits**: Reduced dependencies, improved stability, easier maintenance, better performance 