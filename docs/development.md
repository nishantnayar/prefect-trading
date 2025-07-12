# Development Guide

## Overview

This guide provides comprehensive information for developers working on the Prefect Trading System. It covers coding standards, development workflows, testing practices, and deployment procedures.

> **📋 Quick Links**: [Architecture Decisions](architecture-decisions.md) | [Setup Guide](setup.md) | [Testing Guide](testing.md) | [UI Documentation](ui.md) | [API Documentation](api.md)

## Development Environment Setup

### Prerequisites
- Python 3.9 or higher
- PostgreSQL 12 or higher
- Git
- Docker (optional)

### Initial Setup
```bash
# Clone the repository
git clone https://github.com/your-username/prefect-trading.git
cd prefect-trading

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install-dev

# Setup pre-commit hooks
make pre-commit-install

# Configure environment
cp config/env.example .env
# Edit .env with your credentials
```

### IDE Configuration

#### VS Code
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### PyCharm
- Set project interpreter to virtual environment
- Enable auto-import optimization
- Configure code style to match Black formatting

## Coding Standards

### Python Style Guide
We follow PEP 8 with the following modifications:
- Line length: 88 characters (Black default)
- Use type hints for all function parameters and return values
- Use docstrings for all public functions and classes

### Code Formatting
```bash
# Format code
make format

# Check formatting
make format-check
```

### Import Organization
```python
# Standard library imports
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Third-party imports
import pandas as pd
import streamlit as st
from prefect import flow, task

# Local imports
from src.database.database_connectivity import DatabaseConnectivity
from src.utils.market_hours import is_market_open
```

### Type Hints
```python
from typing import Dict, List, Optional, Union
from datetime import datetime

def fetch_market_data(
    symbol: str,
    start_date: datetime,
    end_date: Optional[datetime] = None
) -> Dict[str, Union[str, float, int]]:
    """
    Fetch market data for a given symbol.
    
    Args:
        symbol: Stock symbol
        start_date: Start date for data
        end_date: End date for data (optional)
    
    Returns:
        Dictionary containing market data
    """
    pass
```

### Error Handling
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def safe_api_call(func):
    """Decorator for safe API calls with retry logic."""
    def wrapper(*args, **kwargs):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"API call failed after {max_retries} attempts")
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
    return wrapper
```

## Development Workflow

### Git Workflow
1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and commit**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

3. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention
We use [Conventional Commits](https://www.conventionalcommits.org/):
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

### Pre-commit Hooks
```bash
# Install pre-commit hooks
make pre-commit-install

# Run pre-commit on all files
make pre-commit-run
```

## Testing

### Test Structure
```
test/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/           # End-to-end tests
├── fixtures/      # Test fixtures
└── conftest.py    # Pytest configuration
```

### Writing Tests
```python
import pytest
from unittest.mock import Mock, patch
from src.data.sources.yahoo_finance_loader import YahooFinanceDataLoader

class TestYahooFinanceDataLoader:
    
    def test_initialization(self):
        """Test loader initialization."""
        loader = YahooFinanceDataLoader()
        assert loader is not None
    
    @pytest.mark.integration
    def test_data_fetching(self):
        """Test data fetching from Yahoo Finance."""
        loader = YahooFinanceDataLoader()
        data = loader.fetch_data('AAPL')
        assert data is not None
        assert 'symbol' in data
    
    @patch('src.data.sources.yahoo_finance_loader.requests.get')
    def test_error_handling(self, mock_get):
        """Test error handling."""
        mock_get.side_effect = Exception("Network error")
        loader = YahooFinanceDataLoader()
        with pytest.raises(Exception):
            loader.fetch_data('AAPL')
```

### Running Tests
```bash
# Run all tests
python scripts/run_tests.py

# Run specific test categories
python scripts/run_tests.py basic
python scripts/run_tests.py database
python scripts/run_tests.py quick

# Run with coverage
pytest --cov=src test/
```

For comprehensive testing information, see [Testing Guide](testing.md).

## Database Development

### Migration Guidelines
1. **Create new migration**
   ```sql
   -- src/database/migrations/002_new_feature/001_add_new_table.sql
   CREATE TABLE new_table (
       id SERIAL PRIMARY KEY,
       name VARCHAR(255) NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

2. **Add indexes for performance**
   ```sql
   CREATE INDEX idx_new_table_name ON new_table(name);
   ```

3. **Update migration documentation**
   ```markdown
   # Migration 002: Add New Feature
   
   - Added new_table for storing feature data
   - Added index on name column for performance
   ```

### Database Testing
```python
import pytest
from src.database.database_connectivity import DatabaseConnectivity

class TestDatabaseOperations:
    
    @pytest.fixture
    def db(self):
        """Database fixture."""
        return DatabaseConnectivity()
    
    def test_connection(self, db):
        """Test database connection."""
        assert db.is_connected()
    
    def test_data_insertion(self, db):
        """Test data insertion."""
        data = {'symbol': 'TEST', 'price': 100.0}
        result = db.insert_market_data(data)
        assert result is True
```

### Database Schema Verification

To verify that your database schema matches the consolidated migrations:

```bash
# Run verification script
python scripts/verify_migrations_simple.py

# Or use Makefile
make db-verify
```

This will check that all tables defined in your consolidated migration scripts are present in the database.

**Understanding Verification Results**:
- **✅ PASSED**: All application tables from migrations are present and correct
- **⚠️ EXTRA TABLES**: These are typically system tables (Prefect, MLflow, etc.) and are expected - not a problem
- **❌ MISSING TABLES**: These indicate actual schema mismatches that need attention

The verification focuses on your application schema and ignores system tables that are managed by other components.

## API Development

### API Design Principles
1. **RESTful design**
2. **Consistent error responses**
3. **Proper HTTP status codes**
4. **Input validation**
5. **Rate limiting**

### Example API Endpoint
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class MarketDataRequest(BaseModel):
    symbol: str
    start_date: datetime
    end_date: Optional[datetime] = None

class MarketDataResponse(BaseModel):
    symbol: str
    price: float
    volume: int
    timestamp: datetime

@app.get("/api/market-data/{symbol}")
async def get_market_data(
    symbol: str,
    start_date: datetime,
    end_date: Optional[datetime] = None
) -> List[MarketDataResponse]:
    """Get market data for a symbol."""
    try:
        data = await fetch_market_data(symbol, start_date, end_date)
        return [MarketDataResponse(**item) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## UI Development

### Streamlit Best Practices
1. **Component organization**
2. **State management**
3. **Error handling**
4. **Performance optimization**

### Example UI Component
```python
import streamlit as st
from typing import Dict, List

class MarketDataDisplay:
    """Market data display component."""
    
    def __init__(self):
        self.data = {}
    
    def display(self, data: Dict):
        """Display market data."""
        st.subheader("Market Data")
        
        if not data:
            st.warning("No data available")
            return
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Price", f"${data.get('price', 0):.2f}")
        
        with col2:
            st.metric("Volume", f"{data.get('volume', 0):,}")
        
        with col3:
            st.metric("Change", f"{data.get('change', 0):.2f}%")
```

## Performance Optimization

### PortfolioManager Singleton Pattern
```python
# Single instance across all UI components
class PortfolioManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PortfolioManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        # Initialize only once
```

### Intelligent Caching System
```python
# Cache with different durations for different data types
def _get_cached_data(self, key: str):
    """Get data from cache if it's still valid."""
    if key in self._cache and key in self._cache_timestamps:
        timestamp = self._cache_timestamps[key]
        cache_duration = 10 if key.startswith('orders_') else self._cache_duration
        if datetime.now() - timestamp < timedelta(seconds=cache_duration):
            return self._cache[key]
    return None

def _set_cached_data(self, key: str, data):
    """Store data in cache with timestamp."""
    self._cache[key] = data
    self._cache_timestamps[key] = datetime.now()
```

### Shared Instance Management
```python
# In UI modules (home.py, portfolio.py)
_portfolio_manager = None

def get_portfolio_manager():
    """Get or create a shared portfolio manager instance."""
    global _portfolio_manager
    if _portfolio_manager is None:
        _portfolio_manager = PortfolioManager()
    return _portfolio_manager

def clear_portfolio_manager():
    """Clear the shared portfolio manager instance."""
    global _portfolio_manager
    _portfolio_manager = None
```

For more details on performance optimizations, see [Architecture Decisions](architecture-decisions.md).

## MLflow Development Workflow

### Experiment Management
```python
import mlflow
from src.mlflow_manager import MLflowManager

# Initialize MLflow manager
mlflow_manager = MLflowManager()

# Create or get experiment
experiment_name = "pairs_trading/technology"
mlflow.set_experiment(experiment_name)

# Start a run
with mlflow.start_run():
    # Log parameters
    mlflow.log_param("learning_rate", 0.001)
    mlflow.log_param("epochs", 100)
    
    # Train model
    model = train_model()
    
    # Log metrics
    mlflow.log_metric("accuracy", 0.95)
    mlflow.log_metric("loss", 0.05)
    
    # Log model
    mlflow.pytorch.log_model(model, "model")
```

### Performance Tracking Integration
```python
from src.ml.model_performance_tracker import save_training_results

# After training, save performance to database
save_success = save_training_results(
    pair_symbol="NVDA-AMD",
    history=training_history,
    config=model_config,
    model_run_id=mlflow.active_run().info.run_id,
    experiment_name=experiment_name,
    early_stopped=False
)

# Rankings and trends are updated automatically
# No manual intervention required
```

### Training Pipeline
```python
# Run the complete training pipeline
python -m src.ml.train_gru_models

# This automatically:
# 1. Trains models for all pairs
# 2. Saves performance metrics to database
# 3. Updates model rankings
# 4. Calculates performance trends
# 5. Links all data to MLflow runs
```

### Periodic Rebaselining
```python
from prefect import flow, task
from src.mlflow_manager import MLflowManager

@task
def retrain_model():
    """Retrain model with latest data."""
    mlflow_manager = MLflowManager()
    return mlflow_manager.retrain_model()

@flow
def rebaseline_workflow():
    """Periodic model rebaselining workflow."""
    # Collect latest data
    # Retrain model
    # Evaluate performance
    # Register new model version
    pass
```

### Database Integration
- **Model Performance**: Stored in `model_performance` table with MLflow run IDs
- **Rankings**: Updated automatically in `model_rankings` table
- **Trends**: Calculated in `model_trends` table with 7-day and 30-day averages
- **Traceability**: All database records link to MLflow experiments via run IDs

For more details on MLflow integration, see [Architecture Decisions](architecture-decisions.md).

## Resources

- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [Prefect Documentation](https://docs.prefect.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Architecture Decisions](architecture-decisions.md) - Design rationale and decisions
- [Setup Guide](setup.md) - Installation and configuration
- [Testing Guide](testing.md) - Testing strategies and implementation
- [UI Documentation](ui.md) - User interface components and features 