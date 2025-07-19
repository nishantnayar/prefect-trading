"""
Tests for websocket_config module.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from src.utils.websocket_config import (
    WebSocketConfig,
    get_websocket_config,
    reload_config,
    is_recycler_mode,
    is_alpaca_mode,
    get_websocket_mode,
    get_websocket_symbols
)


class TestWebSocketConfig:
    """Test cases for WebSocketConfig class."""
    
    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration for testing."""
        return {
            'websocket': {
                'mode': 'alpaca',
                'symbols': ['AAPL', 'MSFT', 'GOOGL'],
                'recycler': {
                    'server_url': 'ws://localhost:8765',
                    'replay_mode': 'loop',
                    'replay_speed': 1.5,
                    'date_range': {
                        'start_date': '2025-01-01',
                        'end_date': '2025-01-31'
                    },
                    'symbols': ['AAPL', 'MSFT'],
                    'loop_count': 3,
                    'data_retention': {
                        'recycled_data_days': 7,
                        'auto_cleanup': False
                    }
                }
            }
        }
    
    def test_websocket_config_initialization(self, sample_config):
        """Test WebSocketConfig initialization."""
        config_yaml = yaml.dump(sample_config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            with patch('src.utils.websocket_config.Path') as mock_path:
                mock_path.return_value = Path("/test/config.yaml")
                
                config = WebSocketConfig("/test/config.yaml")
                
                assert config.config_path == Path("/test/config.yaml")
                assert config._config == sample_config
    
    def test_websocket_config_default_path(self):
        """Test WebSocketConfig initialization with default path."""
        sample_config = {'websocket': {'mode': 'alpaca'}}
        config_yaml = yaml.dump(sample_config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            with patch('src.utils.websocket_config.Path') as mock_path:
                mock_path.return_value.parent.parent.parent = Path("/test")
                mock_path.return_value = Path("/test/config/config.yaml")
                
                config = WebSocketConfig()
                
                assert config.config_path == Path("/test/config/config.yaml")
    
    def test_websocket_config_load_error(self):
        """Test WebSocketConfig initialization when config loading fails."""
        with patch('builtins.open', side_effect=Exception("File not found")):
            with pytest.raises(Exception, match="File not found"):
                WebSocketConfig("/nonexistent/config.yaml")
    
    def test_get_websocket_mode(self, sample_config):
        """Test getting WebSocket mode."""
        config_yaml = yaml.dump(sample_config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            mode = config.get_websocket_mode()
            
            assert mode == 'alpaca'
    
    def test_get_websocket_mode_default(self):
        """Test getting WebSocket mode with default value."""
        config_data = {'websocket': {}}
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            mode = config.get_websocket_mode()
            
            assert mode == 'alpaca'
    
    def test_get_websocket_symbols(self, sample_config):
        """Test getting WebSocket symbols."""
        config_yaml = yaml.dump(sample_config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            symbols = config.get_websocket_symbols()
            
            assert symbols == ['AAPL', 'MSFT', 'GOOGL']
    
    def test_get_websocket_symbols_default(self):
        """Test getting WebSocket symbols with default value."""
        config_data = {'websocket': {}}
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            symbols = config.get_websocket_symbols()
            
            assert symbols == ['AAPL']
    
    def test_is_recycler_mode_true(self):
        """Test recycler mode check when mode is recycler."""
        config_data = {'websocket': {'mode': 'recycler'}}
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            assert config.is_recycler_mode() is True
    
    def test_is_recycler_mode_false(self):
        """Test recycler mode check when mode is not recycler."""
        config_data = {'websocket': {'mode': 'alpaca'}}
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            assert config.is_recycler_mode() is False
    
    def test_is_alpaca_mode_true(self):
        """Test Alpaca mode check when mode is alpaca."""
        config_data = {'websocket': {'mode': 'alpaca'}}
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            assert config.is_alpaca_mode() is True
    
    def test_is_alpaca_mode_false(self):
        """Test Alpaca mode check when mode is not alpaca."""
        config_data = {'websocket': {'mode': 'recycler'}}
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            assert config.is_alpaca_mode() is False
    
    def test_get_recycler_config(self, sample_config):
        """Test getting recycler configuration."""
        config_yaml = yaml.dump(sample_config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            recycler_config = config.get_recycler_config()
            
            assert recycler_config['server_url'] == 'ws://localhost:8765'
            assert recycler_config['replay_mode'] == 'loop'
            assert recycler_config['replay_speed'] == 1.5
    
    def test_get_recycler_config_empty(self):
        """Test getting recycler configuration when not specified."""
        config_data = {'websocket': {}}
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            recycler_config = config.get_recycler_config()
            
            assert recycler_config == {}
    
    def test_get_recycler_server_url(self, sample_config):
        """Test getting recycler server URL."""
        config_yaml = yaml.dump(sample_config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            server_url = config.get_recycler_server_url()
            
            assert server_url == 'ws://localhost:8765'
    
    def test_get_recycler_server_url_default(self):
        """Test getting recycler server URL with default value."""
        config_data = {'websocket': {'recycler': {}}}
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            server_url = config.get_recycler_server_url()
            
            assert server_url == 'ws://localhost:8765'
    
    def test_get_recycler_replay_mode(self, sample_config):
        """Test getting recycler replay mode."""
        config_yaml = yaml.dump(sample_config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            replay_mode = config.get_recycler_replay_mode()
            
            assert replay_mode == 'loop'
    
    def test_get_recycler_replay_speed(self, sample_config):
        """Test getting recycler replay speed."""
        config_yaml = yaml.dump(sample_config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            replay_speed = config.get_recycler_replay_speed()
            
            assert replay_speed == 1.5
    
    def test_get_recycler_date_range(self, sample_config):
        """Test getting recycler date range."""
        config_yaml = yaml.dump(sample_config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            date_range = config.get_recycler_date_range()
            
            assert date_range['start_date'] == '2025-01-01'
            assert date_range['end_date'] == '2025-01-31'
    
    def test_get_recycler_symbols(self, sample_config):
        """Test getting recycler symbols."""
        config_yaml = yaml.dump(sample_config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            symbols = config.get_recycler_symbols()
            
            assert symbols == ['AAPL', 'MSFT']
    
    def test_get_recycler_loop_count(self, sample_config):
        """Test getting recycler loop count."""
        config_yaml = yaml.dump(sample_config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            loop_count = config.get_recycler_loop_count()
            
            assert loop_count == 3
    
    def test_get_recycler_data_retention(self, sample_config):
        """Test getting recycler data retention settings."""
        config_yaml = yaml.dump(sample_config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            data_retention = config.get_recycler_data_retention()
            
            assert data_retention['recycled_data_days'] == 7
            assert data_retention['auto_cleanup'] is False
    
    def test_validate_config_valid_alpaca(self):
        """Test configuration validation with valid Alpaca config."""
        config_data = {'websocket': {'mode': 'alpaca'}}
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            is_valid = config.validate_config()
            
            assert is_valid is True
    
    def test_validate_config_valid_recycler(self):
        """Test configuration validation with valid recycler config."""
        config_data = {
            'websocket': {
                'mode': 'recycler',
                'recycler': {
                    'replay_mode': 'loop',
                    'replay_speed': 1.0,
                    'symbols': ['AAPL']
                }
            }
        }
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            is_valid = config.validate_config()
            
            assert is_valid is True
    
    def test_validate_config_invalid_mode(self):
        """Test configuration validation with invalid mode."""
        config_data = {'websocket': {'mode': 'invalid_mode'}}
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            is_valid = config.validate_config()
            
            assert is_valid is False
    
    def test_validate_config_invalid_replay_mode(self):
        """Test configuration validation with invalid replay mode."""
        config_data = {
            'websocket': {
                'mode': 'recycler',
                'recycler': {
                    'replay_mode': 'invalid_replay_mode',
                    'replay_speed': 1.0,
                    'symbols': ['AAPL']
                }
            }
        }
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            is_valid = config.validate_config()
            
            assert is_valid is False
    
    def test_validate_config_invalid_replay_speed(self):
        """Test configuration validation with invalid replay speed."""
        config_data = {
            'websocket': {
                'mode': 'recycler',
                'recycler': {
                    'replay_mode': 'loop',
                    'replay_speed': 0,
                    'symbols': ['AAPL']
                }
            }
        }
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            is_valid = config.validate_config()
            
            assert is_valid is False
    
    def test_validate_config_no_symbols(self):
        """Test configuration validation with no symbols."""
        config_data = {
            'websocket': {
                'mode': 'recycler',
                'recycler': {
                    'replay_mode': 'loop',
                    'replay_speed': 1.0,
                    'symbols': []
                }
            }
        }
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            is_valid = config.validate_config()
            
            assert is_valid is False
    
    def test_validate_config_exception(self):
        """Test configuration validation when exception occurs."""
        config_data = {'websocket': {'mode': 'alpaca'}}
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            with patch.object(config, 'get_websocket_mode', side_effect=Exception("Test error")):
                is_valid = config.validate_config()
                
                assert is_valid is False
    
    def test_get_config_summary_alpaca(self):
        """Test getting configuration summary for Alpaca mode."""
        config_data = {'websocket': {'mode': 'alpaca'}}
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            summary = config.get_config_summary()
            
            assert "WebSocket Mode: alpaca" in summary
    
    def test_get_config_summary_recycler(self):
        """Test getting configuration summary for recycler mode."""
        config_data = {
            'websocket': {
                'mode': 'recycler',
                'recycler': {
                    'server_url': 'ws://localhost:8765',
                    'replay_mode': 'loop',
                    'replay_speed': 1.5,
                    'symbols': ['AAPL', 'MSFT']
                }
            }
        }
        config_yaml = yaml.dump(config_data)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            config = WebSocketConfig("/test/config.yaml")
            
            summary = config.get_config_summary()
            
            assert "WebSocket Mode: recycler" in summary
            assert "Server URL: ws://localhost:8765" in summary
            assert "Replay Mode: loop" in summary
            assert "Replay Speed: 1.5x" in summary
            assert "Symbols: ['AAPL', 'MSFT']" in summary


class TestWebSocketConfigFunctions:
    """Test cases for convenience functions."""
    
    def test_get_websocket_config_singleton(self):
        """Test that get_websocket_config returns singleton instance."""
        config1 = get_websocket_config()
        config2 = get_websocket_config()
        
        assert config1 is config2
    
    def test_reload_config(self):
        """Test reloading configuration."""
        config1 = get_websocket_config()
        config2 = reload_config()
        
        assert config1 is not config2
    
    def test_is_recycler_mode_function(self):
        """Test is_recycler_mode convenience function."""
        with patch('src.utils.websocket_config.get_websocket_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.is_recycler_mode.return_value = True
            mock_get_config.return_value = mock_config
            
            result = is_recycler_mode()
            
            assert result is True
            mock_config.is_recycler_mode.assert_called_once()
    
    def test_is_alpaca_mode_function(self):
        """Test is_alpaca_mode convenience function."""
        with patch('src.utils.websocket_config.get_websocket_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.is_alpaca_mode.return_value = True
            mock_get_config.return_value = mock_config
            
            result = is_alpaca_mode()
            
            assert result is True
            mock_config.is_alpaca_mode.assert_called_once()
    
    def test_get_websocket_mode_function(self):
        """Test get_websocket_mode convenience function."""
        with patch('src.utils.websocket_config.get_websocket_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.get_websocket_mode.return_value = 'alpaca'
            mock_get_config.return_value = mock_config
            
            result = get_websocket_mode()
            
            assert result == 'alpaca'
            mock_config.get_websocket_mode.assert_called_once()
    
    def test_get_websocket_symbols_function(self):
        """Test get_websocket_symbols convenience function."""
        with patch('src.utils.websocket_config.get_websocket_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.get_websocket_symbols.return_value = ['AAPL', 'MSFT']
            mock_get_config.return_value = mock_config
            
            result = get_websocket_symbols()
            
            assert result == ['AAPL', 'MSFT']
            mock_config.get_websocket_symbols.assert_called_once()
    
    def test_main_block(self):
        """Test the main block execution."""
        with patch('builtins.print') as mock_print:
            with patch('src.utils.websocket_config.WebSocketConfig') as mock_config_class:
                mock_config = MagicMock()
                mock_config.get_config_summary.return_value = "Test Summary"
                mock_config.validate_config.return_value = True
                mock_config_class.return_value = mock_config
                
                # Import and execute the main block
                import src.utils.websocket_config
                
                # The main block should have been executed during import
                # We can't directly test it, but we can verify the module loaded correctly
                assert hasattr(src.utils.websocket_config, 'WebSocketConfig')


if __name__ == "__main__":
    pytest.main([__file__]) 