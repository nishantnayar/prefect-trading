# Testing Quick Start Guide

## Overview

This guide describes the minimal working test suite for the Prefect Trading System. The suite focuses on basic functionality and database connectivity, without requiring real databases, external APIs, or complex mocking.

## Prerequisites

1. **Set up test environment** (recommended):
   ```bash
   python scripts/setup_test_env.py
   ```

2. **Or install testing dependencies manually**:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Verify pytest installation**:
   ```bash
   pytest --version
   ```

## Quick Start

### 1. Set Up Test Environment (Recommended)

```bash
python scripts/setup_test_env.py
```

### 2. Run Tests

```bash
# Run all tests with coverage (default)
python scripts/run_tests.py

# Run quick test suite (basic + database)
python scripts/run_tests.py quick

# Run only basic tests
python scripts/run_tests.py basic

# Run only database tests
python scripts/run_tests.py database

# Get help with all options
python scripts/run_tests.py --help
```

### 3. Run Individual Test Files

```bash
pytest test/unit/test_basic_functionality.py -v
pytest test/unit/database/test_database_connectivity.py -v
```

### 4. Run All Tests with Coverage

```bash
pytest test/ -v --cov=src --cov-report=term-missing
pytest test/ -v --cov=src --cov-report=html
```

## Test Structure

```
test/
├── conftest.py                          # Pytest configuration and fixtures (optional)
├── unit/                                # Unit tests
│   ├── test_basic_functionality.py     # Minimal basic tests
│   └── database/                       # Minimal database tests
│       └── test_database_connectivity.py
├── integration/                         # (future)
├── e2e/                                # (future)
└── fixtures/                           # (future)
```

## What's Tested

### Basic Functionality Tests
- ✅ Import verification
- ✅ Environment variable setup
- ✅ Mock fixture functionality
- ✅ Data structure validation
- ✅ Error handling patterns
- ✅ Utility function validation (symbol, price, date)

### Database Connectivity Tests
- ✅ Class and method existence
- ✅ Simple mock connection and query
- ✅ Error handling pattern
- ✅ Connection pool and transaction concepts
- ✅ Credential validation logic

## Minimal Test Philosophy

- **No real database required**: All database tests use simple mocks or check method existence.
- **No external API calls**: No Yahoo, Alpaca, or News API tests are included.
- **No complex patching**: Only simple Python mocks are used.
- **No integration or e2e tests**: The suite is focused on core logic and structure.

## Example Test Output

```
======================================== test session starts ========================================
platform win32 -- Python 3.10.6, pytest-8.4.1, pluggy-1.6.0
collected 15 items

test/unit/test_basic_functionality.py ............... [ 60%]
test/unit/database/test_database_connectivity.py ............. [100%]

======================================== 28 passed in 6.3s =========================================
```

## Script Organization

```
scripts/                                # Development and testing utilities
├── run_tests.py                       # Test runner
├── setup_test_env.py                  # Test environment setup
└── README.md                          # Scripts documentation

src/scripts/                           # Application-specific scripts
```

## Cross-Platform Compatibility

The Python scripts work on all platforms:
- **Windows**: `python scripts/run_tests.py`
- **macOS/Linux**: `python scripts/run_tests.py` or `python3 scripts/run_tests.py`

No need to worry about shell script permissions or different shell environments.

## Next Steps

1. **Add more unit tests** for other components as needed
2. **Create integration tests** for component interactions (future)
3. **Set up CI/CD pipeline** for automated testing (future)

## Getting Help

- Check the main testing documentation in `docs/testing-architecture.md`
- Review the implementation guide in `docs/testing-guide.md`
- Use `pytest --help` for command-line options
- Use `python scripts/run_tests.py --help` for test runner options 