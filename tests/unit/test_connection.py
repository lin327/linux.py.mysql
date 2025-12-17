"""Unit tests for MySQL connection management."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from mysqlpy.connection import MySQLConnection
from mysqlpy.config import Config
from mysqlpy.exceptions import MySQLConnectionError
import mysql.connector


class TestMySQLConnection:
    """Test suite for MySQLConnection class."""
    
    def test_init(self, config):
        """Test connection initialization."""
        conn = MySQLConnection(config, pool_name="testpool", pool_size=3)
        assert conn.config == config
        assert conn.pool_name == "testpool"
        assert conn.pool_size == 3
        assert conn._connection is None
        assert conn._pool is None
    
    @patch('mysqlpy.connection.MySQLConnectionPool')
    def test_create_pool_success(self, mock_pool_class, config):
        """Test successful pool creation."""
        mock_pool = MagicMock()
        mock_pool_class.return_value = mock_pool
        
        conn = MySQLConnection(config)
        pool = conn._create_pool()
        
        assert pool == mock_pool
        mock_pool_class.assert_called_once()
    
    @patch('mysqlpy.connection.MySQLConnectionPool')
    def test_create_pool_failure(self, mock_pool_class, config):
        """Test pool creation failure."""
        mock_pool_class.side_effect = mysql.connector.Error("Pool creation failed")
        
        conn = MySQLConnection(config)
        with pytest.raises(MySQLConnectionError) as exc_info:
            conn._create_pool()
        assert "Failed to create connection pool" in str(exc_info.value)
    
    @patch('mysqlpy.connection.MySQLConnectionPool')
    def test_connect_success(self, mock_pool_class, config):
        """Test successful connection."""
        mock_pool = MagicMock()
        mock_connection = MagicMock()
        mock_pool.get_connection.return_value = mock_connection
        mock_pool_class.return_value = mock_pool
        
        conn = MySQLConnection(config)
        conn.connect()
        
        assert conn._connection == mock_connection
        mock_pool.get_connection.assert_called_once()
    
    @patch('mysqlpy.connection.MySQLConnectionPool')
    def test_connect_failure(self, mock_pool_class, config):
        """Test connection failure."""
        mock_pool = MagicMock()
        mock_pool.get_connection.side_effect = mysql.connector.Error("Connection failed")
        mock_pool_class.return_value = mock_pool
        
        conn = MySQLConnection(config)
        with pytest.raises(MySQLConnectionError) as exc_info:
            conn.connect()
        assert "Failed to connect to database" in str(exc_info.value)
    
    def test_disconnect(self, config, mock_mysql_connection):
        """Test disconnection."""
        conn = MySQLConnection(config)
        conn._connection = mock_mysql_connection
        
        conn.disconnect()
        
        mock_mysql_connection.close.assert_called_once()
        assert conn._connection is None
    
    def test_disconnect_when_not_connected(self, config):
        """Test disconnect when not connected."""
        conn = MySQLConnection(config)
        # Should not raise exception
        conn.disconnect()
    
    def test_is_connected_true(self, config, mock_mysql_connection):
        """Test is_connected returns True when connected."""
        conn = MySQLConnection(config)
        conn._connection = mock_mysql_connection
        
        assert conn.is_connected() is True
    
    def test_is_connected_false(self, config):
        """Test is_connected returns False when not connected."""
        conn = MySQLConnection(config)
        assert conn.is_connected() is False
    
    def test_is_connected_false_when_disconnected(self, config, mock_mysql_connection):
        """Test is_connected returns False after disconnection."""
        mock_mysql_connection.is_connected.return_value = False
        conn = MySQLConnection(config)
        conn._connection = mock_mysql_connection
        
        assert conn.is_connected() is False
    
    @patch('mysqlpy.connection.MySQLConnectionPool')
    def test_reconnect(self, mock_pool_class, config):
        """Test reconnection."""
        mock_pool = MagicMock()
        mock_connection = MagicMock()
        mock_pool.get_connection.return_value = mock_connection
        mock_pool_class.return_value = mock_pool
        
        conn = MySQLConnection(config)
        conn._connection = mock_connection
        conn.reconnect()
        
        # Should have created new connection
        assert conn._connection == mock_connection
    
    def test_get_connection_when_connected(self, config, mock_mysql_connection):
        """Test getting connection when connected."""
        conn = MySQLConnection(config)
        conn._connection = mock_mysql_connection
        
        result = conn.get_connection()
        assert result == mock_mysql_connection
    
    def test_get_connection_when_not_connected(self, config):
        """Test getting connection when not connected."""
        conn = MySQLConnection(config)
        
        with pytest.raises(MySQLConnectionError) as exc_info:
            conn.get_connection()
        assert "Not connected to database" in str(exc_info.value)
    
    @patch('mysqlpy.connection.MySQLConnectionPool')
    def test_cursor_creates_connection_if_needed(self, mock_pool_class, config):
        """Test cursor creates connection if not connected."""
        mock_pool = MagicMock()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_pool.get_connection.return_value = mock_connection
        mock_pool_class.return_value = mock_pool
        
        conn = MySQLConnection(config)
        cursor = conn.cursor()
        
        assert cursor == mock_cursor
        mock_connection.cursor.assert_called_once()
    
    def test_cursor_when_connected(self, config, mock_mysql_connection):
        """Test cursor when already connected."""
        mock_cursor = MagicMock()
        mock_mysql_connection.cursor.return_value = mock_cursor
        
        conn = MySQLConnection(config)
        conn._connection = mock_mysql_connection
        
        cursor = conn.cursor()
        assert cursor == mock_cursor
    
    def test_commit(self, config, mock_mysql_connection):
        """Test commit transaction."""
        conn = MySQLConnection(config)
        conn._connection = mock_mysql_connection
        
        conn.commit()
        mock_mysql_connection.commit.assert_called_once()
    
    def test_rollback(self, config, mock_mysql_connection):
        """Test rollback transaction."""
        conn = MySQLConnection(config)
        conn._connection = mock_mysql_connection
        
        conn.rollback()
        mock_mysql_connection.rollback.assert_called_once()
    
    @patch('mysqlpy.connection.MySQLConnectionPool')
    def test_context_manager_success(self, mock_pool_class, config):
        """Test context manager with successful operations."""
        mock_pool = MagicMock()
        mock_connection = MagicMock()
        mock_pool.get_connection.return_value = mock_connection
        mock_pool_class.return_value = mock_pool
        
        with MySQLConnection(config) as conn:
            assert conn._connection == mock_connection
        
        mock_connection.commit.assert_called_once()
        mock_connection.close.assert_called_once()
    
    @patch('mysqlpy.connection.MySQLConnectionPool')
    def test_context_manager_with_exception(self, mock_pool_class, config):
        """Test context manager with exception (should rollback)."""
        mock_pool = MagicMock()
        mock_connection = MagicMock()
        mock_pool.get_connection.return_value = mock_connection
        mock_pool_class.return_value = mock_pool
        
        try:
            with MySQLConnection(config) as conn:
                raise ValueError("Test error")
        except ValueError:
            pass
        
        mock_connection.rollback.assert_called_once()
        mock_connection.commit.assert_not_called()
        mock_connection.close.assert_called_once()
