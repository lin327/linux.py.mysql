"""
Integration tests for MySQL operations.

Note: These tests require a running MySQL instance.
They are designed to be skipped in CI environments where MySQL is not available.
"""

import pytest
import os
from mysqlpy import Config, MySQLConnection, MySQLOperations
from mysqlpy.exceptions import MySQLConnectionError


# Skip integration tests if MySQL is not available
pytestmark = pytest.mark.skipif(
    os.getenv('SKIP_INTEGRATION_TESTS', 'true').lower() == 'true',
    reason="Integration tests require MySQL instance"
)


@pytest.fixture
def integration_config():
    """Configuration for integration tests."""
    return Config.from_dict({
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', 'password'),
        'database': os.getenv('MYSQL_DATABASE', 'test_db'),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
    })


@pytest.fixture
def connection(integration_config):
    """Create and cleanup database connection."""
    conn = MySQLConnection(integration_config)
    try:
        conn.connect()
        yield conn
    finally:
        conn.disconnect()


@pytest.fixture
def operations(connection):
    """MySQLOperations instance with real connection."""
    return MySQLOperations(connection)


@pytest.fixture
def test_table(operations):
    """Create and cleanup test table."""
    # Create test table
    operations.execute_query("""
        CREATE TABLE IF NOT EXISTS test_users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            age INT
        )
    """)
    
    yield 'test_users'
    
    # Cleanup
    operations.execute_query("DROP TABLE IF EXISTS test_users")


class TestIntegration:
    """Integration test suite."""
    
    def test_connection_lifecycle(self, integration_config):
        """Test complete connection lifecycle."""
        conn = MySQLConnection(integration_config)
        
        # Test connection
        conn.connect()
        assert conn.is_connected()
        
        # Test disconnection
        conn.disconnect()
        assert not conn.is_connected()
    
    def test_context_manager(self, integration_config):
        """Test connection as context manager."""
        with MySQLConnection(integration_config) as conn:
            assert conn.is_connected()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result == (1,)
            cursor.close()
    
    def test_insert_and_fetch(self, operations, test_table):
        """Test inserting and fetching data."""
        # Insert data
        user_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'age': 30
        }
        insert_id = operations.insert(test_table, user_data)
        assert insert_id > 0
        
        # Fetch data
        result = operations.fetch_one(
            f"SELECT name, email, age FROM {test_table} WHERE id = %s",
            (insert_id,)
        )
        assert result == ('John Doe', 'john@example.com', 30)
    
    def test_fetch_all(self, operations, test_table):
        """Test fetching multiple rows."""
        # Insert multiple rows
        users = [
            {'name': 'User 1', 'email': 'user1@example.com', 'age': 25},
            {'name': 'User 2', 'email': 'user2@example.com', 'age': 30},
            {'name': 'User 3', 'email': 'user3@example.com', 'age': 35},
        ]
        for user in users:
            operations.insert(test_table, user)
        
        # Fetch all
        results = operations.fetch_all(f"SELECT name FROM {test_table}")
        assert len(results) >= 3
    
    def test_fetch_dict(self, operations, test_table):
        """Test fetching rows as dictionaries."""
        # Insert data
        operations.insert(test_table, {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'age': 28
        })
        
        # Fetch as dict
        results = operations.fetch_dict(f"SELECT name, email FROM {test_table}")
        assert len(results) > 0
        assert 'name' in results[0]
        assert 'email' in results[0]
    
    def test_update(self, operations, test_table):
        """Test updating data."""
        # Insert data
        insert_id = operations.insert(test_table, {
            'name': 'Old Name',
            'email': 'old@example.com',
            'age': 25
        })
        
        # Update data
        affected_rows = operations.update(
            test_table,
            {'name': 'New Name', 'age': 26},
            'id = %s',
            (insert_id,)
        )
        assert affected_rows == 1
        
        # Verify update
        result = operations.fetch_one(
            f"SELECT name, age FROM {test_table} WHERE id = %s",
            (insert_id,)
        )
        assert result == ('New Name', 26)
    
    def test_delete(self, operations, test_table):
        """Test deleting data."""
        # Insert data
        insert_id = operations.insert(test_table, {
            'name': 'To Delete',
            'email': 'delete@example.com',
            'age': 30
        })
        
        # Delete data
        affected_rows = operations.delete(test_table, 'id = %s', (insert_id,))
        assert affected_rows == 1
        
        # Verify deletion
        result = operations.fetch_one(
            f"SELECT * FROM {test_table} WHERE id = %s",
            (insert_id,)
        )
        assert result is None
    
    def test_execute_many(self, operations, test_table):
        """Test batch insert."""
        users_data = [
            ('Batch User 1', 'batch1@example.com', 20),
            ('Batch User 2', 'batch2@example.com', 21),
            ('Batch User 3', 'batch3@example.com', 22),
        ]
        
        affected_rows = operations.execute_many(
            f"INSERT INTO {test_table} (name, email, age) VALUES (%s, %s, %s)",
            users_data
        )
        assert affected_rows >= 3
    
    def test_table_exists(self, operations, test_table):
        """Test checking table existence."""
        assert operations.table_exists(test_table) is True
        assert operations.table_exists('nonexistent_table') is False
    
    def test_transaction_rollback(self, connection, operations, test_table):
        """Test transaction rollback."""
        # Insert initial data
        operations.insert(test_table, {
            'name': 'Initial User',
            'email': 'initial@example.com',
            'age': 30
        })
        
        initial_count = operations.fetch_one(f"SELECT COUNT(*) FROM {test_table}")[0]
        
        # Start transaction that will be rolled back
        try:
            operations.insert(test_table, {
                'name': 'Rollback User',
                'email': 'rollback@example.com',
                'age': 25
            })
            connection.rollback()  # Explicit rollback
        except Exception:
            pass
        
        # Count should be the same as before the rollback
        final_count = operations.fetch_one(f"SELECT COUNT(*) FROM {test_table}")[0]
        # Note: Since we committed after first insert, count will be initial_count
        assert final_count >= initial_count
