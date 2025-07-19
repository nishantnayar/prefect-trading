# Test Organization Guide

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
├── migrate_tests.py              # Migration script
├── analyze_coverage.py           # Coverage analysis
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

## Migration Plan

1. **Phase 1**: Create new directory structure
2. **Phase 2**: Move existing tests to appropriate locations
3. **Phase 3**: Create missing test files for uncovered modules
4. **Phase 4**: Add shared fixtures and reduce duplication

## Benefits

- **Easier Navigation**: Find tests quickly by following source structure
- **Better Coverage**: Clear visibility of what's tested vs. what's missing
- **Reduced Duplication**: Shared fixtures and common test utilities
- **Scalability**: Structure supports growth without reorganization
- **Team Onboarding**: New developers can easily understand test organization 