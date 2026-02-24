"""
Python Data SQL - Example Usage
Demonstrates how to use the DatabaseConnection and Repository classes.
"""

from db_connection import DatabaseConnection
from repository import Repository


def main():
    # Example 1: Using Windows Authentication
    db = DatabaseConnection(
        server="your_server_name",
        database="your_database_name",
        trusted_connection=True
    )
    
    # Example 2: Using SQL Server Authentication
    # db = DatabaseConnection(
    #     server="your_server_name",
    #     database="your_database_name",
    #     username="your_username",
    #     password="your_password"
    # )
    
    # Using the connection with context manager
    with db:
        # Create a repository for a specific table
        users_repo = Repository(db, "Users")
        
        # ==================== CREATE ====================
        # Insert a new record
        new_user = {
            "FirstName": "John",
            "LastName": "Doe",
            "Email": "john.doe@example.com"
        }
        user_id = users_repo.create(new_user)
        print(f"Created user with ID: {user_id}")
        
        # Insert multiple records
        new_users = [
            {"FirstName": "Jane", "LastName": "Smith", "Email": "jane.smith@example.com"},
            {"FirstName": "Bob", "LastName": "Johnson", "Email": "bob.johnson@example.com"}
        ]
        count = users_repo.create_many(new_users)
        print(f"Inserted {count} users")
        
        # ==================== READ ====================
        # Get a single record by ID
        user = users_repo.get_by_id("UserId", 1)
        print(f"User: {user}")
        
        # Get all records
        all_users = users_repo.get_all()
        print(f"All users: {all_users}")
        
        # Get records with conditions
        active_users = users_repo.get_where({"IsActive": True})
        print(f"Active users: {active_users}")
        
        # Execute custom query
        results = users_repo.execute_query(
            "SELECT * FROM Users WHERE Email LIKE ?",
            ["%@example.com"]
        )
        print(f"Custom query results: {results}")
        
        # ==================== UPDATE ====================
        # Update a single record
        rows_updated = users_repo.update("UserId", 1, {"Email": "newemail@example.com"})
        print(f"Updated {rows_updated} row(s)")
        
        # Update records with conditions
        rows_updated = users_repo.update_where(
            conditions={"IsActive": False},
            data={"Status": "Inactive"}
        )
        print(f"Updated {rows_updated} row(s)")
        
        # ==================== DELETE ====================
        # Delete a single record
        rows_deleted = users_repo.delete("UserId", 1)
        print(f"Deleted {rows_deleted} row(s)")
        
        # Delete records with conditions
        rows_deleted = users_repo.delete_where({"Status": "Inactive"})
        print(f"Deleted {rows_deleted} row(s)")
        
        # ==================== SCHEMA ACCESS ====================
        # Get table schema
        schema = users_repo.get_table_schema()
        print(f"Table schema: {schema}")
        
        # Get primary keys
        primary_keys = users_repo.get_primary_keys()
        print(f"Primary keys: {primary_keys}")
        
        # Get foreign keys
        foreign_keys = users_repo.get_foreign_keys()
        print(f"Foreign keys: {foreign_keys}")
        
        # Get indexes
        indexes = users_repo.get_indexes()
        print(f"Indexes: {indexes}")
        
        # Get all tables in database
        tables = users_repo.get_all_tables()
        print(f"All tables: {tables}")
        
        # Get complete database schema
        db_schema = users_repo.get_database_schema()
        print(f"Database schema: {db_schema}")
        
        # Check if table exists
        exists = users_repo.table_exists("Users")
        print(f"Table exists: {exists}")
        
        # Get row count
        count = users_repo.get_row_count()
        print(f"Row count: {count}")


if __name__ == "__main__":
    main()

