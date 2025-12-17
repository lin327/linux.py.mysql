"""Unit tests for configuration management."""

import pytest
import json
import yaml
from pathlib import Path
from mysqlpy.config import Config
from mysqlpy.exceptions import MySQLConfigError


class TestConfig:
    """Test suite for Config class."""
    
    def test_config_from_dict_valid(self, sample_config_dict):
        """Test creating config from valid dictionary."""
        config = Config.from_dict(sample_config_dict)
        assert config.get('host') == 'localhost'
        assert config.get('user') == 'testuser'
        assert config.get('database') == 'testdb'
    
    def test_config_from_dict_missing_required_fields(self):
        """Test that missing required fields raise error."""
        incomplete_config = {'host': 'localhost'}
        with pytest.raises(MySQLConfigError) as exc_info:
            Config.from_dict(incomplete_config)
        assert 'Missing required configuration fields' in str(exc_info.value)
    
    def test_config_get_with_default(self, config):
        """Test getting config value with default."""
        assert config.get('nonexistent', 'default') == 'default'
    
    def test_config_get_existing_value(self, config):
        """Test getting existing config value."""
        assert config.get('host') == 'localhost'
    
    def test_config_to_dict(self, sample_config_dict):
        """Test converting config back to dictionary."""
        config = Config.from_dict(sample_config_dict)
        config_dict = config.to_dict()
        assert config_dict == sample_config_dict
    
    def test_config_from_json_file(self, tmp_path, sample_config_dict):
        """Test loading config from JSON file."""
        json_file = tmp_path / "config.json"
        with open(json_file, 'w') as f:
            json.dump(sample_config_dict, f)
        
        config = Config.from_json(str(json_file))
        assert config.get('host') == 'localhost'
    
    def test_config_from_json_file_not_found(self):
        """Test loading config from non-existent JSON file."""
        with pytest.raises(MySQLConfigError) as exc_info:
            Config.from_json('/nonexistent/config.json')
        assert 'not found' in str(exc_info.value)
    
    def test_config_from_json_invalid(self, tmp_path):
        """Test loading config from invalid JSON file."""
        json_file = tmp_path / "invalid.json"
        with open(json_file, 'w') as f:
            f.write("{ invalid json }")
        
        with pytest.raises(MySQLConfigError) as exc_info:
            Config.from_json(str(json_file))
        assert 'Invalid JSON' in str(exc_info.value)
    
    def test_config_from_yaml_file(self, tmp_path, sample_config_dict):
        """Test loading config from YAML file."""
        yaml_file = tmp_path / "config.yml"
        with open(yaml_file, 'w') as f:
            yaml.dump(sample_config_dict, f)
        
        config = Config.from_yaml(str(yaml_file))
        assert config.get('host') == 'localhost'
        assert config.get('database') == 'testdb'
    
    def test_config_from_yaml_file_not_found(self):
        """Test loading config from non-existent YAML file."""
        with pytest.raises(MySQLConfigError) as exc_info:
            Config.from_yaml('/nonexistent/config.yml')
        assert 'not found' in str(exc_info.value)
    
    def test_config_from_yaml_invalid(self, tmp_path):
        """Test loading config from invalid YAML file."""
        yaml_file = tmp_path / "invalid.yml"
        with open(yaml_file, 'w') as f:
            f.write("host: localhost\n  invalid: yaml: structure")
        
        with pytest.raises(MySQLConfigError) as exc_info:
            Config.from_yaml(str(yaml_file))
        assert 'Invalid YAML' in str(exc_info.value)
    
    def test_config_empty_dict(self):
        """Test creating config with empty dictionary."""
        config = Config.from_dict({})
        assert config.get('host') is None
        assert config.to_dict() == {}
