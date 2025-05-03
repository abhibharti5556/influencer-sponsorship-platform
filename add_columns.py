from app import create_app
from app.extensions import db
import sqlite3
import os
from config import Config
from datetime import datetime

def run_migrations():
    app = create_app(Config)
    
    # Get the database path
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri[10:]
    else:
        raise ValueError(f"Unsupported database URI: {db_uri}")
    
    # Make path absolute if it's relative
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)
    
    print(f"Running migrations on database: {db_path}")
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if user.is_flagged column exists
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'is_flagged' not in column_names:
        print("Adding is_flagged column to user table...")
        cursor.execute("ALTER TABLE user ADD COLUMN is_flagged BOOLEAN DEFAULT 0")
    else:
        print("Column is_flagged already exists in user table")
        
    if 'is_active' not in column_names:
        print("Adding is_active column to user table...")
        cursor.execute("ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT 1")
    else:
        print("Column is_active already exists in user table")
    
    # Check if campaign.is_flagged column exists
    cursor.execute("PRAGMA table_info(campaign)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'is_flagged' not in column_names:
        print("Adding is_flagged column to campaign table...")
        cursor.execute("ALTER TABLE campaign ADD COLUMN is_flagged BOOLEAN DEFAULT 0")
    else:
        print("Column is_flagged already exists in campaign table")
        
    if 'created_at' not in column_names:
        print("Adding created_at column to campaign table...")
        cursor.execute("ALTER TABLE campaign ADD COLUMN created_at TIMESTAMP")
        
        # Set default values for created_at on existing records
        print("Setting default created_at values for existing campaigns...")
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(f"UPDATE campaign SET created_at = '{now}' WHERE created_at IS NULL")
    else:
        print("Column created_at already exists in campaign table")
    
    # Check if ad_request.created_at column exists
    cursor.execute("PRAGMA table_info(ad_request)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'created_at' not in column_names:
        print("Adding created_at column to ad_request table...")
        cursor.execute("ALTER TABLE ad_request ADD COLUMN created_at TIMESTAMP")
        
        # Set default values for created_at on existing records
        print("Setting default created_at values for existing ad requests...")
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(f"UPDATE ad_request SET created_at = '{now}' WHERE created_at IS NULL")
    else:
        print("Column created_at already exists in ad_request table")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("Migrations completed successfully!")

if __name__ == '__main__':
    run_migrations() 