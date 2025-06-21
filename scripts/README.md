# Scripts Directory

This directory contains utility scripts for the Prefect Trading System.

## Directory Structure

```
scripts/
├── README.md              # This file
├── run_tests.py           # Test runner
└── setup_test_env.py      # Test environment setup

src/scripts/               # Application-specific scripts
```

## Scripts Overview

### Root Scripts (`scripts/`)

#### `run_tests.py` - Test Runner
Minimal test runner for basic and database tests.

**Usage:**
```bash
python scripts/run_tests.py [test_type]
```

**Available test types:**
- `basic` - Basic functionality tests only
- `unit` - All unit tests
- `database` - Database tests only
- `integration` - Integration tests only (future)
- `e2e` - End-to-end tests only (future)
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

### Application Scripts (`src/scripts/`)

These scripts are part of the application and handle specific functionality.

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

### 3. Get help
```bash
python scripts/run_tests.py --help
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
```

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

## Advantages of Python Scripts

1. **Cross-platform**: Works on Windows, macOS, and Linux
2. **No shell dependencies**: No need for bash, zsh, or other shells
3. **Better error handling**: More robust error handling and reporting
4. **Easier maintenance**: Python code is easier to maintain and debug
5. **Consistent behavior**: Same behavior across different platforms
6. **Better integration**: Seamless integration with Python testing tools

## Minimal Test Suite Philosophy

- Only basic and database tests are included in the quick suite
- No external API, Yahoo, or Alpaca tests
- No real database required; all database tests use simple mocks or check method existence
- No complex patching or integration tests by default 