"""Configuration management for MySQL connections."""

import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from .exceptions import MySQLConfigError


class Config:
    """
    Configuration manager for MySQL connections.
    
    Supports loading configuration from:
    - Dictionary
    - JSON file
    - YAML file
    
    Example:
        >>> config = Config.from_yaml('config.yml')
        >>> config.get('host')
        'localhost'
    """
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration.
        
        Args:
            config_dict: Dictionary containing configuration parameters
        """
        self._config = config_dict or {}
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate that required configuration parameters are present."""
        if not self._config:
            return
        
        required_fields = ['host', 'user', 'password', 'database']
        missing_fields = [field for field in required_fields 
                         if field not in self._config]
        
        if missing_fields:
            raise MySQLConfigError(
                f"Missing required configuration fields: {', '.join(missing_fields)}"
            )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Configuration parameters
            
        Returns:
            Config instance
        """
        return cls(config_dict)
    
    @classmethod
    def from_json(cls, filepath: str) -> 'Config':
        """
        Load configuration from JSON file.
        
        Args:
            filepath: Path to JSON configuration file
            
        Returns:
            Config instance
            
        Raises:
            MySQLConfigError: If file doesn't exist or is invalid
        """
        path = Path(filepath)
        if not path.exists():
            raise MySQLConfigError(f"Configuration file not found: {filepath}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            return cls(config_dict)
        except json.JSONDecodeError as e:
            raise MySQLConfigError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise MySQLConfigError(f"Error reading configuration file: {e}")
    
    @classmethod
    def from_yaml(cls, filepath: str) -> 'Config':
        """
        Load configuration from YAML file.
        
        Args:
            filepath: Path to YAML configuration file
            
        Returns:
            Config instance
            
        Raises:
            MySQLConfigError: If file doesn't exist or is invalid
        """
        path = Path(filepath)
        if not path.exists():
            raise MySQLConfigError(f"Configuration file not found: {filepath}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
            return cls(config_dict)
        except yaml.YAMLError as e:
            raise MySQLConfigError(f"Invalid YAML in configuration file: {e}")
        except Exception as e:
            raise MySQLConfigError(f"Error reading configuration file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self._config.copy()
