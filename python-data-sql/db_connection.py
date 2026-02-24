"""
Database Connection Module
Provides a class for establishing and managing database connections using the repository pattern.
"""

import pyodbc
from typing import Optional
from contextlib import contextmanager


class DatabaseConnection:
    """
    A class to manage database connections using the repository pattern.
    Supports SQL Server connections via pyodbc.
    """
    
    def __init__(
        self,
        server: str,
        database: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        driver: str = "{ODBC Driver 17 for SQL Server}",
        trusted_connection: bool = False
    ):
        """
        Initialize the database connection parameters.
        
        Args:
            server: The database server address
            database: The name of the database
            username: Username for SQL authentication (optional if using Windows auth)
            password: Password for SQL authentication (optional if using Windows auth)
            driver: ODBC driver to use
            trusted_connection: If True, use Windows authentication
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver
        self.trusted_connection = trusted_connection
        self._connection: Optional[pyodbc.Connection] = None
    
    def _build_connection_string(self) -> str:
        """Build the connection string based on authentication type."""
        if self.trusted_connection:
            return (
                f"DRIVER={self.driver};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Trusted_Connection=yes;"
            )
        else:
            return (
                f"DRIVER={self.driver};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
            )
    
    def connect(self) -> pyodbc.Connection:
        """
        Establish a connection to the database.
        
        Returns:
            pyodbc.Connection: The database connection object
            
        Raises:
            pyodbc.Error: If connection fails
        """
        if self._connection is None or self._connection.closed:
            connection_string = self._build_connection_string()
            self._connection = pyodbc.connect(connection_string)
        return self._connection
    
    def disconnect(self) -> None:
        """Close the database connection if it exists."""
        if self._connection is not None and not self._connection.closed:
            self._connection.close()
            self._connection = None
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        Automatically handles connection cleanup.
        
        Yields:
            pyodbc.Connection: The database connection
        """
        connection = self.connect()
        try:
            yield connection
        finally:
            pass  # Keep connection open for reuse; call disconnect() explicitly when done
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager for database cursors.
        Automatically handles cursor cleanup.
        
        Yields:
            pyodbc.Cursor: A database cursor
        """
        connection = self.connect()
        cursor = connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    
    def is_connected(self) -> bool:
        """Check if there is an active database connection."""
        return self._connection is not None and not self._connection.closed
    
    def __enter__(self):
        """Support for with statement."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup when exiting with statement."""
        self.disconnect()
        return False
