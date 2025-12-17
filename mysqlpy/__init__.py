"""
linux.py.mysql - Enterprise-grade MySQL connection and operations library.

This package provides robust MySQL database connectivity with comprehensive
error handling, connection pooling, and enterprise-level features.
"""

from .connection import MySQLConnection
from .operations import MySQLOperations
from .config import Config
from .exceptions import (
    MySQLConnectionError,
    MySQLQueryError,
    MySQLConfigError,
)

__version__ = "1.0.0"
__all__ = [
    "MySQLConnection",
    "MySQLOperations",
    "Config",
    "MySQLConnectionError",
    "MySQLQueryError",
    "MySQLConfigError",
]
