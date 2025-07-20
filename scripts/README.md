# Scripts Directory

This directory contains various utility scripts for development, testing, and system management.

## 🚀 Service Starter Scripts

### Overview
The service starter scripts allow you to start Prefect server, Prefect workers, Streamlit UI, and MLflow server concurrently with a single command.

### Available Scripts

#### 1. Python Script (Cross-Platform)
**File**: `start_services.py`
**Usage**: `python scripts/start_services.py`
**Features**:
- Cross-platform compatibility (Windows, macOS, Linux)
- Process monitoring and logging
- Graceful shutdown with Ctrl+C
- Automatic error detection and cleanup
- Real-time output from both services

#### 2. Windows Batch Script
**File**: `start_services.bat`
**Usage**: `scripts\start_services.bat`
**Features**:
- Windows-specific optimizations
- Opens services in separate command windows
- Easy to stop (just close the windows)
- Environment validation

#### 3. Unix/Linux/macOS Shell Script
**File**: `start_services.sh`
**Usage**: `./scripts/start_services.sh`
**Features**:
- Unix/Linux/macOS specific
- Signal handling for graceful shutdown
- Background process management
- Environment validation

### Makefile Integration

The scripts are integrated into the Makefile for easy access:

```bash
# Start all services (Python script)
make run-services

# Start all services (Windows)
make run-services-windows

# Start all services (Unix/Linux/macOS)
make run-services-unix
```

### Service URLs

When services are running, you can access:
- **Streamlit UI**: http://localhost:8501
- **Prefect UI**: http://localhost:4200
- **MLflow UI**: http://localhost:5000
- **Prefect Workers**: daily, realtime, endofday, and hourly pools, default queue

### Troubleshooting

#### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the ports
   netstat -ano | findstr :8501  # Windows (Streamlit)
   netstat -ano | findstr :4200  # Windows (Prefect)
   netstat -ano | findstr :5000  # Windows (MLflow)
   lsof -i :8501                 # Unix/Linux/macOS (Streamlit)
   lsof -i :4200                 # Unix/Linux/macOS (Prefect)
   lsof -i :5000                 # Unix/Linux/macOS (MLflow)
   ```

2. **Python Path Issues**
   - Ensure you're running from the project root directory
   - Verify Python is in your PATH
   - Check that required packages are installed

3. **Permission Issues (Unix/Linux/macOS)**
   ```bash
   # Make shell script executable
   chmod +x scripts/start_services.sh
   ```

4. **Environment Variables**
   - Ensure `.env` file is properly configured
   - Check that database is running and accessible

#### Stopping Services

- **Python Script**: Press `Ctrl+C` in the terminal
- **Windows Batch**: Close the command windows
- **Unix Shell**: Press `Ctrl+C` in the terminal

## Other Scripts

### Database Management
- `check_db_direct.py` - Database health check
- `verify_migrations_simple.py` - Migration verification
- `create_mlflow_db.sql` - MLflow database setup

### Data Management
- `load_historical_data.py` - Historical data loading
- `manage_symbols.py` - Symbol management
- `manage_sectors.py` - Sector configuration

### Testing
- `run_tests.py` - Unified test runner
- `setup_test_env.py` - Test environment setup
- `check_env_file.py` - Environment file validation

### Analysis
- `run_pair_analysis.py` - Pair analysis execution
- `check_delisted_symbols.py` - Symbol maintenance

### Manual Operations
- `manual_save.py` - Manual data saving
- `check_postgres_data.py` - PostgreSQL data inspection

### MLflow Testing
- `test_mlflow_connection.py` - Test MLflow connection and experiment creation 