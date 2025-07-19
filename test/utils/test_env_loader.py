"""
Tests for env_loader module.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from src.utils.env_loader import (
    load_env_file,
    load_env_file_with_decouple,
    get_env,
    get_env_bool,
    get_env_int
)


class TestEnvLoader:
    """Test cases for env_loader module."""
    
    def test_load_env_file_success(self):
        """Test successful environment file loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("TEST_VAR=test_value\nDB_HOST=localhost")
            
            with patch('src.utils.env_loader.Path') as mock_path:
                mock_path.return_value.parent.parent.parent = Path(temp_dir)
                
                result = load_env_file(str(env_file))
                
                assert result is True
    
    def test_load_env_file_not_found(self):
        """Test environment file loading when file doesn't exist."""
        with patch('src.utils.env_loader.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = Path("/nonexistent")
            mock_path.return_value.exists.return_value = False
            
            result = load_env_file()
            
            assert result is False
    
    def test_load_env_file_exception(self):
        """Test environment file loading when exception occurs."""
        with patch('src.utils.env_loader.Path') as mock_path:
            mock_path.side_effect = Exception("Path error")
            
            result = load_env_file()
            
            assert result is False
    
    def test_load_env_file_with_custom_path(self):
        """Test environment file loading with custom path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / "custom.env"
            env_file.write_text("CUSTOM_VAR=custom_value")
            
            result = load_env_file(str(env_file))
            
            assert result is True
    
    def test_load_env_file_with_decouple_available(self):
        """Test decouple-based environment loading when decouple is available."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("DECOUPLE_VAR=decouple_value\nDB_PASSWORD=secret123")
            
            with patch('src.utils.env_loader.DECOUPLE_AVAILABLE', None):
                with patch('src.utils.env_loader.load_env_file') as mock_load:
                    mock_load.return_value = True
                    
                    with patch('builtins.__import__') as mock_import:
                        mock_import.return_value = MagicMock()
                        
                        result = load_env_file_with_decouple(str(env_file))
                        
                        assert result is True
    
    def test_load_env_file_with_decouple_not_available(self):
        """Test decouple-based environment loading when decouple is not available."""
        with patch('src.utils.env_loader.DECOUPLE_AVAILABLE', None):
            with patch('src.utils.env_loader.load_env_file') as mock_load:
                mock_load.return_value = True
                
                with patch('builtins.__import__', side_effect=ImportError):
                    result = load_env_file_with_decouple()
                    
                    assert result is True
                    mock_load.assert_called_once()
    
    def test_load_env_file_with_decouple_file_not_found(self):
        """Test decouple-based environment loading when file doesn't exist."""
        with patch('src.utils.env_loader.DECOUPLE_AVAILABLE', True):
            with patch('src.utils.env_loader.Path') as mock_path:
                mock_path.return_value.exists.return_value = False
                
                result = load_env_file_with_decouple()
                
                assert result is False
    
    def test_load_env_file_with_decouple_exception(self):
        """Test decouple-based environment loading when exception occurs."""
        with patch('src.utils.env_loader.DECOUPLE_AVAILABLE', True):
            with patch('src.utils.env_loader.Path') as mock_path:
                mock_path.side_effect = Exception("Path error")
                
                with patch('src.utils.env_loader.load_env_file') as mock_load:
                    mock_load.return_value = True
                    
                    result = load_env_file_with_decouple()
                    
                    assert result is True
                    mock_load.assert_called_once()
    
    def test_load_env_file_with_decouple_processing(self):
        """Test decouple-based environment loading with actual file processing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("TEST_VAR=test_value\n# Comment\nDB_HOST=localhost")
            
            with patch('src.utils.env_loader.DECOUPLE_AVAILABLE', True):
                with patch('src.utils.env_loader.Path') as mock_path:
                    mock_path.return_value.parent.parent.parent = Path(temp_dir)
                    mock_path.return_value.exists.return_value = True
                    
                    with patch('builtins.open', mock_open(read_data="TEST_VAR=test_value\nDB_HOST=localhost")):
                        with patch('decouple.Config') as mock_config:
                            mock_config_instance = MagicMock()
                            mock_config_instance.return_value = "processed_value"
                            mock_config.return_value = mock_config_instance
                            
                            result = load_env_file_with_decouple(str(env_file))
                            
                            assert result is True
    
    def test_load_env_file_with_decouple_processing_exception(self):
        """Test decouple-based environment loading when processing fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("TEST_VAR=test_value")
            
            with patch('src.utils.env_loader.DECOUPLE_AVAILABLE', True):
                with patch('src.utils.env_loader.Path') as mock_path:
                    mock_path.return_value.parent.parent.parent = Path(temp_dir)
                    mock_path.return_value.exists.return_value = True
                    
                    with patch('builtins.open', mock_open(read_data="TEST_VAR=test_value")):
                        with patch('decouple.Config') as mock_config:
                            mock_config_instance = MagicMock()
                            mock_config_instance.side_effect = Exception("Config error")
                            mock_config.return_value = mock_config_instance
                            
                            with patch('src.utils.env_loader.load_env_file') as mock_load:
                                mock_load.return_value = True
                                
                                result = load_env_file_with_decouple(str(env_file))
                                
                                assert result is True
                                mock_load.assert_called_once()
    
    def test_get_env_with_value(self):
        """Test getting environment variable with existing value."""
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            result = get_env('TEST_VAR')
            
            assert result == 'test_value'
    
    def test_get_env_with_default(self):
        """Test getting environment variable with default value."""
        with patch.dict(os.environ, {}, clear=True):
            result = get_env('NONEXISTENT_VAR', 'default_value')
            
            assert result == 'default_value'
    
    def test_get_env_bool_true_values(self):
        """Test getting boolean environment variable with true values."""
        true_values = ['true', 'TRUE', 'True', '1', 'yes', 'YES', 'Yes', 'on', 'ON', 'On']
        
        for value in true_values:
            with patch.dict(os.environ, {'BOOL_VAR': value}):
                result = get_env_bool('BOOL_VAR')
                
                assert result is True
    
    def test_get_env_bool_false_values(self):
        """Test getting boolean environment variable with false values."""
        false_values = ['false', 'FALSE', 'False', '0', 'no', 'NO', 'No', 'off', 'OFF', 'Off', 'anything_else']
        
        for value in false_values:
            with patch.dict(os.environ, {'BOOL_VAR': value}):
                result = get_env_bool('BOOL_VAR')
                
                assert result is False
    
    def test_get_env_bool_with_default(self):
        """Test getting boolean environment variable with default value."""
        with patch.dict(os.environ, {}, clear=True):
            result = get_env_bool('NONEXISTENT_BOOL', True)
            
            assert result is True
    
    def test_get_env_int_with_value(self):
        """Test getting integer environment variable with valid value."""
        with patch.dict(os.environ, {'INT_VAR': '42'}):
            result = get_env_int('INT_VAR')
            
            assert result == 42
    
    def test_get_env_int_with_default(self):
        """Test getting integer environment variable with default value."""
        with patch.dict(os.environ, {}, clear=True):
            result = get_env_int('NONEXISTENT_INT', 100)
            
            assert result == 100
    
    def test_get_env_int_invalid_value(self):
        """Test getting integer environment variable with invalid value."""
        with patch.dict(os.environ, {'INVALID_INT': 'not_a_number'}):
            result = get_env_int('INVALID_INT', 50)
            
            assert result == 50
    
    def test_get_env_int_none_value(self):
        """Test getting integer environment variable with None value."""
        with patch.dict(os.environ, {'NONE_INT': 'None'}):
            result = get_env_int('NONE_INT', 25)
            
            assert result == 25
    
    def test_load_env_file_with_decouple_import_error(self):
        """Test decouple import error handling."""
        with patch('src.utils.env_loader.DECOUPLE_AVAILABLE', None):
            with patch('src.utils.env_loader.load_env_file') as mock_load:
                mock_load.return_value = True
                
                with patch('builtins.__import__', side_effect=ImportError("No module named 'decouple'")):
                    result = load_env_file_with_decouple()
                    
                    assert result is True
                    mock_load.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__]) 