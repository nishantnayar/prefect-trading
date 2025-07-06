# Scripts Directory

This directory contains utility scripts for the Prefect Trading System.

> **📋 Quick Links**: [Main README](../README.md) | [Architecture Decisions](../docs/architecture-decisions.md) | [Setup Guide](../docs/setup.md) | [Development Guide](../docs/development.md) | [Testing Guide](../docs/testing.md)

## Directory Structure

```
scripts/
├── README.md              # This file
├── run_tests.py           # Test runner
├── setup_test_env.py      # Test environment setup
├── create_mlflow_db.sql   # MLflow database setup
├── manage_symbols.py      # Symbol management utility
└── manual_save.py         # Manual data saving utility

src/scripts/               # Application-specific scripts
├── check_delisted_symbols.py
├── check_postgres_data.py
└── manage_symbols.py
```

## Scripts Overview

### Root Scripts (`scripts/`)

#### `run_tests.py` - Test Runner
Comprehensive test runner with multiple test suites and coverage reporting.

**Usage:**
```bash
python scripts/run_tests.py [test_type]
```

**Available test types:**
- `basic` - Basic functionality tests only
- `unit` - All unit tests
- `database` - Database tests only
- `integration` - Integration tests only
- `e2e` - End-to-end tests only
- `coverage` - All tests with coverage report
- `quick` - Quick test suite (basic + database)
- `all` - Complete test suite with coverage (default)

**Examples:**
```bash
python scripts/run_tests.py          # Run all tests with coverage
python scripts/run_tests.py quick    # Run quick test suite (basic + database)
python scripts/run_tests.py basic    # Run basic tests only
python scripts/run_tests.py database # Run database tests only
python scripts/run_tests.py --help   # Show help message
```

#### `setup_test_env.py` - Test Environment Setup
Sets up the test environment including dependencies and directory structure.

**Usage:**
```bash
python scripts/setup_test_env.py
```

**What it does:**
- Installs production and development dependencies
- Sets up test directory structure (with `__init__.py`)
- Configures environment variables
- Makes scripts executable (Unix-like systems)

#### `create_mlflow_db.sql` - MLflow Database Setup
SQL script to create and configure the MLflow database.

**Usage:**
```bash
psql -f scripts/create_mlflow_db.sql
```

#### `manage_symbols.py` - Symbol Management Utility
Utility for managing trading symbols and checking data availability.

**Usage:**
```bash
python scripts/manage_symbols.py [command]
```

**Commands:**
- `status` - Check symbol data availability
- `add` - Add new symbols
- `remove` - Remove symbols
- `list` - List all symbols

#### `manual_save.py` - Manual Data Saving
Utility for manually saving data to the database.

**Usage:**
```bash
python scripts/manual_save.py
```

### Application Scripts (`src/scripts/`)

These scripts are part of the application and handle specific functionality.

#### `check_delisted_symbols.py`
Checks for delisted symbols and updates the database accordingly.

#### `check_postgres_data.py`
Verifies PostgreSQL data integrity and structure.

#### `manage_symbols.py`
Application-specific symbol management functionality.

## Quick Start

### 1. Set up test environment
```bash
python scripts/setup_test_env.py
```

### 2. Run tests
```bash
# Run all tests
python scripts/run_tests.py

# Run quick test suite (basic + database)
python scripts/run_tests.py quick

# Run only basic tests
python scripts/run_tests.py basic

# Run only database tests
python scripts/run_tests.py database
```

### 3. Set up MLflow database
```bash
psql -f scripts/create_mlflow_db.sql
```

### 4. Manage symbols
```bash
python scripts/manage_symbols.py status
```

### 5. Get help
```bash
python scripts/run_tests.py --help
python scripts/manage_symbols.py --help
```

## Script Organization

- **Root scripts** (`scripts/`) - Development and testing utilities
- **Application scripts** (`src/scripts/`) - Application-specific functionality

This separation keeps development tools separate from application code while maintaining clear organization.

## Cross-Platform Compatibility

The Python scripts work on all platforms:
- **Windows**: `python scripts/run_tests.py`
- **macOS/Linux**: `python scripts/run_tests.py` or `python3 scripts/run_tests.py`

No need to worry about shell script permissions or different shell environments.

## Environment Variables

The test scripts automatically set these environment variables:

```bash
export TESTING=true
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=test_trading_db
export DB_USER=test_user
export DB_PASSWORD=test_password
export MLFLOW_TRACKING_URI=http://localhost:5000
```

## Integration with Main Documentation

These scripts are referenced in the main documentation:

- **[Setup Guide](../docs/setup.md)**: Test environment setup and MLflow configuration
- **[Development Guide](../docs/development.md)**: Development workflows and testing practices
- **[Testing Guide](../docs/testing.md)**: Comprehensive testing strategies
- **[Architecture Decisions](../docs/architecture-decisions.md)**: Design rationale for script organization

## Troubleshooting

### Script not found
Make sure you're in the project root directory when running scripts.

### Python not found
Make sure Python is installed and in your PATH:
```bash
python --version
# or
python3 --version
```

### Import errors in tests
Make sure the virtual environment is activated (if using venv):
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Permission errors (Unix-like systems)
If you get permission errors, make the scripts executable:
```bash
chmod +x scripts/*.py
```

### MLflow database issues
If MLflow database setup fails:
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Create database manually
createdb mlflow_db

# Run the setup script
psql -d mlflow_db -f scripts/create_mlflow_db.sql
```

## Advantages of Python Scripts

1. **Cross-platform**: Works on Windows, macOS, and Linux
2. **No shell dependencies**: No need for bash, zsh, or other shells
3. **Better error handling**: More robust error handling and reporting
4. **Easier maintenance**: Python code is easier to maintain and debug
5. **Consistent behavior**: Same behavior across different platforms
6. **Better integration**: Seamless integration with Python testing tools
7. **MLflow integration**: Native support for MLflow operations

## Testing Philosophy

- Only basic and database tests are included in the quick suite
- No external API, Yahoo, or Alpaca tests
- No real database required; all database tests use simple mocks or check method existence
- No complex patching or integration tests by default
- MLflow tests require server setup but use mocked operations where possible

## Related Documentation

- **[Main README](../README.md)**: Project overview and quick start
- **[Architecture Decisions](../docs/architecture-decisions.md)**: Design rationale and decisions
- **[Setup Guide](../docs/setup.md)**: Installation and configuration
- **[Development Guide](../docs/development.md)**: Development practices and workflows
- **[Testing Guide](../docs/testing.md)**: Testing strategies and implementation 