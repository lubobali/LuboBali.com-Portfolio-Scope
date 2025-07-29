#!/usr/bin/env python3
"""
Quick database check script
"""

import psycopg2
import os

def check_database():
    try:
        # Connect to database
        db_url = "postgresql://postgres:vZDarOmyRiNkTEDOGjDkDVOWakMLxymj@yamabiko.proxy.rlwy.net:20282/railway"
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        print("🔗 Connected to Railway PostgreSQL")
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        print(f"\n📋 Tables in database: {[t[0] for t in tables]}")
        
        # Check click_logs data
        cursor.execute("SELECT COUNT(*) FROM click_logs")
        click_count = cursor.fetchone()[0]
        print(f"📊 Records in click_logs: {click_count}")
        
        if click_count > 0:
            cursor.execute("SELECT * FROM click_logs ORDER BY timestamp DESC LIMIT 3")
            recent_clicks = cursor.fetchall()
            print(f"🕒 Recent clicks: {recent_clicks}")
        
        # Check daily_click_summary data
        try:
            cursor.execute("SELECT COUNT(*) FROM daily_click_summary")
            summary_count = cursor.fetchone()[0]
            print(f"📈 Records in daily_click_summary: {summary_count}")
            
            if summary_count > 0:
                cursor.execute("SELECT * FROM daily_click_summary ORDER BY date DESC LIMIT 3")
                recent_summary = cursor.fetchall()
                print(f"📋 Recent summary: {recent_summary}")
        except Exception as e:
            print(f"❌ daily_click_summary table issue: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_database()
