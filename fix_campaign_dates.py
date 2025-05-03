import sqlite3
import os
from datetime import datetime
import sys

def fix_campaign_dates():
    # Path to the database
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.sqlite3')
    print(f"Fixing date formats in database: {db_path}")
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Fix date column types first - create temp table with correct schema
        print("Creating temporary campaign table with proper date schema...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaign_temp (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            budget REAL NOT NULL,
            niche TEXT NOT NULL,
            visibility TEXT DEFAULT 'public',
            created_at TEXT,
            sponsor_id INTEGER NOT NULL,
            is_flagged BOOLEAN DEFAULT 0,
            FOREIGN KEY(sponsor_id) REFERENCES user(id)
        )
        """)
        
        # 2. Copy data from campaign to campaign_temp, converting dates
        print("Copying data with fixed date formats...")
        cursor.execute("SELECT * FROM campaign")
        campaigns = cursor.fetchall()
        
        # Get column names
        cursor.execute("PRAGMA table_info(campaign)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        for campaign in campaigns:
            # Create a dictionary mapping column names to values
            campaign_dict = {column_names[i]: campaign[i] for i in range(len(column_names))}
            
            # Handle start_date
            if campaign_dict.get('start_date'):
                try:
                    # Clean date format and ensure it's YYYY-MM-DD only
                    if 'T' in str(campaign_dict['start_date']):
                        date_str = str(campaign_dict['start_date']).split('T')[0]
                    elif ' ' in str(campaign_dict['start_date']):
                        date_str = str(campaign_dict['start_date']).split(' ')[0]
                    else:
                        date_str = str(campaign_dict['start_date'])
                    
                    # Ensure it's a valid date
                    try:
                        datetime.strptime(date_str, '%Y-%m-%d')
                        campaign_dict['start_date'] = date_str
                    except ValueError:
                        campaign_dict['start_date'] = '2024-01-01'  # Default fallback date
                except Exception as e:
                    print(f"Error processing start_date for campaign {campaign_dict['id']}: {e}")
                    campaign_dict['start_date'] = '2024-01-01'  # Default fallback date
            
            # Handle end_date
            if campaign_dict.get('end_date'):
                try:
                    # Clean date format and ensure it's YYYY-MM-DD only
                    if 'T' in str(campaign_dict['end_date']):
                        date_str = str(campaign_dict['end_date']).split('T')[0]
                    elif ' ' in str(campaign_dict['end_date']):
                        date_str = str(campaign_dict['end_date']).split(' ')[0]
                    else:
                        date_str = str(campaign_dict['end_date'])
                    
                    # Ensure it's a valid date
                    try:
                        datetime.strptime(date_str, '%Y-%m-%d')
                        campaign_dict['end_date'] = date_str
                    except ValueError:
                        campaign_dict['end_date'] = '2024-12-31'  # Default fallback date
                except Exception as e:
                    print(f"Error processing end_date for campaign {campaign_dict['id']}: {e}")
                    campaign_dict['end_date'] = '2024-12-31'  # Default fallback date
            
            # Handle created_at
            if campaign_dict.get('created_at'):
                try:
                    # Ensure it's in ISO format
                    dt = datetime.now().isoformat() if not campaign_dict['created_at'] else campaign_dict['created_at']
                    if isinstance(dt, str):
                        # Clean up the string
                        if 'T' in dt:
                            dt = dt.replace('T', ' ')
                        campaign_dict['created_at'] = dt
                except Exception as e:
                    print(f"Error processing created_at for campaign {campaign_dict['id']}: {e}")
                    campaign_dict['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Insert into temp table
            placeholders = ', '.join(['?'] * len(campaign_dict))
            columns_str = ', '.join(campaign_dict.keys())
            sql = f"INSERT INTO campaign_temp ({columns_str}) VALUES ({placeholders})"
            
            cursor.execute(sql, list(campaign_dict.values()))
        
        # 3. Drop original table and rename temp table
        print("Replacing campaign table with fixed version...")
        cursor.execute("DROP TABLE campaign")
        cursor.execute("ALTER TABLE campaign_temp RENAME TO campaign")
        
        # Commit changes
        conn.commit()
        print("Successfully fixed campaign date formats!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    fix_campaign_dates() 