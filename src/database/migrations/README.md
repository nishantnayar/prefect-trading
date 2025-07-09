# Database Migrations

This directory contains consolidated database migration scripts for the Prefect Trading project.

## Migration Structure

The migrations have been consolidated from multiple small scripts into logical groups:

### 1. `001_initial_schema_consolidated.sql`
**Purpose**: Creates the core database schema
**Combines**: Original migrations 001-007

**Tables Created**:
- `logs` - Application logging
- `market_data` - Real-time market data
- `symbols` - Stock symbols management
- `yahoo_company_info` - Company information from Yahoo Finance
- `yahoo_company_officers` - Company officers data
- `news_articles` - News articles storage

**Features**:
- All necessary indexes for performance
- Foreign key constraints
- Triggers for automatic timestamp updates
- Comprehensive table and column comments

### 2. `002_data_source_enhancement_consolidated.sql`
**Purpose**: Adds data source tracking capability
**Combines**: Original migration 008

**Changes**:
- Adds `data_source` column to `market_data` table
- Creates index for efficient filtering
- Documents the column purpose

### 3. `003_historical_data_consolidated.sql`
**Purpose**: Creates historical data storage
**Combines**: Original migration 010

**Tables Created**:
- `market_data_historical` - Historical market data for analysis

**Features**:
- Optimized for historical data queries
- Includes data source tracking
- Unique constraints to prevent duplicates

## Usage

### For New Installations
Run the migrations in order:

```bash
# 1. Create initial schema
psql -d your_database -f 001_initial_schema_consolidated.sql

# 2. Add data source tracking
psql -d your_database -f 002_data_source_enhancement_consolidated.sql

# 3. Create historical data table
psql -d your_database -f 003_historical_data_consolidated.sql
```

### For Existing Installations
If you already have the database set up with the original migration files, you can:

1. **Skip these consolidated scripts** - Your existing database is already up to date
2. **Use for reference** - These scripts show the complete schema structure
3. **Use for new environments** - Deploy new instances using these consolidated scripts

### Using Makefile Commands
```bash
# Run consolidated migrations
make db-migrate-consolidated

# Verify schema matches migrations
make db-verify

# Check current database schema
make db-check

# Reset database with consolidated migrations
make db-reset
```

## Migration History

### Original Structure (Deprecated)
- `001_initial_schema/` - Multiple small migration files (001-007)
- `008_add_data_source.sql` - Data source enhancement
- `009_mlflow_integration/` - Empty directory (future use)
- `010_create_market_data_historical.sql` - Historical data table

### Consolidated Structure (Current)
- `001_initial_schema_consolidated.sql` - Complete initial schema
- `002_data_source_enhancement_consolidated.sql` - Data source tracking
- `003_historical_data_consolidated.sql` - Historical data storage

## Benefits of Consolidation

1. **Simplified Deployment**: Fewer files to manage and execute
2. **Better Documentation**: Clear sections with comments explaining each part
3. **Easier Maintenance**: All related changes in single files
4. **Reduced Complexity**: No need to track multiple small migration files
5. **Better Version Control**: Clearer history of schema changes

## Verification

### Schema Verification
Use the verification script to ensure your database matches the consolidated migrations:

```bash
# Run verification
python scripts/verify_migrations.py

# Or use Makefile
make db-verify
```

### Quick Schema Check
Check your current database structure:

```bash
# Quick check
python scripts/check_db_direct.py

# Or use Makefile
make db-check
```

## Future Migrations

For future database changes:

1. Create new consolidated migration files following the naming pattern: `XXX_description_consolidated.sql`
2. Include comprehensive comments explaining the purpose and changes
3. Add appropriate indexes and constraints
4. Update this README with new migration information

## Notes

- All scripts use `IF NOT EXISTS` clauses where appropriate to prevent errors on re-runs
- Indexes are created for optimal query performance
- Foreign key constraints maintain data integrity
- Triggers automatically update `updated_at` timestamps
- Comprehensive comments document table and column purposes 