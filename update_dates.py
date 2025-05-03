from app import create_app
from app.extensions import db
import sqlite3
import os
from config import Config
from datetime import datetime

def run_update():
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
    
    print(f"Running updates on database: {db_path}")
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fix campaign dates
    print("Updating campaign created_at values to ISO format...")
    now = datetime.utcnow().isoformat()
    cursor.execute("UPDATE campaign SET created_at = ? WHERE created_at IS NULL OR created_at = ''", (now,))
    
    # Fix start_date and end_date
    print("Updating campaign start_date and end_date to ISO format...")
    cursor.execute("SELECT id, start_date, end_date FROM campaign")
    campaigns = cursor.fetchall()
    
    for campaign in campaigns:
        campaign_id, start_date, end_date = campaign
        if start_date and not isinstance(start_date, datetime):
            try:
                # Try to parse the existing date, or use current date if can't parse
                try:
                    # If it's a string that looks like a date, try to parse it 
                    if isinstance(start_date, str) and len(start_date) > 10:
                        parsed_date = datetime.fromisoformat(start_date.split(".")[0])
                        iso_date = parsed_date.isoformat()
                    else:
                        iso_date = datetime.utcnow().isoformat()
                except (ValueError, TypeError):
                    iso_date = datetime.utcnow().isoformat()
                    
                cursor.execute("UPDATE campaign SET start_date = ? WHERE id = ?", (iso_date, campaign_id))
            except Exception as e:
                print(f"Error updating start_date for campaign {campaign_id}: {e}")
                print(f"start_date value: {start_date}, type: {type(start_date)}")
        
        if end_date and not isinstance(end_date, datetime):
            try:
                # Try to parse the existing date, or use current date if can't parse
                try:
                    # If it's a string that looks like a date, try to parse it
                    if isinstance(end_date, str) and len(end_date) > 10:
                        parsed_date = datetime.fromisoformat(end_date.split(".")[0])
                        iso_date = parsed_date.isoformat()
                    else:
                        iso_date = datetime.utcnow().isoformat()
                except (ValueError, TypeError):
                    iso_date = datetime.utcnow().isoformat()
                    
                cursor.execute("UPDATE campaign SET end_date = ? WHERE id = ?", (iso_date, campaign_id))
            except Exception as e:
                print(f"Error updating end_date for campaign {campaign_id}: {e}")
                print(f"end_date value: {end_date}, type: {type(end_date)}")
    
    # Fix ad_request dates
    print("Updating ad_request created_at values to ISO format...")
    now = datetime.utcnow().isoformat()
    cursor.execute("UPDATE ad_request SET created_at = ? WHERE created_at IS NULL OR created_at = ''", (now,))
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("Date updates completed successfully!")

if __name__ == '__main__':
    run_update() 