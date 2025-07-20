# Test Organization Guide

## Overview

The test folder is organized to mirror the source code structure while maintaining clear separation between test types. This optimization provides better navigation, reduced duplication, and improved scalability.

## Optimization Summary

### Issues Identified in Original Structure

1. **Inconsistent Structure Mapping**: Test folders didn't mirror source code structure
2. **Empty Test Directories**: `test/database/`, `test/data/`, `test/ui/` were empty
3. **Poor Separation of Concerns**: All tests mixed in `test/unit/` without proper organization
4. **Missing Test Coverage**: Entire modules lacked tests (flows, scripts, mlflow_manager)
5. **Code Duplication**: Repeated mock setups across test files

### Optimizations Implemented

1. **Mirror Source Structure**: Test folders now match source code organization
2. **Clear Test Type Separation**: Unit, integration, and e2e tests properly organized
3. **Shared Fixtures**: Common test data and mocks centralized in `fixtures/`
4. **Migration Tools**: Scripts to help move existing tests and analyze coverage
5. **Better Documentation**: Clear organization principles and migration guide

### Optimized Structure

```
test/
├── unit/                          # Unit tests (fast, isolated)
│   ├── data/                      # Mirror src/data structure
│   │   ├── sources/
│   │   │   ├── test_alpaca_daily_loader.py
│   │   │   ├── test_alpaca_historical_loader.py
│   │   │   ├── test_symbol_manager.py
│   │   │   └── test_portfolio_manager.py
│   │   └── __init__.py
│   ├── database/                  # Mirror src/database structure
│   │   ├── test_database_connectivity.py
│   │   └── __init__.py
│   ├── ml/                        # Mirror src/ml structure
│   │   ├── test_gru_model.py
│   │   ├── test_pair_analysis.py
│   │   └── __init__.py
│   ├── ui/                        # Mirror src/ui structure
│   │   ├── components/
│   │   │   ├── test_company_info.py
│   │   │   ├── test_market_data.py
│   │   │   └── test_symbol_selector.py
│   │   └── __init__.py
│   ├── utils/                     # Mirror src/utils structure
│   │   ├── test_config_loader.py
│   │   ├── test_env_loader.py
│   │   └── __init__.py
│   ├── flows/                     # Mirror src/flows structure
│   │   ├── test_preprocessing_flows.py
│   │   └── __init__.py
│   └── test_mlflow_manager.py     # Root level module
├── integration/                   # Integration tests (external dependencies)
│   ├── test_database_integration.py
│   ├── test_api_integration.py
│   └── test_mlflow_integration.py
├── e2e/                          # End-to-end tests (full system)
│   ├── test_trading_workflow.py
│   └── test_ui_workflow.py
├── fixtures/                     # Shared test fixtures
│   ├── database_fixtures.py
│   ├── data_fixtures.py
│   └── mock_fixtures.py
├── conftest.py                   # Pytest configuration
├── analyze_coverage.py           # Coverage analysis tool
└── __init__.py
```

## Organization Principles

### 1. **Mirror Source Structure**
- Test folders should mirror the source code structure
- Makes it easy to find tests for specific modules
- Maintains consistency as the codebase grows

### 2. **Test Type Separation**
- **Unit tests**: Fast, isolated, no external dependencies
- **Integration tests**: Test interactions between components
- **E2E tests**: Test complete workflows

### 3. **Shared Fixtures**
- Common test data and mocks in `fixtures/`
- Reduces duplication across test files
- Centralized test data management

### 4. **Naming Conventions**
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<method_name>_<scenario>`

## Testing Tools

### Coverage Analysis
```bash
# Analyze test coverage and identify missing tests
python test/analyze_coverage.py
```

The coverage analysis tool provides:
- **Coverage Summary**: Overall test coverage statistics
- **Missing Tests**: List of modules without tests
- **Extra Test Files**: Orphaned test files
- **Recommendations**: Suggestions for improving coverage

### Shared Fixtures
- **`database_fixtures.py`**: Database-related test utilities
- **`mock_fixtures.py`**: Common mock objects and API responses
- **`data_fixtures.py`**: Sample data for testing

### Running Tests
```bash
# Run all tests with coverage
python scripts/run_tests.py

# Run specific test categories
python -m pytest test/unit/                    # Unit tests only
python -m pytest test/integration/             # Integration tests only
python -m pytest test/e2e/                     # End-to-end tests only

# Run tests for specific module
python -m pytest test/unit/database/           # Database tests only
python -m pytest test/unit/data/sources/       # Data source tests only
```

## Benefits

- **Easier Navigation**: Find tests quickly by following source structure
- **Better Coverage**: Clear visibility of what's tested vs. what's missing
- **Reduced Duplication**: Shared fixtures eliminate repeated code
- **Scalability**: Structure supports growth without reorganization
- **Team Onboarding**: New developers can easily understand test organization

## Migration Status

### ✅ Completed
- [x] Created optimized directory structure
- [x] Added shared fixtures (`database_fixtures.py`, `mock_fixtures.py`)
- [x] Updated `conftest.py` to use shared fixtures
- [x] Created coverage analysis tool (`analyze_coverage.py`)
- [x] Added comprehensive documentation

### 🔄 In Progress
- [ ] Move existing tests to proper locations
- [ ] Create missing test files for uncovered modules
- [ ] Update import statements in moved tests
- [ ] Verify all tests pass in new structure

### 📋 Next Steps
1. **Phase 1**: Move existing tests to appropriate locations
2. **Phase 2**: Create missing test files for uncovered modules
3. **Phase 3**: Add integration and e2e tests
4. **Phase 4**: Optimize test execution and coverage reporting

## Best Practices

### Writing New Tests
1. **Follow the Structure**: Place tests in the appropriate directory that mirrors the source
2. **Use Shared Fixtures**: Leverage fixtures in `test/fixtures/` to reduce duplication
3. **Follow Naming Conventions**: Use consistent naming for files, classes, and methods
4. **Write Comprehensive Tests**: Cover happy path, edge cases, and error scenarios

### Maintaining Tests
1. **Keep Tests Updated**: Update tests when source code changes
2. **Run Coverage Analysis**: Regularly check for missing test coverage
3. **Use Shared Fixtures**: Avoid duplicating common test setup code
4. **Document Complex Tests**: Add comments for complex test scenarios

### Performance Considerations
1. **Fast Unit Tests**: Keep unit tests fast and isolated
2. **Mock External Dependencies**: Use mocks for API calls and database operations
3. **Parallel Execution**: Design tests to run in parallel when possible
4. **Resource Cleanup**: Ensure proper cleanup in integration and e2e tests

## Related Documentation

- **[Testing Guide](../docs/testing.md)**: Comprehensive testing documentation
- **[Development Guide](../docs/development.md)**: Development practices and workflows
- **[Architecture Decisions](../docs/architecture-decisions.md)**: Test optimization decision details
- **[Setup Guide](../docs/setup.md)**: Test setup and verification instructions 