"""
WebSocket Configuration Loader

This module provides utilities to load and manage WebSocket configuration
for switching between Alpaca and data recycler modes.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class WebSocketConfig:
    """Configuration loader for WebSocket settings"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the WebSocket configuration loader
        
        Args:
            config_path: Path to config.yaml file. If None, uses default location.
        """
        if config_path is None:
            # Try multiple possible config paths
            possible_paths = [
                "config/config.yaml",  # Relative to current working directory
                Path(__file__).parent.parent.parent / "config" / "config.yaml",  # Relative to this file
                Path.cwd() / "config" / "config.yaml",  # Relative to current working directory
            ]
            
            # Use the first path that exists
            for path in possible_paths:
                if Path(path).exists():
                    config_path = path
                    break
            else:
                # If none exist, use the first one as default
                config_path = possible_paths[0]
        
        self.config_path = Path(config_path)
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f)
            logger.info(f"Loaded WebSocket configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration from {self.config_path}: {e}")
            raise
    
    def get_websocket_mode(self) -> str:
        """Get the current WebSocket mode (alpaca or recycler)"""
        mode = self._config.get('websocket', {}).get('mode', 'alpaca')
        logger.info(f"WebSocket mode: {mode}")
        return mode
    
    def get_websocket_symbols(self) -> list:
        """Get the symbols for websocket data collection"""
        symbols = self._config.get('websocket', {}).get('symbols', ['AAPL'])
        logger.info(f"WebSocket symbols: {symbols}")
        return symbols
    
    def is_recycler_mode(self) -> bool:
        """Check if the system is in recycler mode"""
        return self.get_websocket_mode() == 'recycler'
    
    def is_alpaca_mode(self) -> bool:
        """Check if the system is in Alpaca mode"""
        return self.get_websocket_mode() == 'alpaca'
    
    def get_recycler_config(self) -> Dict[str, Any]:
        """Get recycler configuration"""
        recycler_config = self._config.get('websocket', {}).get('recycler', {})
        logger.debug(f"Recycler config: {recycler_config}")
        return recycler_config
    
    def get_recycler_server_url(self) -> str:
        """Get the recycler server URL"""
        return self.get_recycler_config().get('server_url', 'ws://localhost:8765')
    
    def get_recycler_replay_mode(self) -> str:
        """Get the replay mode (loop, date_range, single_pass)"""
        return self.get_recycler_config().get('replay_mode', 'loop')
    
    def get_recycler_replay_speed(self) -> float:
        """Get the replay speed multiplier"""
        return self.get_recycler_config().get('replay_speed', 1.0)
    
    def get_recycler_date_range(self) -> Dict[str, str]:
        """Get the date range for replay"""
        return self.get_recycler_config().get('date_range', {
            'start_date': '2025-06-23',
            'end_date': '2025-06-30'
        })
    
    def get_recycler_symbols(self) -> list:
        """Get the symbols to replay"""
        return self.get_recycler_config().get('symbols', ['AAPL'])
    
    def get_recycler_loop_count(self) -> int:
        """Get the loop count (-1 for infinite, 1 for single pass)"""
        return self.get_recycler_config().get('loop_count', -1)
    
    def get_recycler_data_retention(self) -> Dict[str, Any]:
        """Get data retention settings"""
        return self.get_recycler_config().get('data_retention', {
            'recycled_data_days': 1,
            'auto_cleanup': True
        })
    
    def validate_config(self) -> bool:
        """Validate the current configuration"""
        try:
            mode = self.get_websocket_mode()
            if mode not in ['alpaca', 'recycler']:
                logger.error(f"Invalid WebSocket mode: {mode}")
                return False
            
            if mode == 'recycler':
                # Validate recycler-specific settings
                replay_mode = self.get_recycler_replay_mode()
                if replay_mode not in ['loop', 'date_range', 'single_pass']:
                    logger.error(f"Invalid replay mode: {replay_mode}")
                    return False
                
                replay_speed = self.get_recycler_replay_speed()
                if replay_speed <= 0:
                    logger.error(f"Invalid replay speed: {replay_speed}")
                    return False
                
                symbols = self.get_recycler_symbols()
                if not symbols:
                    logger.error("No symbols specified for replay")
                    return False
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def get_config_summary(self) -> str:
        """Get a summary of the current configuration"""
        mode = self.get_websocket_mode()
        summary = f"WebSocket Mode: {mode}"
        
        if mode == 'recycler':
            recycler_config = self.get_recycler_config()
            summary += f"\n  Server URL: {recycler_config.get('server_url')}"
            summary += f"\n  Replay Mode: {recycler_config.get('replay_mode')}"
            summary += f"\n  Replay Speed: {recycler_config.get('replay_speed')}x"
            summary += f"\n  Symbols: {recycler_config.get('symbols')}"
        
        return summary


# Global configuration instance
_websocket_config = None


def get_websocket_config() -> WebSocketConfig:
    """Get the global WebSocket configuration instance"""
    global _websocket_config
    if _websocket_config is None:
        _websocket_config = WebSocketConfig()
    return _websocket_config


def reload_config():
    """Reload the configuration from file"""
    global _websocket_config
    _websocket_config = None
    return get_websocket_config()


# Convenience functions
def is_recycler_mode() -> bool:
    """Check if system is in recycler mode"""
    return get_websocket_config().is_recycler_mode()


def is_alpaca_mode() -> bool:
    """Check if system is in Alpaca mode"""
    return get_websocket_config().is_alpaca_mode()


def get_websocket_mode() -> str:
    """Get current WebSocket mode"""
    return get_websocket_config().get_websocket_mode()


def get_websocket_symbols() -> list:
    """Get websocket symbols from configuration"""
    return get_websocket_config().get_websocket_symbols()


if __name__ == "__main__":
    # Test the configuration loader
    config = WebSocketConfig()
    print("Configuration Summary:")
    print(config.get_config_summary())
    print(f"\nValidation: {'PASSED' if config.validate_config() else 'FAILED'}") 