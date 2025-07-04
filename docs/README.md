# Prefect Trading System Documentation

## What is Prefect Trading System?

Prefect Trading System is a modern, modular platform for financial data collection, analysis, and trading automation. It integrates real-time and historical data, robust workflow orchestration, and a professional UI for both developers and traders.

## Overview

The Prefect Trading System is a comprehensive financial data collection and analysis platform built with modern technologies and best practices. This documentation provides complete guidance for setup, development, testing, and deployment.

## Quick Navigation

### 🚀 Getting Started
- **[Setup Guide](setup.md)** - Complete environment setup and configuration (includes quick start)

### 📚 Core Documentation
- **[Project Overview](project-overview.md)** - System architecture and components
- **[Development Guide](development.md)** - Coding standards, workflows, and best practices
- **[API Documentation](api.md)** - External and internal API integrations
- **[UI Documentation](ui.md)** - Streamlit interface and components
- **[Portfolio Management](portfolio.md)** - Portfolio tracking and analysis features

### 🧪 Testing
- **[Testing Guide](testing.md)** - Comprehensive testing strategy and implementation
- **[Testing UI](testing-ui.md)** - Testing results interface documentation
- **[Coverage Display](coverage-display.md)** - Test coverage visualization and analysis

## Community & Support
- **GitHub Issues**: [Open an issue](https://github.com/your-repo/issues)
- **Discussions**: [Join the conversation](https://github.com/your-repo/discussions)
- **Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Contact**: dev-team@example.com

## Documentation Structure

```
docs/
├── README.md                    # This file - Main documentation index
├── setup.md                     # Environment setup and configuration (consolidated)
├── project-overview.md          # System architecture and overview
├── development.md               # Development guidelines and workflows
├── api.md                       # API documentation and integrations
├── ui.md                        # User interface documentation
├── portfolio.md                 # Portfolio management features
├── testing.md                   # Complete testing guide (consolidated)
├── testing-ui.md                # Testing results UI documentation
└── coverage-display.md          # Test coverage visualization guide
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
- **AgGrid**: Advanced table functionality

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
4. **Portfolio**: Set up portfolio tracking with [Portfolio Management](portfolio.md)

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

### December 2024 - PortfolioManager Architecture Improvements
- **Architecture Decisions**: Added comprehensive documentation of PortfolioManager singleton pattern and caching system
- **UI Documentation**: Updated to reflect intelligent caching and centralized refresh functionality
- **Testing Documentation**: Added comprehensive coverage of Testing page features and AgGrid integration
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

### Testing page documentation**: Coverage visualization and AgGrid integration
- **Portfolio page documentation**: Real-time data integration with singleton pattern
- **Enhanced UI documentation**: Current navigation structure with performance improvements 