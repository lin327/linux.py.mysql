"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, MagicMock
from mysqlpy import Config


@pytest.fixture
def sample_config_dict():
    """Sample configuration dictionary for testing."""
    return {
        'host': 'localhost',
        'user': 'testuser',
        'password': 'testpass',
        'database': 'testdb',
        'port': 3306,
        'charset': 'utf8mb4'
    }


@pytest.fixture
def config(sample_config_dict):
    """Config instance for testing."""
    return Config.from_dict(sample_config_dict)


@pytest.fixture
def mock_mysql_connection():
    """Mock MySQL connection for testing."""
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True
    mock_conn.commit = Mock()
    mock_conn.rollback = Mock()
    mock_conn.close = Mock()
    return mock_conn


@pytest.fixture
def mock_cursor():
    """Mock MySQL cursor for testing."""
    mock = MagicMock()
    mock.execute = Mock()
    mock.fetchone = Mock()
    mock.fetchall = Mock()
    mock.fetchmany = Mock()
    mock.close = Mock()
    mock.rowcount = 1
    mock.lastrowid = 1
    return mock
