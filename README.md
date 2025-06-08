# Prefect Trading System

A robust trading system built with Prefect for automated market data collection, processing, and analysis.

## Overview

This system provides automated data collection from multiple sources (Yahoo Finance and Alpaca), real-time market data streaming, and end-of-day processing capabilities. It's built using Prefect for workflow orchestration and includes comprehensive error handling and logging.

## Features

- **Multiple Data Sources**
  - Yahoo Finance data collection
  - Alpaca market data integration
  - Real-time market data via WebSocket

- **Automated Workflows**
  - Hourly data processing
  - End-of-Day (EOD) processing
  - Symbol maintenance and delisting checks
  - Real-time market data streaming

- **Database Integration**
  - PostgreSQL database connectivity
  - Robust error handling and logging

## Project Structure

```
prefect-trading/
├── config/             # Configuration files
├── src/
│   ├── data/          # Data collection and processing
│   ├── database/      # Database connectivity and operations
│   ├── scripts/       # Utility scripts
│   ├── ui/           # User interface components
│   └── utils/        # Utility functions
├── main.py           # Main entry point
├── prefect.yaml      # Prefect configuration
└── prefect_secrets.py # Secret management
```

## Prerequisites

- Python 3.9+
- PostgreSQL database
- Prefect
- Alpaca API credentials
- Yahoo Finance API access

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd prefect-trading
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your environment:
   - Set up your database credentials
   - Configure Alpaca API credentials
   - Set up Prefect configuration

## Usage

The system provides several main workflows:

1. **Hourly Process Flow**
   ```python
   from main import hourly_proces_flow
   hourly_proces_flow()
   ```

2. **End-of-Day Process Flow**
   ```python
   from main import eod_proces_flow
   eod_proces_flow()
   ```

3. **Market Data WebSocket Flow**
   ```python
   from main import market_data_websocket_flow
   market_data_websocket_flow()
   ```

## Configuration

The system uses Prefect for workflow management. Configure your workflows in `prefect.yaml` and manage secrets in `prefect_secrets.py`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the terms of the license included in the repository.

## Support

For support, please open an issue in the repository or contact the maintainers. 