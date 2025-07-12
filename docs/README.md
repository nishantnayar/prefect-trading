# Prefect Trading System Documentation

## What is Prefect Trading System?

Prefect Trading System is a modern, modular platform for financial data collection, analysis, and trading automation. It integrates real-time and historical data, robust workflow orchestration, and a professional UI for both developers and traders.

## Overview

The Prefect Trading System is a comprehensive financial data collection and analysis platform built with modern technologies and best practices. This documentation provides complete guidance for setup, development, testing, and deployment.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │  Prefect Flows  │    │   PostgreSQL    │
│                 │    │                 │    │   Database      │
│ • Yahoo Finance │───▶│ • Hourly Flow   │───▶│ • Market Data   │
│ • Alpaca API    │    │ • EOD Flow      │    │ • News Articles │
│ • News API      │    │ • WebSocket Flow│    │ • Company Info  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Streamlit UI   │
                       │                 │
                       │ • Dashboard     │
                       │ • Real-time Data│
                       │ • Portfolio Mgmt│
                       └─────────────────┘
```

### Core Components

#### 1. Data Collection Layer
- **Yahoo Finance Integration**: Historical market data and company information
- **Alpaca Integration**: Real-time market data and trading capabilities
- **News API Integration**: Market news and sentiment analysis
- **Data Recycler System**: Historical data replay for testing and development

#### 2. Database Layer
- **PostgreSQL Integration**: Primary data storage and management
- **Connection Pooling**: Efficient database connection management
- **Schema Management**: Automated migrations and version control
- **Data Validation**: Comprehensive data quality checks

#### 3. Processing Layer
- **Hourly Processing**: Real-time data processing and analysis
- **End-of-Day Processing**: Daily data aggregation and maintenance
- **GARCH Pairs Trading**: Advanced algorithmic trading with MLflow integration
- **Risk Management**: Comprehensive risk monitoring and control

#### 4. User Interface
- **Streamlit Dashboard**: Modern, responsive web interface with 5 main pages
- **PortfolioManager Singleton**: Efficient resource usage with single instance across components
- **Intelligent Caching**: Multi-tier caching system for optimal performance
- **Real-time Updates**: Live market data through intelligent caching

#### 5. Workflow Management
- **Prefect Orchestration**: Workflow orchestration and task management
- **MLflow Integration**: Model management and experiment tracking
- **Error Handling**: Comprehensive error handling and recovery mechanisms
- **Monitoring**: Real-time system monitoring and alerting

## Quick Navigation

### 🚀 Getting Started
- **[Setup Guide](setup.md)** - Complete environment setup and configuration (includes quick start)

### 📚 Core Documentation
- **[Development Guide](development.md)** - Coding standards, workflows, and best practices
- **[API Documentation](api.md)** - External and internal API integrations
- **[UI Documentation](ui.md)** - Streamlit interface and components (includes portfolio management)
- **[Data Systems](data-systems.md)** - Data recycler system and GARCH pairs trading

### 🧪 Testing
- **[Testing Guide](testing.md)** - Comprehensive testing strategy, UI, and coverage analysis

## Community & Support
- **GitHub Issues**: [Open an issue](https://github.com/your-repo/issues)
- **Discussions**: [Join the conversation](https://github.com/your-repo/discussions)
- **Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Contact**: dev-team@example.com

## Documentation Structure

```
docs/
├── README.md                    # This file - Main documentation index
├── setup.md                     # Environment setup and configuration
├── development.md               # Development guidelines and workflows
├── api.md                       # API documentation and integrations
├── ui.md                        # User interface documentation (includes portfolio management)
├── data-systems.md              # Data recycler system and GARCH pairs trading
├── testing.md                   # Comprehensive testing guide (includes UI and coverage)
└── architecture-decisions.md    # Architecture decisions and implementation planning
```

## Key Features

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

### 🎯 User Interface
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

## Getting Started

1. **Quick Setup**: Follow the [Setup Guide](setup.md) for immediate setup (30 minutes)
2. **Development**: Review the [Development Guide](development.md) for coding standards
3. **Testing**: Implement testing using the [Testing Guide](testing.md)
4. **UI & Portfolio**: Set up the interface and portfolio tracking with [UI Documentation](ui.md)
5. **Data Systems**: Configure data collection and trading systems with [Data Systems](data-systems.md)

## Contributing

When contributing to the project:

1. Follow the coding standards in the [Development Guide](development.md)
2. Write tests following the [Testing Guide](testing.md)
3. Update relevant documentation
4. Ensure all tests pass before submitting changes

## Support

- **Documentation**: Check the relevant documentation files
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub discussions for questions
- **Code Review**: Request review from team members

## License

This project is licensed under the terms specified in the LICENSE file.

## Recent Documentation Updates

### July 2025 - Daily Pair Identification Flow Implementation
- **New Prefect Flow**: Implemented automated daily pair identification with GARCH analysis
- **Start of Day Workflow**: Created 6:00 AM pre-market flow for model preparation
- **GARCH Integration**: Added GARCH(1,1) model fitting with statistical diagnostics
- **MLflow Integration**: Automated model logging and versioning for selected pairs
- **Quality Gates**: Implemented correlation, cointegration, and composite score thresholds
- **Testing Framework**: Added comprehensive testing scripts and Makefile commands
- **Documentation**: Integrated daily pair identification into existing documentation structure

### Key Features of Daily Pair Identification Flow
- **7-Step Process**: Data collection → Correlation analysis → Cointegration testing → GARCH fitting → Model selection → MLflow logging → Configuration update
- **Statistical Rigor**: Correlation ≥ 0.8, cointegration p-value < 0.05, composite score > 0.7
- **Composite Scoring**: 40% AIC/BIC + 30% volatility forecasting + 20% trading performance + 10% diagnostics
- **Automated Execution**: Scheduled at 6:00 AM EST Mon-Fri via Prefect deployment
- **Manual Testing**: `make test-pairs`, `make run-pairs`, `make run-start-day` commands
- **Production Ready**: Error handling, resource management, and comprehensive logging

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

### Testing page documentation**: Coverage visualization and Streamlit dataframe integration
- **Portfolio page documentation**: Real-time data integration with singleton pattern
- **Enhanced UI documentation**: Current navigation structure with performance improvements

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