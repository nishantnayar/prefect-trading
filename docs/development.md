# Development Guide

## Overview

This guide provides comprehensive information for developers working on the Prefect Trading System. It covers coding standards, development workflows, testing practices, and deployment procedures.

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
make test

# Run specific test categories
make test-unit
make test-integration
make test-e2e

# Run with coverage
make test-coverage
```

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

### Database Optimization
1. **Use appropriate indexes**
2. **Optimize queries**
3. **Connection pooling**
4. **Query caching**

### Code Optimization
```python
# Use async/await for I/O operations
async def fetch_multiple_symbols(symbols: List[str]) -> List[Dict]:
    """Fetch data for multiple symbols concurrently."""
    tasks = [fetch_symbol_data(symbol) for symbol in symbols]
    return await asyncio.gather(*tasks)

# Use generators for large datasets
def process_large_dataset(data: List[Dict]) -> Generator[Dict, None, None]:
    """Process large dataset using generator."""
    for item in data:
        processed_item = process_item(item)
        yield processed_item
```

## Security

### Security Best Practices
1. **Input validation**
2. **SQL injection prevention**
3. **API key management**
4. **Error message sanitization**

### Example Security Implementation
```python
import re
from typing import Optional

def validate_symbol(symbol: str) -> bool:
    """Validate stock symbol format."""
    pattern = r'^[A-Z]{1,5}$'
    return bool(re.match(pattern, symbol))

def sanitize_input(input_str: str) -> str:
    """Sanitize user input."""
    return re.sub(r'[<>"\']', '', input_str)

def secure_api_call(api_key: str, endpoint: str) -> Optional[Dict]:
    """Make secure API call."""
    if not api_key:
        raise ValueError("API key is required")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Make API call with proper error handling
    pass
```

## Monitoring and Logging

### Logging Configuration
```python
import logging
import sys
from loguru import logger

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO"
)
logger.add(
    "logs/trading_system.log",
    rotation="1 day",
    retention="30 days",
    level="DEBUG"
)
```

### Performance Monitoring
```python
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper
```

## Deployment

### Production Deployment
1. **Environment configuration**
2. **Database setup**
3. **Service configuration**
4. **Monitoring setup**

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501 4200

CMD ["streamlit", "run", "src/ui/streamlit_app.py"]
```

### CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: make test
    
    - name: Deploy
      run: make deploy
```

## Troubleshooting

### Common Issues
1. **Database connection errors**
2. **API rate limiting**
3. **Memory leaks**
4. **Performance issues**

### Debugging Tools
```python
import pdb
import traceback

def debug_function():
    """Example debugging function."""
    try:
        # Your code here
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error(traceback.format_exc())
        pdb.set_trace()  # Interactive debugger
```

## Resources

- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [Prefect Documentation](https://docs.prefect.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pytest Documentation](https://docs.pytest.org/) 