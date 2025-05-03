from app import create_app
from app.extensions import db
import sqlite3
import os
from config import Config
from datetime import datetime

def run_fix():
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
    
    print(f"Running date format fixes on database: {db_path}")
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fix campaign dates by replacing 'T' in ISO format
    print("Fixing campaign start_date and end_date formats...")
    
    # Get all campaigns
    cursor.execute("SELECT id, start_date, end_date FROM campaign")
    campaigns = cursor.fetchall()
    
    updated_count = 0
    for campaign in campaigns:
        campaign_id, start_date, end_date = campaign
        
        if start_date and isinstance(start_date, str) and 'T' in start_date:
            # Replace T with space
            fixed_date = start_date.replace('T', ' ')
            cursor.execute("UPDATE campaign SET start_date = ? WHERE id = ?", (fixed_date, campaign_id))
            updated_count += 1
            
        if end_date and isinstance(end_date, str) and 'T' in end_date:
            # Replace T with space
            fixed_date = end_date.replace('T', ' ')
            cursor.execute("UPDATE campaign SET end_date = ? WHERE id = ?", (fixed_date, campaign_id))
            updated_count += 1
    
    print(f"Updated {updated_count} date fields")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("Date format fixes completed successfully!")

if __name__ == '__main__':
    run_fix() 