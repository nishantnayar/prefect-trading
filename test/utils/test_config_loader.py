"""
Tests for config_loader module.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open
import yaml

from src.utils.config_loader import (
    find_config_file,
    load_config,
    get_config_section,
    get_variance_stability_config,
    get_sectors_config,
    get_mlflow_config,
    get_websocket_config
)


class TestConfigLoader:
    """Test cases for config_loader module."""
    
    def test_find_config_file_success(self):
        """Test successful config file finding."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            config_path.write_text("test: config")
            
            with patch('src.utils.config_loader.Path.cwd') as mock_cwd:
                mock_cwd.return_value = Path(temp_dir)
                result = find_config_file("config.yaml")
                
                assert result == config_path
    
    def test_find_config_file_not_found(self):
        """Test config file not found scenario."""
        # Mock the entire find_config_file function to test the not found path
        with patch('src.utils.config_loader.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path("/nonexistent")
            # Mock all Path.exists calls to return False
            with patch('pathlib.Path.exists', return_value=False):
                # Also mock the __file__ path
                with patch('src.utils.config_loader.__file__', '/nonexistent/file.py'):
                    result = find_config_file("nonexistent.yaml")
                    
                    assert result is None
    
    def test_find_config_file_with_env_var(self):
        """Test finding config file using environment variable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.yaml"
            config_path.write_text("test: config")
            
            with patch.dict(os.environ, {'CONFIG_PATH': temp_dir}):
                # Mock Path.cwd to return a path where config doesn't exist
                with patch('src.utils.config_loader.Path.cwd') as mock_cwd:
                    mock_cwd.return_value = Path("/nonexistent")
                    result = find_config_file("test_config.yaml")
                    
                    assert result == config_path
    
    def test_find_config_file_env_var_not_set(self):
        """Test when CONFIG_PATH environment variable is not set."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.utils.config_loader.Path.cwd') as mock_cwd:
                mock_cwd.return_value = Path("/nonexistent")
                # Mock all Path.exists calls to return False
                with patch('pathlib.Path.exists', return_value=False):
                    result = find_config_file("nonexistent.yaml")
                    
                    assert result is None
    
    def test_load_config_success(self):
        """Test successful config loading."""
        test_config = {"database": {"host": "localhost"}}
        config_yaml = yaml.dump(test_config)
        
        with patch('src.utils.config_loader.find_config_file') as mock_find:
            mock_find.return_value = Path("/test/config.yaml")
            
            with patch('builtins.open', mock_open(read_data=config_yaml)):
                result = load_config("config.yaml")
                
                assert result == test_config
    
    def test_load_config_file_not_found(self):
        """Test config loading when file not found."""
        with patch('src.utils.config_loader.find_config_file') as mock_find:
            mock_find.return_value = None
            
            result = load_config("config.yaml")
            
            assert result == {}
    
    def test_load_config_file_not_found_with_default(self):
        """Test config loading when file not found with default config."""
        default_config = {"default": "value"}
        
        with patch('src.utils.config_loader.find_config_file') as mock_find:
            mock_find.return_value = None
            
            result = load_config("config.yaml", default_config)
            
            assert result == default_config
    
    def test_load_config_file_error(self):
        """Test config loading when file read fails."""
        with patch('src.utils.config_loader.find_config_file') as mock_find:
            mock_find.return_value = Path("/test/config.yaml")
            
            with patch('builtins.open', side_effect=Exception("File error")):
                result = load_config("config.yaml")
                
                assert result == {}
    
    def test_load_config_file_error_with_default(self):
        """Test config loading when file read fails with default config."""
        default_config = {"default": "value"}
        
        with patch('src.utils.config_loader.find_config_file') as mock_find:
            mock_find.return_value = Path("/test/config.yaml")
            
            with patch('builtins.open', side_effect=Exception("File error")):
                result = load_config("config.yaml", default_config)
                
                assert result == default_config
    
    def test_get_config_section_success(self):
        """Test successful config section loading."""
        test_config = {"database": {"host": "localhost"}, "websocket": {"mode": "alpaca"}}
        
        with patch('src.utils.config_loader.load_config') as mock_load:
            mock_load.return_value = test_config
            
            result = get_config_section("database")
            
            assert result == {"host": "localhost"}
    
    def test_get_config_section_not_found(self):
        """Test config section loading when section not found."""
        test_config = {"database": {"host": "localhost"}}
        
        with patch('src.utils.config_loader.load_config') as mock_load:
            mock_load.return_value = test_config
            
            result = get_config_section("nonexistent")
            
            assert result == {}
    
    def test_get_config_section_not_found_with_default(self):
        """Test config section loading when section not found with default."""
        test_config = {"database": {"host": "localhost"}}
        default_section = {"default": "value"}
        
        with patch('src.utils.config_loader.load_config') as mock_load:
            mock_load.return_value = test_config
            
            result = get_config_section("nonexistent", default=default_section)
            
            assert result == default_section
    
    def test_get_variance_stability_config(self):
        """Test variance stability config loading."""
        with patch('src.utils.config_loader.get_config_section') as mock_get_section:
            mock_get_section.return_value = {
                "arch_test_pvalue_threshold": 0.05,
                "rolling_std_cv_threshold": 1.0
            }
            
            result = get_variance_stability_config()
            
            assert "arch_test_pvalue_threshold" in result
            assert "rolling_std_cv_threshold" in result
    
    def test_get_variance_stability_config_default(self):
        """Test variance stability config with default values."""
        with patch('src.utils.config_loader.load_config') as mock_load:
            mock_load.return_value = {}
            
            result = get_variance_stability_config()
            
            assert result["arch_test_pvalue_threshold"] == 1e-100
            assert result["rolling_std_cv_threshold"] == 2.0
            assert result["ljung_box_pvalue_threshold"] == 0.001
    
    def test_get_sectors_config(self):
        """Test sectors config loading."""
        with patch('src.utils.config_loader.get_config_section') as mock_get_section:
            mock_get_section.return_value = {
                "active": ["Technology", "Healthcare"],
                "available": ["Technology", "Healthcare", "Finance"]
            }
            
            result = get_sectors_config()
            
            assert "active" in result
            assert "available" in result
    
    def test_get_sectors_config_default(self):
        """Test sectors config with default values."""
        with patch('src.utils.config_loader.load_config') as mock_load:
            mock_load.return_value = {}
            
            result = get_sectors_config()
            
            assert result["active"] == ["Technology"]
            assert "Technology" in result["available"]
            assert "Healthcare" in result["available"]
    
    def test_get_mlflow_config(self):
        """Test MLflow config loading."""
        with patch('src.utils.config_loader.get_config_section') as mock_get_section:
            mock_get_section.return_value = {
                "tracking_uri": "http://custom:5000",
                "experiment_name": "custom_experiment"
            }
            
            result = get_mlflow_config()
            
            assert result["tracking_uri"] == "http://custom:5000"
            assert result["experiment_name"] == "custom_experiment"
    
    def test_get_mlflow_config_default(self):
        """Test MLflow config with default values."""
        with patch('src.utils.config_loader.load_config') as mock_load:
            mock_load.return_value = {}
            
            result = get_mlflow_config()
            
            assert result["tracking_uri"] == "http://localhost:5000"
            assert result["experiment_name"] == "pairs_trading"
            assert result["artifact_root"] == "file:./mlruns"
    
    def test_get_websocket_config(self):
        """Test WebSocket config loading."""
        with patch('src.utils.config_loader.get_config_section') as mock_get_section:
            mock_get_section.return_value = {
                "mode": "custom",
                "symbols": ["AAPL", "MSFT"]
            }
            
            result = get_websocket_config()
            
            assert result["mode"] == "custom"
            assert result["symbols"] == ["AAPL", "MSFT"]
    
    def test_get_websocket_config_default(self):
        """Test WebSocket config with default values."""
        with patch('src.utils.config_loader.load_config') as mock_load:
            mock_load.return_value = {}
            
            result = get_websocket_config()
            
            assert result["mode"] == "alpaca"
            assert result["symbols"] == ["AAPL"]


if __name__ == "__main__":
    pytest.main([__file__]) 