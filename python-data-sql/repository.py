"""
Repository Module
Provides a base repository class implementing the repository pattern with CRUD operations
and schema access functionality.
"""

from typing import Any, Dict, List, Optional, Tuple
from db_connection import DatabaseConnection


class Repository:
    """
    A repository class implementing CRUD operations and schema access.
    Uses the repository pattern to abstract database operations.
    """
    
    def __init__(self, db_connection: DatabaseConnection, table_name: str):
        """
        Initialize the repository with a database connection and table name.
        
        Args:
            db_connection: An instance of DatabaseConnection
            table_name: The name of the table this repository operates on
        """
        self.db_connection = db_connection
        self.table_name = table_name
    
    # ==================== CREATE ====================
    
    def create(self, data: Dict[str, Any]) -> int:
        """
        Insert a new record into the table.
        
        Args:
            data: Dictionary of column names and values to insert
            
        Returns:
            int: The ID of the newly inserted record (if identity column exists)
            
        Raises:
            Exception: If the insert operation fails
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        values = list(data.values())
        
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query, values)
            cursor.execute("SELECT SCOPE_IDENTITY()")
            result = cursor.fetchone()
            cursor.commit()
            return result[0] if result and result[0] else 0
    
    def create_many(self, records: List[Dict[str, Any]]) -> int:
        """
        Insert multiple records into the table.
        
        Args:
            records: List of dictionaries containing column names and values
            
        Returns:
            int: Number of records inserted
        """
        if not records:
            return 0
            
        columns = ", ".join(records[0].keys())
        placeholders = ", ".join(["?" for _ in records[0]])
        
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        with self.db_connection.get_cursor() as cursor:
            for record in records:
                cursor.execute(query, list(record.values()))
            cursor.commit()
            return len(records)
    
    # ==================== READ ====================
    
    def get_by_id(self, id_column: str, id_value: Any) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single record by its ID.
        
        Args:
            id_column: The name of the ID column
            id_value: The value of the ID to search for
            
        Returns:
            Optional[Dict]: The record as a dictionary, or None if not found
        """
        query = f"SELECT * FROM {self.table_name} WHERE {id_column} = ?"
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query, [id_value])
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def get_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all records from the table.
        
        Args:
            limit: Optional maximum number of records to return
            
        Returns:
            List[Dict]: List of records as dictionaries
        """
        if limit:
            query = f"SELECT TOP {limit} * FROM {self.table_name}"
        else:
            query = f"SELECT * FROM {self.table_name}"
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_where(
        self,
        conditions: Dict[str, Any],
        operator: str = "AND"
    ) -> List[Dict[str, Any]]:
        """
        Retrieve records matching specified conditions.
        
        Args:
            conditions: Dictionary of column names and values to filter by
            operator: Logical operator to combine conditions ("AND" or "OR")
            
        Returns:
            List[Dict]: List of matching records as dictionaries
        """
        where_clauses = [f"{col} = ?" for col in conditions.keys()]
        where_string = f" {operator} ".join(where_clauses)
        values = list(conditions.values())
        
        query = f"SELECT * FROM {self.table_name} WHERE {where_string}"
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query, values)
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def execute_query(
        self,
        query: str,
        params: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a custom SELECT query.
        
        Args:
            query: The SQL query to execute
            params: Optional list of parameters for the query
            
        Returns:
            List[Dict]: Query results as a list of dictionaries
        """
        with self.db_connection.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            return []
    
    # ==================== UPDATE ====================
    
    def update(
        self,
        id_column: str,
        id_value: Any,
        data: Dict[str, Any]
    ) -> int:
        """
        Update a record by its ID.
        
        Args:
            id_column: The name of the ID column
            id_value: The value of the ID to update
            data: Dictionary of column names and new values
            
        Returns:
            int: Number of rows affected
        """
        set_clauses = ", ".join([f"{col} = ?" for col in data.keys()])
        values = list(data.values()) + [id_value]
        
        query = f"UPDATE {self.table_name} SET {set_clauses} WHERE {id_column} = ?"
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query, values)
            rows_affected = cursor.rowcount
            cursor.commit()
            return rows_affected
    
    def update_where(
        self,
        conditions: Dict[str, Any],
        data: Dict[str, Any],
        operator: str = "AND"
    ) -> int:
        """
        Update records matching specified conditions.
        
        Args:
            conditions: Dictionary of column names and values to filter by
            data: Dictionary of column names and new values
            operator: Logical operator to combine conditions
            
        Returns:
            int: Number of rows affected
        """
        set_clauses = ", ".join([f"{col} = ?" for col in data.keys()])
        where_clauses = [f"{col} = ?" for col in conditions.keys()]
        where_string = f" {operator} ".join(where_clauses)
        
        values = list(data.values()) + list(conditions.values())
        query = f"UPDATE {self.table_name} SET {set_clauses} WHERE {where_string}"
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query, values)
            rows_affected = cursor.rowcount
            cursor.commit()
            return rows_affected
    
    # ==================== DELETE ====================
    
    def delete(self, id_column: str, id_value: Any) -> int:
        """
        Delete a record by its ID.
        
        Args:
            id_column: The name of the ID column
            id_value: The value of the ID to delete
            
        Returns:
            int: Number of rows affected
        """
        query = f"DELETE FROM {self.table_name} WHERE {id_column} = ?"
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query, [id_value])
            rows_affected = cursor.rowcount
            cursor.commit()
            return rows_affected
    
    def delete_where(
        self,
        conditions: Dict[str, Any],
        operator: str = "AND"
    ) -> int:
        """
        Delete records matching specified conditions.
        
        Args:
            conditions: Dictionary of column names and values to filter by
            operator: Logical operator to combine conditions
            
        Returns:
            int: Number of rows affected
        """
        where_clauses = [f"{col} = ?" for col in conditions.keys()]
        where_string = f" {operator} ".join(where_clauses)
        values = list(conditions.values())
        
        query = f"DELETE FROM {self.table_name} WHERE {where_string}"
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query, values)
            rows_affected = cursor.rowcount
            cursor.commit()
            return rows_affected
    
    def delete_all(self) -> int:
        """
        Delete all records from the table.
        USE WITH CAUTION!
        
        Returns:
            int: Number of rows affected
        """
        query = f"DELETE FROM {self.table_name}"
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query)
            rows_affected = cursor.rowcount
            cursor.commit()
            return rows_affected
    
    # ==================== SCHEMA ACCESS ====================
    
    def get_table_schema(self) -> List[Dict[str, Any]]:
        """
        Get the schema information for the current table.
        
        Returns:
            List[Dict]: List of column information including name, type, nullable, etc.
        """
        query = """
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                ORDINAL_POSITION
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query, [self.table_name])
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_primary_keys(self) -> List[str]:
        """
        Get the primary key columns for the current table.
        
        Returns:
            List[str]: List of primary key column names
        """
        query = """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_NAME = ?
            AND CONSTRAINT_NAME LIKE 'PK_%'
        """
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query, [self.table_name])
            return [row[0] for row in cursor.fetchall()]
    
    def get_foreign_keys(self) -> List[Dict[str, Any]]:
        """
        Get foreign key relationships for the current table.
        
        Returns:
            List[Dict]: List of foreign key information
        """
        query = """
            SELECT 
                fk.name AS FK_NAME,
                tp.name AS PARENT_TABLE,
                cp.name AS PARENT_COLUMN,
                tr.name AS REFERENCED_TABLE,
                cr.name AS REFERENCED_COLUMN
            FROM sys.foreign_keys fk
            INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
            INNER JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id
            INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
            INNER JOIN sys.columns cp ON fkc.parent_column_id = cp.column_id 
                AND fkc.parent_object_id = cp.object_id
            INNER JOIN sys.columns cr ON fkc.referenced_column_id = cr.column_id 
                AND fkc.referenced_object_id = cr.object_id
            WHERE tp.name = ?
        """
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query, [self.table_name])
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_indexes(self) -> List[Dict[str, Any]]:
        """
        Get index information for the current table.
        
        Returns:
            List[Dict]: List of index information
        """
        query = """
            SELECT 
                i.name AS INDEX_NAME,
                i.type_desc AS INDEX_TYPE,
                i.is_unique AS IS_UNIQUE,
                i.is_primary_key AS IS_PRIMARY_KEY,
                STRING_AGG(c.name, ', ') AS COLUMNS
            FROM sys.indexes i
            INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id 
                AND i.index_id = ic.index_id
            INNER JOIN sys.columns c ON ic.object_id = c.object_id 
                AND ic.column_id = c.column_id
            WHERE OBJECT_NAME(i.object_id) = ?
            GROUP BY i.name, i.type_desc, i.is_unique, i.is_primary_key
        """
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query, [self.table_name])
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_all_tables(self) -> List[str]:
        """
        Get all table names in the database.
        
        Returns:
            List[str]: List of table names
        """
        query = """
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]
    
    def get_database_schema(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get the complete schema for all tables in the database.
        
        Returns:
            Dict: Dictionary mapping table names to their column information
        """
        tables = self.get_all_tables()
        schema = {}
        
        query = """
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """
        
        with self.db_connection.get_cursor() as cursor:
            for table in tables:
                cursor.execute(query, [table])
                columns = [column[0] for column in cursor.description]
                schema[table] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return schema
    
    def table_exists(self, table_name: Optional[str] = None) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: The table name to check (defaults to current table)
            
        Returns:
            bool: True if table exists, False otherwise
        """
        check_table = table_name or self.table_name
        query = """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = ?
        """
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query, [check_table])
            result = cursor.fetchone()
            return result[0] > 0 if result else False
    
    def get_row_count(self) -> int:
        """
        Get the total number of rows in the table.
        
        Returns:
            int: Number of rows
        """
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        
        with self.db_connection.get_cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result else 0
