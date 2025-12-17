"""Custom exceptions for MySQL operations."""


class MySQLBaseException(Exception):
    """Base exception for all MySQL-related errors."""
    pass


class MySQLConnectionError(MySQLBaseException):
    """Raised when there's an error establishing or maintaining a connection."""
    pass


class MySQLQueryError(MySQLBaseException):
    """Raised when a query execution fails."""
    pass


class MySQLConfigError(MySQLBaseException):
    """Raised when there's an error in configuration."""
    pass
