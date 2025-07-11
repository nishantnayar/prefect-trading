# Scripts Directory

This directory contains utility scripts for the Prefect Trading project.

## Database Scripts

### Migration Verification

#### `verify_migrations_simple.py`
**Purpose**: Simplified verification of database schema against consolidated migration scripts.

**Features**:
- Connects to database using existing configuration
- Extracts current schema (tables, columns, indexes)
- Compares with expected schema from consolidated migrations
- Generates detailed JSON report with discrepancies
- Provides clear pass/fail status
- Avoids complex SQL queries that can cause issues
- Distinguishes between application tables and system tables

**Usage**:
```bash
# Run verification
python scripts/verify_migrations_simple.py

# Or use Makefile
make db-verify
```

**Understanding Results**:
- **✅ PASSED**: All application tables from migrations are present
- **⚠️ EXTRA TABLES**: These are typically system tables (Prefect, MLflow, etc.) and are expected
- **❌ MISSING TABLES**: These indicate actual schema mismatches that need attention

**Output**:
- Console report showing table comparisons
- JSON report saved to `scripts/schema_verification_report_YYYYMMDD_HHMMSS.json`

#### `check_db_direct.py`
**Purpose**: Quick database schema inspection and connectivity test.

**Features**:
- Sets database credentials directly (no .env file needed)
- Simple database connection test
- Lists all tables with row counts
- Shows detailed column information
- Displays indexes, constraints, and triggers
- Useful for understanding current database state

**Usage**:
```bash
# Quick schema check
python scripts/check_db_direct.py

# Or use Makefile
make db-check
```

### Database Management

#### `create_mlflow_db.sql`
**Purpose**: Creates the MLflow database for model tracking.

**Usage**:
```bash
psql -U postgres -f scripts/create_mlflow_db.sql
```

#### `check_env_file.py`
**Purpose**: Validates environment file configuration.

**Usage**:
```bash
python scripts/check_env_file.py
```

#### `load_historical_data.py`
**Purpose**: Loads historical market data into the database.

**Usage**:
```bash
python scripts/load_historical_data.py
```

#### `manage_symbols.py`
**Purpose**: Manages stock symbols in the database.

**Usage**:
```bash
python scripts/manage_symbols.py
```

#### `manual_save.py`
**Purpose**: Manual data persistence utilities.

**Usage**:
```bash
python scripts/manual_save.py
```

### MLflow Scripts

#### `create_mlflow_db.sql`
**Purpose**: Creates the MLflow database for model tracking and experiment management.

**Usage**:
```bash
psql -U postgres -f scripts/create_mlflow_db.sql
```

### Testing Scripts

#### `run_tests.py`
**Purpose**: Runs the complete test suite.

**Usage**:
```bash
python scripts/run_tests.py
```

#### `setup_test_env.py`
**Purpose**: Sets up test environment and database.

**Usage**:
```bash
python scripts/setup_test_env.py
```

## ML Training Scripts

### PyTorch GRU Implementation

The ML training scripts are located in `src/ml/`:

#### `train_gru_models.py`
**Purpose**: Trains PyTorch GRU models for all pairs with MLflow integration.

**Features**:
- Trains models for all pairs that meet correlation threshold (>0.8)
- Comprehensive performance analysis and ranking
- MLflow experiment tracking with descriptive run names
- Model registry integration
- Performance statistics and correlation analysis

**Usage**:
```bash
# Train all pairs
python -m src.ml.train_gru_models

# View results in MLflow UI
# Open http://localhost:5000
```

#### `gru_model.py`
**Purpose**: PyTorch GRU model implementation and training utilities.

**Features**:
- PyTorch GRU model architecture
- Dataset and training utilities
- MLflow integration for model logging
- Performance tracking and early stopping

## Makefile Integration

The following database-related commands are available in the main Makefile:

```bash
# Run original migrations (legacy)
make db-migrate

# Run consolidated migrations (recommended)
make db-migrate-consolidated

# Verify schema against consolidated migrations
make db-verify

# Quick schema check
make db-check

# Reset database with consolidated migrations
make db-reset
```

## Migration Files

### Consolidated Migrations (Recommended)
- `001_initial_schema_consolidated.sql` - Complete initial schema
- `002_data_source_enhancement_consolidated.sql` - Data source tracking
- `003_historical_data_consolidated.sql` - Historical data storage

### Original Migrations (Legacy)
- `001_initial_schema/` - Multiple small migration files
- `008_add_data_source.sql` - Data source enhancement
- `010_create_market_data_historical.sql` - Historical data table

## Usage Examples

### 1. Verify Current Database Against Migrations
```bash
# Check if current database matches consolidated migrations
make db-verify
```

### 2. Quick Database Health Check
```bash
# See current database structure and row counts
make db-check
```

### 3. Reset Database with Consolidated Migrations
```bash
# Drop and recreate database with consolidated migrations
make db-reset
```

### 4. Manual Migration Verification
```bash
# Run verification script directly
python scripts/verify_migrations_simple.py

# Check specific database schema
python scripts/check_db_direct.py
```

## Troubleshooting

### Database Connection Issues
1. Ensure PostgreSQL is running
2. Check database credentials are correct
3. Verify database exists and is accessible
4. Check network connectivity

### Migration Verification Failures
1. Run `make db-check` to see current schema
2. Compare with expected schema in consolidated migrations
3. Check if any manual schema changes were made
4. Consider running `make db-reset` to start fresh

### Permission Issues
1. Ensure database user has appropriate permissions
2. Check PostgreSQL authentication configuration
3. Verify connection string format

## Output Files

### Verification Reports
- `schema_verification_report_YYYYMMDD_HHMMSS.json` - Detailed verification results
- Console output with summary and recommendations

### Logs
- Database connection logs
- Migration execution logs
- Error details for troubleshooting 