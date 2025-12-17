"""MySQL connection management with pooling and error handling."""

import logging
from typing import Optional, Dict, Any
import mysql.connector
from mysql.connector import Error as MySQLError
from mysql.connector.pooling import MySQLConnectionPool

from .config import Config
from .exceptions import MySQLConnectionError

logger = logging.getLogger(__name__)


class MySQLConnection:
    """
    Enterprise-grade MySQL connection manager.
    
    Features:
    - Connection pooling
    - Automatic reconnection
    - Comprehensive error handling
    - Context manager support
    
    Example:
        >>> config = Config.from_dict({
        ...     'host': 'localhost',
        ...     'user': 'root',
        ...     'password': 'password',
        ...     'database': 'testdb'
        ... })
        >>> with MySQLConnection(config) as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT 1")
    """
    
    def __init__(self, config: Config, pool_name: str = "mypool", 
                 pool_size: int = 5):
        """
        Initialize MySQL connection manager.
        
        Args:
            config: Configuration object
            pool_name: Name for the connection pool
            pool_size: Size of the connection pool
            
        Raises:
            MySQLConnectionError: If connection cannot be established
        """
        self.config = config
        self.pool_name = pool_name
        self.pool_size = pool_size
        self._connection = None
        self._pool = None
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _create_pool(self) -> MySQLConnectionPool:
        """
        Create connection pool.
        
        Returns:
            MySQLConnectionPool instance
            
        Raises:
            MySQLConnectionError: If pool creation fails
        """
        try:
            pool_config = {
                'pool_name': self.pool_name,
                'pool_size': self.pool_size,
                'host': self.config.get('host'),
                'user': self.config.get('user'),
                'password': self.config.get('password'),
                'database': self.config.get('database'),
            }
            
            # Add optional parameters
            if self.config.get('port'):
                pool_config['port'] = self.config.get('port')
            if self.config.get('charset'):
                pool_config['charset'] = self.config.get('charset')
            
            logger.info(f"Creating connection pool '{self.pool_name}'")
            return MySQLConnectionPool(**pool_config)
        except MySQLError as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise MySQLConnectionError(f"Failed to create connection pool: {e}")
    
    def connect(self) -> None:
        """
        Establish database connection.
        
        Raises:
            MySQLConnectionError: If connection fails
        """
        try:
            if self._pool is None:
                self._pool = self._create_pool()
            
            self._connection = self._pool.get_connection()
            logger.info("Successfully connected to MySQL database")
        except MySQLError as e:
            logger.error(f"Connection failed: {e}")
            raise MySQLConnectionError(f"Failed to connect to database: {e}")
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            logger.info("Disconnected from MySQL database")
            self._connection = None
    
    def is_connected(self) -> bool:
        """
        Check if connection is active.
        
        Returns:
            True if connected, False otherwise
        """
        return (self._connection is not None and 
                self._connection.is_connected())
    
    def reconnect(self) -> None:
        """
        Reconnect to database.
        
        Raises:
            MySQLConnectionError: If reconnection fails
        """
        logger.info("Attempting to reconnect to database")
        self.disconnect()
        self.connect()
    
    def get_connection(self):
        """
        Get the active connection object.
        
        Returns:
            MySQL connection object
            
        Raises:
            MySQLConnectionError: If not connected
        """
        if not self.is_connected():
            raise MySQLConnectionError("Not connected to database")
        return self._connection
    
    def cursor(self, **kwargs):
        """
        Create a cursor from the connection.
        
        Args:
            **kwargs: Arguments to pass to cursor creation
            
        Returns:
            MySQL cursor object
            
        Raises:
            MySQLConnectionError: If not connected
        """
        if not self.is_connected():
            self.connect()
        return self._connection.cursor(**kwargs)
    
    def commit(self) -> None:
        """Commit current transaction."""
        if self.is_connected():
            self._connection.commit()
    
    def rollback(self) -> None:
        """Rollback current transaction."""
        if self.is_connected():
            self._connection.rollback()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.disconnect()
        return False
