#!/usr/bin/env python3
"""
Check daily_click_summary table structure
"""

import psycopg2

def check_table_structure():
    try:
        db_url = "postgresql://postgres:vZDarOmyRiNkTEDOGjDkDVOWakMLxymj@yamabiko.proxy.rlwy.net:20282/railway"
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Get column names
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'daily_click_summary'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print("📋 daily_click_summary columns:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
        
        # Get the actual data
        cursor.execute("SELECT * FROM daily_click_summary")
        data = cursor.fetchall()
        print(f"\n📊 Sample data: {data}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_table_structure()
