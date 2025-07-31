#!/usr/bin/env python3
"""
Add Sample Data - For Dashboard Testing Only
Adds a few sample records to show dashboard functionality
"""

import os
import psycopg2
from datetime import datetime, date, timedelta
import json

def add_sample_data():
    """Add sample data to demonstrate dashboard functionality"""
    
    # Database connection
    db_url = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL") or os.getenv("DB_URL")
    if not db_url:
        db_url = "postgresql://postgres:vZDarOmyRiNkTEDOGjDkDVOWakMLxymj@yamabiko.proxy.rlwy.net:20282/railway"
    
    try:
        with psycopg2.connect(db_url) as conn:
            with conn.cursor() as cursor:
                
                print("📊 Adding sample data for dashboard demo...")
                
                # Add sample click logs
                sample_clicks = [
                    ('home', 'general', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', 'https://linkedin.com', 'sess_demo_1', 45),
                    ('home', 'general', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'direct', 'sess_demo_2', 78),
                    ('/resume', 'general', 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)', 'https://google.com', 'sess_demo_3', 120),
                    ('/cvs-pipeline', 'data-engineering', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', 'https://linkedin.com', 'sess_demo_4', 180),
                    ('/about-me', 'general', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'direct', 'sess_demo_5', 95)
                ]
                
                for page, tag, agent, ref, session, time_spent in sample_clicks:
                    cursor.execute("""
                        INSERT INTO click_logs (page_name, tag, user_agent, referrer, session_id, time_on_page, timestamp)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (page, tag, agent, ref, session, time_spent, datetime.now()))
                
                # Add sample daily summary
                today = date.today()
                cursor.execute("""
                    INSERT INTO daily_click_summary 
                    (date, project_name, total_clicks, avg_time_on_page, device_split, top_referrers, repeat_visits, tag)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    today,
                    'Portfolio Demo',
                    5,
                    103.6,
                    json.dumps({"desktop": 3, "mobile": 2}),
                    json.dumps({"linkedin.com": 2, "direct": 2, "google.com": 1}),
                    0,
                    'general'
                ))
                
                conn.commit()
                
                print("✅ Sample data added successfully!")
                print("🎯 Your dashboard should now show sample analytics")
                print("🔄 Refresh your Streamlit dashboard to see the data")
                print()
                print("📝 Note: This is just demo data. Real visitor data will")
                print("    be processed automatically at midnight UTC daily.")
                
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        return False
    
    return True

if __name__ == "__main__":
    add_sample_data()
