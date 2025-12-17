"""Unit tests for custom exceptions."""

import pytest
from mysqlpy.exceptions import (
    MySQLBaseException,
    MySQLConnectionError,
    MySQLQueryError,
    MySQLConfigError,
)


class TestExceptions:
    """Test suite for custom exceptions."""
    
    def test_base_exception_inheritance(self):
        """Test that all custom exceptions inherit from base."""
        assert issubclass(MySQLConnectionError, MySQLBaseException)
        assert issubclass(MySQLQueryError, MySQLBaseException)
        assert issubclass(MySQLConfigError, MySQLBaseException)
    
    def test_base_exception_is_exception(self):
        """Test that base exception inherits from Exception."""
        assert issubclass(MySQLBaseException, Exception)
    
    def test_connection_error_raise(self):
        """Test raising connection error."""
        with pytest.raises(MySQLConnectionError) as exc_info:
            raise MySQLConnectionError("Connection failed")
        assert str(exc_info.value) == "Connection failed"
    
    def test_query_error_raise(self):
        """Test raising query error."""
        with pytest.raises(MySQLQueryError) as exc_info:
            raise MySQLQueryError("Query execution failed")
        assert str(exc_info.value) == "Query execution failed"
    
    def test_config_error_raise(self):
        """Test raising config error."""
        with pytest.raises(MySQLConfigError) as exc_info:
            raise MySQLConfigError("Invalid configuration")
        assert str(exc_info.value) == "Invalid configuration"
    
    def test_exception_can_be_caught_as_base(self):
        """Test that specific exceptions can be caught as base exception."""
        try:
            raise MySQLConnectionError("Test error")
        except MySQLBaseException as e:
            assert isinstance(e, MySQLConnectionError)
            assert str(e) == "Test error"
