"""
Shared Mock Fixtures
===================

Common mock fixtures and utilities for testing.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit functions for UI testing."""
    mock_st = {
        'title': Mock(),
        'subheader': Mock(),
        'metric': Mock(),
        'dataframe': Mock(),
        'info': Mock(),
        'warning': Mock(),
        'success': Mock(),
        'error': Mock(),
        'caption': Mock(),
        'divider': Mock(),
        'button': Mock(return_value=False),
        'write': Mock(),
        'plotly_chart': Mock(),
        'columns': Mock(),
        'rerun': Mock(),
        'selectbox': Mock(return_value='AAPL'),
        'multiselect': Mock(return_value=['AAPL', 'GOOGL']),
        'date_input': Mock(return_value='2024-01-01'),
        'number_input': Mock(return_value=100),
        'text_input': Mock(return_value='test_input'),
        'sidebar': Mock(),
    }
    
    # Configure columns mock to return context managers
    def create_context_mock():
        mock = Mock()
        mock.__enter__ = Mock(return_value=mock)
        mock.__exit__ = Mock(return_value=None)
        return mock
    
    def columns_side_effect(num_cols):
        if isinstance(num_cols, list):
            return [create_context_mock() for _ in range(len(num_cols))]
        else:
            return [create_context_mock() for _ in range(num_cols)]
    
    mock_st['columns'].side_effect = columns_side_effect
    
    return mock_st


@pytest.fixture
def mock_alpaca_api():
    """Mock Alpaca API responses."""
    return {
        'get_bars': Mock(return_value=Mock(
            df=Mock(return_value=Mock(
                to_dict=Mock(return_value={
                    'open': [149.50, 150.00],
                    'high': [151.00, 151.50],
                    'low': [149.00, 149.50],
                    'close': [150.25, 150.75],
                    'volume': [50000000, 52000000]
                })
            ))
        )),
        'get_account': Mock(return_value=Mock(
            cash=10000.00,
            portfolio_value=50000.00,
            buying_power=10000.00
        )),
        'get_position': Mock(return_value=Mock(
            symbol='AAPL',
            qty=100,
            avg_entry_price=150.00,
            current_price=150.25
        ))
    }


@pytest.fixture
def mock_yahoo_api():
    """Mock Yahoo Finance API responses."""
    return {
        'get_historical_data': Mock(return_value={
            'AAPL': {
                '2024-01-01': {
                    'Open': 149.50,
                    'High': 151.00,
                    'Low': 149.00,
                    'Close': 150.25,
                    'Volume': 50000000
                }
            }
        }),
        'get_company_info': Mock(return_value={
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'market_cap': 2500000000000
        })
    }


@pytest.fixture
def mock_mlflow():
    """Mock MLflow functions for ML testing."""
    return {
        'set_tracking_uri': Mock(),
        'start_run': Mock(return_value=Mock(
            __enter__=Mock(return_value=Mock()),
            __exit__=Mock(return_value=None)
        )),
        'log_param': Mock(),
        'log_metric': Mock(),
        'log_artifact': Mock(),
        'save_model': Mock(),
        'load_model': Mock(return_value=Mock()),
        'search_runs': Mock(return_value=[]),
        'get_run': Mock(return_value=Mock(
            data=Mock(params={}, metrics={})
        ))
    }


@pytest.fixture
def mock_requests():
    """Mock requests library for API testing."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'success'}
    mock_response.text = '{"status": "success"}'
    
    return {
        'get': Mock(return_value=mock_response),
        'post': Mock(return_value=mock_response),
        'put': Mock(return_value=mock_response),
        'delete': Mock(return_value=mock_response)
    }


@pytest.fixture
def mock_pandas():
    """Mock pandas for data processing testing."""
    return {
        'read_csv': Mock(return_value=Mock()),
        'DataFrame': Mock(return_value=Mock()),
        'Series': Mock(return_value=Mock()),
        'concat': Mock(return_value=Mock()),
        'merge': Mock(return_value=Mock())
    }


@pytest.fixture
def mock_numpy():
    """Mock numpy for numerical operations testing."""
    return {
        'array': Mock(return_value=Mock()),
        'zeros': Mock(return_value=Mock()),
        'ones': Mock(return_value=Mock()),
        'random': Mock(
            normal=Mock(return_value=Mock()),
            rand=Mock(return_value=Mock())
        ),
        'mean': Mock(return_value=150.25),
        'std': Mock(return_value=2.5)
    }


@pytest.fixture
def mock_torch():
    """Mock PyTorch for ML model testing."""
    mock_tensor = Mock()
    mock_tensor.detach.return_value = mock_tensor
    mock_tensor.numpy.return_value = Mock()
    
    return {
        'tensor': Mock(return_value=mock_tensor),
        'zeros': Mock(return_value=mock_tensor),
        'ones': Mock(return_value=mock_tensor),
        'randn': Mock(return_value=mock_tensor),
        'nn': Mock(
            Linear=Mock(return_value=Mock()),
            LSTM=Mock(return_value=Mock()),
            GRU=Mock(return_value=Mock()),
            Sequential=Mock(return_value=Mock())
        ),
        'optim': Mock(
            Adam=Mock(return_value=Mock()),
            SGD=Mock(return_value=Mock())
        )
    }


@pytest.fixture
def mock_environment_variables():
    """Mock environment variables for testing."""
    return {
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/testdb',
        'ALPACA_API_KEY': 'test_alpaca_key',
        'ALPACA_SECRET_KEY': 'test_alpaca_secret',
        'YAHOO_API_KEY': 'test_yahoo_key',
        'MLFLOW_TRACKING_URI': 'http://localhost:5000',
        'ENVIRONMENT': 'test'
    }


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        'database': {
            'host': 'localhost',
            'port': 5432,
            'database': 'testdb',
            'user': 'test',
            'password': 'test'
        },
        'alpaca': {
            'api_key': 'test_key',
            'secret_key': 'test_secret',
            'base_url': 'https://paper-api.alpaca.markets'
        },
        'mlflow': {
            'tracking_uri': 'http://localhost:5000',
            'experiment_name': 'test_experiment'
        }
    } 