# linux.py.mysql

[![Tests](https://github.com/lin327/linux.py.mysql/workflows/Tests/badge.svg)](https://github.com/lin327/linux.py.mysql/actions)
[![codecov](https://codecov.io/gh/lin327/linux.py.mysql/branch/main/graph/badge.svg)](https://codecov.io/gh/lin327/linux.py.mysql)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

Enterprise-grade Python MySQL connection and operations library with comprehensive error handling, connection pooling, and robust testing infrastructure.

## Features

- **Connection Pooling**: Efficient connection management with built-in pooling
- **Error Handling**: Comprehensive exception hierarchy for precise error management
- **Configuration Management**: Support for JSON, YAML, and dictionary-based configuration
- **High-Level Operations**: Intuitive API for CRUD operations
- **Transaction Support**: Full transaction management with commit/rollback
- **Context Manager**: Pythonic context manager support for automatic resource cleanup
- **Enterprise-Grade Testing**: Comprehensive unit and integration test suites
- **Type Safety**: Full type hints for better IDE support
- **Logging**: Built-in logging for debugging and monitoring

## Installation

```bash
pip install -r requirements.txt
```

For development (includes testing tools):

```bash
pip install -r requirements-dev.txt
```

## Quick Start

### Basic Usage

```python
from mysqlpy import Config, MySQLConnection, MySQLOperations

# Create configuration
config = Config.from_dict({
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'mydb'
})

# Use context manager for automatic cleanup
with MySQLConnection(config) as conn:
    ops = MySQLOperations(conn)
    
    # Insert data
    user_id = ops.insert('users', {
        'name': 'John Doe',
        'email': 'john@example.com'
    })
    
    # Fetch data
    users = ops.fetch_all("SELECT * FROM users WHERE id > %s", (0,))
    
    # Update data
    ops.update('users', {'name': 'Jane Doe'}, 'id = %s', (user_id,))
    
    # Delete data
    ops.delete('users', 'id = %s', (user_id,))
```

### Configuration from Files

**YAML Configuration:**

```python
# config.yml
host: localhost
user: root
password: password
database: mydb
port: 3306
charset: utf8mb4

# Python code
config = Config.from_yaml('config.yml')
```

**JSON Configuration:**

```python
# config.json
{
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "mydb"
}

# Python code
config = Config.from_json('config.json')
```

### Advanced Operations

**Batch Insert:**

```python
users_data = [
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com')
]

ops.execute_many(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    users_data
)
```

**Fetch as Dictionaries:**

```python
users = ops.fetch_dict("SELECT id, name, email FROM users")
for user in users:
    print(f"User: {user['name']} ({user['email']})")
```

**Transaction Management:**

```python
conn = MySQLConnection(config)
conn.connect()

try:
    ops = MySQLOperations(conn)
    ops.insert('users', {'name': 'Test User', 'email': 'test@example.com'})
    ops.insert('audit_log', {'action': 'user_created'})
    conn.commit()
except Exception as e:
    conn.rollback()
    raise
finally:
    conn.disconnect()
```

## Architecture

The library is organized into several key components:

- **`mysqlpy.config`**: Configuration management with support for multiple formats
- **`mysqlpy.connection`**: Connection pooling and lifecycle management
- **`mysqlpy.operations`**: High-level CRUD operations interface
- **`mysqlpy.exceptions`**: Custom exception hierarchy for error handling

## Testing

The project includes comprehensive test coverage with both unit and integration tests.

### Running Unit Tests

Unit tests run quickly and don't require a MySQL instance:

```bash
pytest tests/unit/ -v
```

### Running Integration Tests

Integration tests require a MySQL instance. Set environment variables first:

```bash
export SKIP_INTEGRATION_TESTS=false
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD=password
export MYSQL_DATABASE=test_db

pytest tests/integration/ -v
```

### Running All Tests with Coverage

```bash
pytest --cov=mysqlpy --cov-report=html
```

View coverage report:

```bash
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
```

## Project Structure

```
linux.py.mysql/
├── mysqlpy/                 # Main package
│   ├── __init__.py         # Package exports
│   ├── config.py           # Configuration management
│   ├── connection.py       # Connection pooling
│   ├── operations.py       # CRUD operations
│   └── exceptions.py       # Custom exceptions
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   │   ├── test_config.py
│   │   ├── test_connection.py
│   │   ├── test_operations.py
│   │   └── test_exceptions.py
│   ├── integration/        # Integration tests
│   │   └── test_integration.py
│   └── conftest.py         # Pytest fixtures
├── .github/
│   └── workflows/
│       └── tests.yml       # CI/CD configuration
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── setup.py               # Package setup
├── pytest.ini             # Pytest configuration
└── README.md              # This file
```

## Error Handling

The library provides a comprehensive exception hierarchy:

```python
from mysqlpy.exceptions import (
    MySQLConnectionError,  # Connection-related errors
    MySQLQueryError,       # Query execution errors
    MySQLConfigError,      # Configuration errors
)

try:
    conn = MySQLConnection(config)
    conn.connect()
except MySQLConnectionError as e:
    print(f"Failed to connect: {e}")
except MySQLConfigError as e:
    print(f"Invalid configuration: {e}")
```

## Best Practices

1. **Use Context Managers**: Always use `with` statements for automatic resource cleanup
2. **Parameterized Queries**: Use parameterized queries to prevent SQL injection
3. **Connection Pooling**: Leverage built-in connection pooling for better performance
4. **Error Handling**: Catch specific exceptions for precise error handling
5. **Configuration Files**: Store sensitive credentials in config files, not in code
6. **Transaction Management**: Use transactions for operations that must succeed or fail together

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/lin327/linux.py.mysql.git
cd linux.py.mysql

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest -v
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/lin327/linux.py.mysql).
