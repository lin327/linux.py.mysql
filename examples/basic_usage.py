"""
Basic usage examples for linux.py.mysql library.

This file demonstrates common use cases and best practices.
"""

from mysqlpy import Config, MySQLConnection, MySQLOperations
from mysqlpy.exceptions import MySQLConnectionError, MySQLQueryError


def example_basic_connection():
    """Example: Basic connection and query."""
    config = Config.from_dict({
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
        'database': 'testdb'
    })
    
    with MySQLConnection(config) as conn:
        ops = MySQLOperations(conn)
        
        # Simple query
        result = ops.fetch_one("SELECT VERSION()")
        print(f"MySQL version: {result[0]}")


def example_crud_operations():
    """Example: Complete CRUD operations."""
    config = Config.from_dict({
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
        'database': 'testdb'
    })
    
    with MySQLConnection(config) as conn:
        ops = MySQLOperations(conn)
        
        # CREATE
        user_id = ops.insert('users', {
            'name': 'John Doe',
            'email': 'john@example.com',
            'age': 30
        })
        print(f"Created user with ID: {user_id}")
        
        # READ
        user = ops.fetch_one(
            "SELECT * FROM users WHERE id = %s",
            (user_id,)
        )
        print(f"Fetched user: {user}")
        
        # UPDATE
        ops.update(
            'users',
            {'age': 31},
            'id = %s',
            (user_id,)
        )
        print(f"Updated user {user_id}")
        
        # DELETE
        ops.delete('users', 'id = %s', (user_id,))
        print(f"Deleted user {user_id}")


def example_batch_operations():
    """Example: Batch insert operations."""
    config = Config.from_dict({
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
        'database': 'testdb'
    })
    
    with MySQLConnection(config) as conn:
        ops = MySQLOperations(conn)
        
        # Batch insert
        users = [
            ('Alice', 'alice@example.com', 25),
            ('Bob', 'bob@example.com', 30),
            ('Charlie', 'charlie@example.com', 35)
        ]
        
        affected = ops.execute_many(
            "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)",
            users
        )
        print(f"Inserted {affected} users")


def example_error_handling():
    """Example: Proper error handling."""
    config = Config.from_dict({
        'host': 'localhost',
        'user': 'root',
        'password': 'wrong_password',
        'database': 'testdb'
    })
    
    try:
        with MySQLConnection(config) as conn:
            ops = MySQLOperations(conn)
            ops.fetch_all("SELECT * FROM users")
    except MySQLConnectionError as e:
        print(f"Connection failed: {e}")
    except MySQLQueryError as e:
        print(f"Query failed: {e}")


def example_fetch_as_dict():
    """Example: Fetching results as dictionaries."""
    config = Config.from_dict({
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
        'database': 'testdb'
    })
    
    with MySQLConnection(config) as conn:
        ops = MySQLOperations(conn)
        
        users = ops.fetch_dict("SELECT id, name, email FROM users LIMIT 10")
        for user in users:
            print(f"User {user['id']}: {user['name']} ({user['email']})")


def example_transaction():
    """Example: Transaction management."""
    config = Config.from_dict({
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
        'database': 'testdb'
    })
    
    conn = MySQLConnection(config)
    conn.connect()
    
    try:
        ops = MySQLOperations(conn)
        
        # Multiple operations in a transaction
        user_id = ops.insert('users', {
            'name': 'Transaction User',
            'email': 'transaction@example.com',
            'age': 25
        })
        
        ops.insert('user_logs', {
            'user_id': user_id,
            'action': 'user_created'
        })
        
        # Commit transaction
        conn.commit()
        print("Transaction committed successfully")
        
    except Exception as e:
        # Rollback on error
        conn.rollback()
        print(f"Transaction rolled back: {e}")
        
    finally:
        conn.disconnect()


if __name__ == '__main__':
    print("Linux.py.mysql Examples")
    print("-" * 50)
    
    # Note: These examples require a running MySQL instance
    # and appropriate database/table setup
    
    # Uncomment to run examples:
    # example_basic_connection()
    # example_crud_operations()
    # example_batch_operations()
    # example_error_handling()
    # example_fetch_as_dict()
    # example_transaction()
