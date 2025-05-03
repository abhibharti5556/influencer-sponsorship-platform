import os
import sqlite3
from app import create_app

def update_database_schema():
    """Update the database schema by adding missing columns to the campaign table."""
    app = create_app()
    
    # Get database path from app config
    db_path = os.path.join(app.root_path, '..', app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
    
    print(f"Updating database at: {db_path}")
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the title column exists
    cursor.execute("PRAGMA table_info(campaign)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Add missing columns
    columns_to_add = []
    
    if 'title' not in columns:
        columns_to_add.append(("title", "VARCHAR(100)"))
        
    if 'duration' not in columns:
        columns_to_add.append(("duration", "INTEGER"))
        
    if 'platform' not in columns:
        columns_to_add.append(("platform", "VARCHAR(50)"))
        
    if 'requirements' not in columns:
        columns_to_add.append(("requirements", "TEXT"))
        
    if 'status' not in columns:
        columns_to_add.append(("status", "VARCHAR(20)"))
    
    # Add the columns
    for column_name, column_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE campaign ADD COLUMN {column_name} {column_type}")
            print(f"Added column '{column_name}' to campaign table")
        except sqlite3.OperationalError as e:
            print(f"Error adding column '{column_name}': {e}")
    
    # For title column, populate it with name if it's null
    if "title" in [col[0] for col in columns_to_add]:
        cursor.execute("UPDATE campaign SET title = name WHERE title IS NULL")
        print("Updated title column using name values")
        
    # For platform column, set default to 'instagram'
    if "platform" in [col[0] for col in columns_to_add]:
        cursor.execute("UPDATE campaign SET platform = 'instagram' WHERE platform IS NULL")
        print("Set default platform to 'instagram'")
        
    # For status column, set based on dates
    if "status" in [col[0] for col in columns_to_add]:
        # Set default status to 'active'
        cursor.execute("UPDATE campaign SET status = 'active' WHERE status IS NULL")
        print("Set default status to 'active'")
        
        # Update statuses based on dates
        cursor.execute("UPDATE campaign SET status = 'pending' WHERE date(start_date) > date('now')")
        cursor.execute("UPDATE campaign SET status = 'inactive' WHERE date(end_date) < date('now')")
        print("Updated campaign statuses based on dates")
        
    # For duration column, calculate based on start and end dates
    if "duration" in [col[0] for col in columns_to_add]:
        cursor.execute("UPDATE campaign SET duration = (julianday(end_date) - julianday(start_date)) + 1")
        print("Calculated duration based on start and end dates")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database schema update completed")

if __name__ == "__main__":
    update_database_schema() 