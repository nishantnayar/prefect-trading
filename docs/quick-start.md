# Quick Start Guide

## For New Developers

This guide will help you get the Prefect Trading System up and running on your local machine in under 30 minutes.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher**
- **PostgreSQL 12 or higher**
- **Git**
- **Docker** (optional, for containerized development)

### Check Your Environment

```bash
# Check Python version
python --version

# Check if PostgreSQL is running
psql --version

# Check if Git is installed
git --version
```

## Step 1: Clone and Setup

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

## Step 2: Install Dependencies

```bash
# Install all dependencies
make install-dev

# Or manually:
pip install -r config/requirements.txt
pip install -r config/requirements-dev.txt
```

## Step 3: Configure Environment

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

## Step 4: Database Setup

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

## Step 5: Configure Prefect

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

## Step 6: Start the Application

```bash
# Start the Streamlit UI
make run-ui

# Or manually:
streamlit run src/ui/streamlit_app.py
```

## Step 7: Verify Installation

1. **Check Prefect UI**: Open [http://localhost:4200](http://localhost:4200)
2. **Check Streamlit UI**: Open [http://localhost:8501](http://localhost:8501)
3. **Run Tests**: `make test`

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

# Kill the process
kill -9 <PID>
```

### Missing Dependencies

```bash
# Reinstall dependencies
pip install --upgrade -r config/requirements.txt
pip install --upgrade -r config/requirements-dev.txt
```

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
make test
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
make test

# Run specific test categories
make test-unit
make test-integration
make test-e2e

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

## Project Structure Overview

```
prefect-trading/
├── src/                    # Source code
│   ├── data/              # Data collection
│   ├── database/          # Database operations
│   ├── ui/                # User interface
│   └── utils/             # Utilities
├── test/                  # Test suite
├── docs/                  # Documentation
├── config/                # Configuration files
├── main.py               # Main entry point
├── prefect.yaml          # Prefect configuration
└── requirements.txt      # Dependencies
```

## Next Steps

1. **Read the Documentation**:
   - [Project Overview](project-overview.md)
   - [Architecture Guide](architecture.md)
   - [Development Guide](development.md)
   - [Testing Guide](testing.md)

2. **Explore the Codebase**:
   - Start with `main.py` to understand the workflows
   - Look at `src/ui/streamlit_app.py` for the UI
   - Check `src/data/sources/` for data collection

3. **Run the System**:
   - Deploy workflows: `make deploy`
   - Monitor execution in Prefect UI
   - Test the Streamlit dashboard

4. **Contribute**:
   - Pick an issue from the GitHub issues
   - Follow the development workflow
   - Submit a pull request

## Getting Help

- **Documentation**: Check the `docs/` directory
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub discussions
- **Code Review**: Request review from team members

## Troubleshooting Checklist

- [ ] Python 3.9+ installed
- [ ] PostgreSQL running and accessible
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] Database created and migrated
- [ ] Prefect server running
- [ ] Prefect blocks configured
- [ ] Streamlit app accessible
- [ ] Tests passing

If you encounter issues, check the [Troubleshooting](development.md#troubleshooting) section in the development guide. 