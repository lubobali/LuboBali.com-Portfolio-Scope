#!/usr/bin/env python3
"""
Insert sample data into daily_click_summary for testing dashboard
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, timedelta

def insert_sample_daily_data():
    """Insert sample aggregated data for the last week"""
    
    # Use the public Railway URL - you'll need to provide this
    database_url = input("Paste your PUBLIC DATABASE_URL from Railway (with railway.app): ").strip()
    
    if not database_url:
        print("❌ No DATABASE_URL provided")
        return
    
    try:
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        # Create daily_click_summary table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS daily_click_summary (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL UNIQUE,
            total_visits INTEGER NOT NULL DEFAULT 0,
            unique_sessions INTEGER NOT NULL DEFAULT 0,
            total_time_spent INTEGER NOT NULL DEFAULT 0,
            avg_time_per_visit DECIMAL(10,2) DEFAULT 0,
            top_pages JSONB DEFAULT '[]'::jsonb,
            referrer_breakdown JSONB DEFAULT '{}'::jsonb,
            hourly_breakdown JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        
        # Sample data for the last 7 days
        today = date.today()
        sample_data = []
        
        for i in range(7):
            day = today - timedelta(days=i)
            visits = 15 + (i * 3)  # Varying visits
            sessions = visits - 2  # Slightly fewer unique sessions
            time_spent = visits * 45 + (i * 20)  # Varying time
            avg_time = round(time_spent / visits, 2) if visits > 0 else 0
            
            sample_data.append({
                'date': day,
                'total_visits': visits,
                'unique_sessions': sessions, 
                'total_time_spent': time_spent,
                'avg_time_per_visit': avg_time,
                'top_pages': [
                    {"page": "Home", "visits": visits // 3},
                    {"page": "About", "visits": visits // 4},
                    {"page": "Projects", "visits": visits // 2}
                ],
                'referrer_breakdown': {
                    "direct": visits // 2,
                    "google": visits // 3,
                    "linkedin": visits // 6
                },
                'hourly_breakdown': {
                    f"{h:02d}": max(0, visits // 24 + (h % 3)) for h in range(24)
                }
            })
        
        # Insert sample data
        insert_query = """
        INSERT INTO daily_click_summary (
            date, total_visits, unique_sessions, total_time_spent, 
            avg_time_per_visit, top_pages, referrer_breakdown, hourly_breakdown
        ) VALUES (%(date)s, %(total_visits)s, %(unique_sessions)s, %(total_time_spent)s,
                 %(avg_time_per_visit)s, %(top_pages)s, %(referrer_breakdown)s, %(hourly_breakdown)s)
        ON CONFLICT (date) DO UPDATE SET
            total_visits = EXCLUDED.total_visits,
            unique_sessions = EXCLUDED.unique_sessions,
            total_time_spent = EXCLUDED.total_time_spent,
            avg_time_per_visit = EXCLUDED.avg_time_per_visit,
            top_pages = EXCLUDED.top_pages,
            referrer_breakdown = EXCLUDED.referrer_breakdown,
            hourly_breakdown = EXCLUDED.hourly_breakdown
        """
        
        for data in sample_data:
            cursor.execute(insert_query, data)
            print(f"✅ Inserted data for {data['date']}: {data['total_visits']} visits")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n🎉 Sample data inserted successfully!")
        print("📊 Check pgAdmin daily_click_summary table")
        print("🚀 Run your Streamlit dashboard to see the charts!")
        
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    insert_sample_daily_data()
