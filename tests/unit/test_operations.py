"""Unit tests for MySQL operations."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from mysqlpy.operations import MySQLOperations
from mysqlpy.connection import MySQLConnection
from mysqlpy.exceptions import MySQLQueryError
import mysql.connector


class TestMySQLOperations:
    """Test suite for MySQLOperations class."""
    
    @pytest.fixture
    def mock_connection(self, mock_mysql_connection, mock_cursor):
        """Mock MySQLConnection for testing."""
        conn = MagicMock(spec=MySQLConnection)
        conn.cursor.return_value = mock_cursor
        conn.commit = Mock()
        conn.rollback = Mock()
        return conn
    
    @pytest.fixture
    def operations(self, mock_connection):
        """MySQLOperations instance for testing."""
        return MySQLOperations(mock_connection)
    
    def test_init(self, mock_connection):
        """Test operations initialization."""
        ops = MySQLOperations(mock_connection)
        assert ops.connection == mock_connection
    
    def test_execute_query_success(self, operations, mock_connection, mock_cursor):
        """Test successful query execution."""
        mock_cursor.rowcount = 5
        
        result = operations.execute_query("INSERT INTO users VALUES (%s)", ("test",))
        
        assert result == 5
        mock_cursor.execute.assert_called_once_with("INSERT INTO users VALUES (%s)", ("test",))
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_execute_query_failure(self, operations, mock_connection, mock_cursor):
        """Test query execution failure."""
        mock_cursor.execute.side_effect = mysql.connector.Error("Query failed")
        
        with pytest.raises(MySQLQueryError) as exc_info:
            operations.execute_query("INVALID SQL")
        
        assert "Failed to execute query" in str(exc_info.value)
        mock_connection.rollback.assert_called_once()
    
    def test_execute_query_without_params(self, operations, mock_connection, mock_cursor):
        """Test query execution without parameters."""
        mock_cursor.rowcount = 1
        
        operations.execute_query("DELETE FROM users")
        
        mock_cursor.execute.assert_called_once_with("DELETE FROM users", ())
    
    def test_fetch_one_success(self, operations, mock_connection, mock_cursor):
        """Test fetching single row."""
        mock_cursor.fetchone.return_value = (1, 'John', 'Doe')
        
        result = operations.fetch_one("SELECT * FROM users WHERE id = %s", (1,))
        
        assert result == (1, 'John', 'Doe')
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_fetch_one_no_results(self, operations, mock_connection, mock_cursor):
        """Test fetching when no results."""
        mock_cursor.fetchone.return_value = None
        
        result = operations.fetch_one("SELECT * FROM users WHERE id = %s", (999,))
        
        assert result is None
    
    def test_fetch_one_failure(self, operations, mock_connection, mock_cursor):
        """Test fetch one failure."""
        mock_cursor.execute.side_effect = mysql.connector.Error("Fetch failed")
        
        with pytest.raises(MySQLQueryError) as exc_info:
            operations.fetch_one("SELECT * FROM users")
        
        assert "Failed to fetch data" in str(exc_info.value)
    
    def test_fetch_all_success(self, operations, mock_connection, mock_cursor):
        """Test fetching all rows."""
        mock_cursor.fetchall.return_value = [
            (1, 'John', 'Doe'),
            (2, 'Jane', 'Smith')
        ]
        
        result = operations.fetch_all("SELECT * FROM users")
        
        assert len(result) == 2
        assert result[0] == (1, 'John', 'Doe')
        mock_cursor.fetchall.assert_called_once()
    
    def test_fetch_all_empty(self, operations, mock_connection, mock_cursor):
        """Test fetching when no rows."""
        mock_cursor.fetchall.return_value = []
        
        result = operations.fetch_all("SELECT * FROM users WHERE 1=0")
        
        assert result == []
    
    def test_fetch_all_failure(self, operations, mock_connection, mock_cursor):
        """Test fetch all failure."""
        mock_cursor.execute.side_effect = mysql.connector.Error("Fetch failed")
        
        with pytest.raises(MySQLQueryError):
            operations.fetch_all("SELECT * FROM users")
    
    def test_fetch_dict_success(self, operations, mock_connection):
        """Test fetching rows as dictionaries."""
        dict_cursor = MagicMock()
        dict_cursor.fetchall.return_value = [
            {'id': 1, 'name': 'John'},
            {'id': 2, 'name': 'Jane'}
        ]
        mock_connection.cursor.return_value = dict_cursor
        
        result = operations.fetch_dict("SELECT id, name FROM users")
        
        assert len(result) == 2
        assert result[0]['name'] == 'John'
        mock_connection.cursor.assert_called_with(dictionary=True)
    
    def test_fetch_dict_failure(self, operations, mock_connection):
        """Test fetch dict failure."""
        dict_cursor = MagicMock()
        dict_cursor.execute.side_effect = mysql.connector.Error("Fetch failed")
        mock_connection.cursor.return_value = dict_cursor
        
        with pytest.raises(MySQLQueryError):
            operations.fetch_dict("SELECT * FROM users")
    
    def test_execute_many_success(self, operations, mock_connection, mock_cursor):
        """Test batch query execution."""
        mock_cursor.rowcount = 3
        params_list = [
            ('John', 'Doe'),
            ('Jane', 'Smith'),
            ('Bob', 'Johnson')
        ]
        
        result = operations.execute_many(
            "INSERT INTO users (first_name, last_name) VALUES (%s, %s)",
            params_list
        )
        
        assert result == 3
        mock_cursor.executemany.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    def test_execute_many_failure(self, operations, mock_connection, mock_cursor):
        """Test batch query failure."""
        mock_cursor.executemany.side_effect = mysql.connector.Error("Batch failed")
        
        with pytest.raises(MySQLQueryError) as exc_info:
            operations.execute_many("INSERT INTO users VALUES (%s)", [("test",)])
        
        assert "Failed to execute batch query" in str(exc_info.value)
        mock_connection.rollback.assert_called_once()
    
    def test_insert_success(self, operations, mock_connection, mock_cursor):
        """Test inserting a row."""
        mock_cursor.lastrowid = 42
        data = {'name': 'John Doe', 'email': 'john@example.com'}
        
        result = operations.insert('users', data)
        
        assert result == 42
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    def test_insert_failure(self, operations, mock_connection, mock_cursor):
        """Test insert failure."""
        mock_cursor.execute.side_effect = mysql.connector.Error("Insert failed")
        
        with pytest.raises(MySQLQueryError) as exc_info:
            operations.insert('users', {'name': 'John'})
        
        assert "Failed to insert data" in str(exc_info.value)
        mock_connection.rollback.assert_called_once()
    
    def test_update_success(self, operations, mock_connection, mock_cursor):
        """Test updating rows."""
        mock_cursor.rowcount = 2
        data = {'name': 'Updated Name', 'email': 'new@example.com'}
        
        result = operations.update('users', data, 'id = %s', (1,))
        
        assert result == 2
        mock_cursor.execute.assert_called_once()
        # Verify the query structure
        call_args = mock_cursor.execute.call_args[0]
        assert 'UPDATE users SET' in call_args[0]
        assert 'WHERE id = %s' in call_args[0]
    
    def test_update_with_multiple_conditions(self, operations, mock_connection, mock_cursor):
        """Test update with multiple WHERE conditions."""
        mock_cursor.rowcount = 1
        data = {'status': 'active'}
        
        operations.update('users', data, 'id = %s AND status = %s', (1, 'inactive'))
        
        mock_cursor.execute.assert_called_once()
    
    def test_delete_success(self, operations, mock_connection, mock_cursor):
        """Test deleting rows."""
        mock_cursor.rowcount = 3
        
        result = operations.delete('users', 'status = %s', ('inactive',))
        
        assert result == 3
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args[0]
        assert 'DELETE FROM users WHERE' in call_args[0]
    
    def test_delete_with_multiple_conditions(self, operations, mock_connection, mock_cursor):
        """Test delete with multiple conditions."""
        mock_cursor.rowcount = 1
        
        operations.delete('users', 'id = %s AND status = %s', (1, 'deleted'))
        
        mock_cursor.execute.assert_called_once()
    
    def test_table_exists_true(self, operations, mock_connection, mock_cursor):
        """Test checking if table exists (returns True)."""
        mock_cursor.fetchone.return_value = (1,)
        
        result = operations.table_exists('users')
        
        assert result is True
        mock_cursor.execute.assert_called_once()
    
    def test_table_exists_false(self, operations, mock_connection, mock_cursor):
        """Test checking if table exists (returns False)."""
        mock_cursor.fetchone.return_value = (0,)
        
        result = operations.table_exists('nonexistent_table')
        
        assert result is False
    
    def test_table_exists_no_result(self, operations, mock_connection, mock_cursor):
        """Test table_exists when no result returned."""
        mock_cursor.fetchone.return_value = None
        
        result = operations.table_exists('some_table')
        
        assert result is False
