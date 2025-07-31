#!/usr/bin/env python3
"""
Add missing top_pages column to daily_click_summary table and populate with data
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime, date, timedelta

# Set the database URL
DATABASE_URL = "postgresql://postgres:vZDarOmyRiNkTEDOGjDkDVOWakMLxymj@yamabiko.proxy.rlwy.net:20282/railway"

def get_db_connection():
    """Create and return PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def add_top_pages_column():
    """Add top_pages column if it doesn't exist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Add top_pages column
        cursor.execute("""
            ALTER TABLE daily_click_summary 
            ADD COLUMN IF NOT EXISTS top_pages JSON
        """)
        
        conn.commit()
        print("✓ Added top_pages column")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error adding column: {e}")
        raise

def update_sample_data_with_pages():
    """Update existing records with top_pages data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Sample page data for each date
        page_updates = [
            {
                'date': date.today() - timedelta(days=1),
                'top_pages': {
                    "Home": 12,
                    "About": 5,
                    "Projects": 6,
                    "Contact": 2
                }
            },
            {
                'date': date.today() - timedelta(days=2),
                'top_pages': {
                    "Home": 8,
                    "Projects": 7,
                    "About": 2,
                    "Contact": 1
                }
            },
            {
                'date': date.today() - timedelta(days=3),
                'top_pages': {
                    "Home": 15,
                    "Projects": 10,
                    "About": 5,
                    "Contact": 2
                }
            }
        ]
        
        # Update each record
        for data in page_updates:
            cursor.execute("""
                UPDATE daily_click_summary 
                SET top_pages = %s 
                WHERE date = %s AND project_name = 'lubobali_portfolio'
            """, (json.dumps(data['top_pages']), data['date']))
            
            print(f"✓ Updated {data['date']} with top pages data")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n🎉 Successfully updated all records with top_pages data!")
        
    except Exception as e:
        print(f"Error updating data: {e}")
        raise

def verify_data():
    """Verify the updated data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT date, project_name, total_clicks, top_pages
            FROM daily_click_summary 
            ORDER BY date DESC
        """)
        
        records = cursor.fetchall()
        
        print("\n📊 Updated daily_click_summary data:")
        for record in records:
            top_pages = record['top_pages'] if record['top_pages'] else {}
            print(f"  {record['date']}: {record['total_clicks']} clicks, pages: {top_pages}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error verifying data: {e}")

if __name__ == "__main__":
    print("🔧 Fixing top_pages data for dashboard...")
    print("=" * 50)
    
    try:
        # Add column if needed
        add_top_pages_column()
        
        # Update with page data
        update_sample_data_with_pages()
        
        # Verify the changes
        verify_data()
        
        print("\n✅ Fix completed! Refresh your dashboard to see the Top Pages chart.")
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
