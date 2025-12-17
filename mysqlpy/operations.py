"""High-level MySQL operations interface."""

import logging
from typing import List, Dict, Any, Optional, Tuple
from mysql.connector import Error as MySQLError

from .connection import MySQLConnection
from .exceptions import MySQLQueryError

logger = logging.getLogger(__name__)


class MySQLOperations:
    """
    High-level interface for MySQL CRUD operations.
    
    Provides enterprise-grade methods for:
    - Executing queries
    - Fetching results
    - Batch operations
    - Transaction management
    
    Example:
        >>> from mysqlpy import Config, MySQLConnection, MySQLOperations
        >>> config = Config.from_dict({...})
        >>> conn = MySQLConnection(config)
        >>> ops = MySQLOperations(conn)
        >>> results = ops.fetch_all("SELECT * FROM users WHERE age > %s", (18,))
    """
    
    def __init__(self, connection: MySQLConnection):
        """
        Initialize operations manager.
        
        Args:
            connection: MySQLConnection instance
        """
        self.connection = connection
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Execute a query (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL query string
            params: Query parameters (for parameterized queries)
            
        Returns:
            Number of affected rows
            
        Raises:
            MySQLQueryError: If query execution fails
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            affected_rows = cursor.rowcount
            self.connection.commit()
            cursor.close()
            logger.info(f"Query executed successfully, {affected_rows} rows affected")
            return affected_rows
        except MySQLError as e:
            self.connection.rollback()
            logger.error(f"Query execution failed: {e}")
            raise MySQLQueryError(f"Failed to execute query: {e}")
    
    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Tuple]:
        """
        Fetch a single row from query result.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Single row as tuple, or None if no results
            
        Raises:
            MySQLQueryError: If query execution fails
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            logger.debug(f"Fetched one row from query")
            return result
        except MySQLError as e:
            logger.error(f"Fetch one failed: {e}")
            raise MySQLQueryError(f"Failed to fetch data: {e}")
    
    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        """
        Fetch all rows from query result.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of rows as tuples
            
        Raises:
            MySQLQueryError: If query execution fails
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            logger.debug(f"Fetched {len(results)} rows from query")
            return results
        except MySQLError as e:
            logger.error(f"Fetch all failed: {e}")
            raise MySQLQueryError(f"Failed to fetch data: {e}")
    
    def fetch_dict(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Fetch all rows as dictionaries with column names as keys.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of rows as dictionaries
            
        Raises:
            MySQLQueryError: If query execution fails
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            logger.debug(f"Fetched {len(results)} rows as dictionaries")
            return results
        except MySQLError as e:
            logger.error(f"Fetch dict failed: {e}")
            raise MySQLQueryError(f"Failed to fetch data: {e}")
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        Execute the same query multiple times with different parameters.
        
        Useful for batch INSERT/UPDATE operations.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Total number of affected rows
            
        Raises:
            MySQLQueryError: If query execution fails
        """
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            affected_rows = cursor.rowcount
            self.connection.commit()
            cursor.close()
            logger.info(f"Batch query executed, {affected_rows} rows affected")
            return affected_rows
        except MySQLError as e:
            self.connection.rollback()
            logger.error(f"Batch query failed: {e}")
            raise MySQLQueryError(f"Failed to execute batch query: {e}")
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """
        Insert a single row into a table.
        
        Args:
            table: Table name
            data: Dictionary of column names and values
            
        Returns:
            ID of inserted row (if applicable)
            
        Raises:
            MySQLQueryError: If insertion fails
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(data.values()))
            last_id = cursor.lastrowid
            self.connection.commit()
            cursor.close()
            logger.info(f"Inserted row into {table}, ID: {last_id}")
            return last_id
        except MySQLError as e:
            self.connection.rollback()
            logger.error(f"Insert failed: {e}")
            raise MySQLQueryError(f"Failed to insert data: {e}")
    
    def update(self, table: str, data: Dict[str, Any], 
               where_clause: str, where_params: Tuple) -> int:
        """
        Update rows in a table.
        
        Args:
            table: Table name
            data: Dictionary of column names and new values
            where_clause: WHERE clause (without 'WHERE' keyword)
            where_params: Parameters for WHERE clause
            
        Returns:
            Number of affected rows
            
        Raises:
            MySQLQueryError: If update fails
        """
        set_clause = ', '.join([f"{col} = %s" for col in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        params = tuple(data.values()) + where_params
        
        return self.execute_query(query, params)
    
    def delete(self, table: str, where_clause: str, where_params: Tuple) -> int:
        """
        Delete rows from a table.
        
        Args:
            table: Table name
            where_clause: WHERE clause (without 'WHERE' keyword)
            where_params: Parameters for WHERE clause
            
        Returns:
            Number of affected rows
            
        Raises:
            MySQLQueryError: If deletion fails
        """
        query = f"DELETE FROM {table} WHERE {where_clause}"
        return self.execute_query(query, where_params)
    
    def table_exists(self, table: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table: Table name
            
        Returns:
            True if table exists, False otherwise
        """
        query = """
            SELECT COUNT(*)
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            AND table_name = %s
        """
        result = self.fetch_one(query, (table,))
        return result[0] > 0 if result else False
