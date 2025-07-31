#!/usr/bin/env python3
"""
Test script to insert sample data into daily_click_summary table
Uses the real Railway database connection
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime, date, timedelta

# Set the database URL (try with default Railway database name)
DATABASE_URL = "postgresql://postgres:vZDarOmyRiNkTEDOGjDkDVOWakMLxymj@yamabiko.proxy.rlwy.net:20282/railway"

def get_db_connection():
    """Create and return PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def create_daily_summary_table():
    """Create daily_click_summary table if it doesn't exist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS daily_click_summary (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            project_name TEXT NOT NULL,
            total_clicks INT NOT NULL DEFAULT 0,
            avg_time_on_page FLOAT,
            device_split JSON,
            top_referrers JSON,
            repeat_visits INT NOT NULL DEFAULT 0,
            tag TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE(date, project_name, tag)
        );
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        print("✓ daily_click_summary table created/verified")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating daily_click_summary table: {e}")
        raise

def insert_sample_data():
    """Insert sample aggregated data for testing"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Sample data for the last few days
        sample_data = [
            {
                'date': date.today() - timedelta(days=1),
                'project_name': 'lubobali_portfolio',
                'total_clicks': 25,
                'avg_time_on_page': 45.5,
                'device_split': {
                    "Desktop": 18,
                    "Mobile": 7
                },
                'top_referrers': {
                    "Direct Traffic": 15,
                    "Google": 7,
                    "LinkedIn": 3
                },
                'repeat_visits': 5,
                'tag': None
            },
            {
                'date': date.today() - timedelta(days=2),
                'project_name': 'lubobali_portfolio',
                'total_clicks': 18,
                'avg_time_on_page': 38.2,
                'device_split': {
                    "Desktop": 12,
                    "Mobile": 6
                },
                'top_referrers': {
                    "Direct Traffic": 10,
                    "Google": 5,
                    "Twitter": 3
                },
                'repeat_visits': 3,
                'tag': None
            },
            {
                'date': date.today() - timedelta(days=3),
                'project_name': 'lubobali_portfolio',
                'total_clicks': 32,
                'avg_time_on_page': 52.1,
                'device_split': {
                    "Desktop": 22,
                    "Mobile": 10
                },
                'top_referrers': {
                    "Direct Traffic": 18,
                    "Google": 10,
                    "LinkedIn": 4
                },
                'repeat_visits': 8,
                'tag': None
            }
        ]
        
        # Insert each day's data
        for data in sample_data:
            insert_query = """
            INSERT INTO daily_click_summary (
                date, project_name, total_clicks, avg_time_on_page, 
                device_split, top_referrers, repeat_visits, tag
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (date, project_name, tag) DO UPDATE SET
                total_clicks = EXCLUDED.total_clicks,
                avg_time_on_page = EXCLUDED.avg_time_on_page,
                device_split = EXCLUDED.device_split,
                top_referrers = EXCLUDED.top_referrers,
                repeat_visits = EXCLUDED.repeat_visits,
                created_at = CURRENT_TIMESTAMP
            RETURNING id, date
            """
            
            cursor.execute(insert_query, (
                data['date'],
                data['project_name'],
                data['total_clicks'],
                data['avg_time_on_page'],
                json.dumps(data['device_split']),
                json.dumps(data['top_referrers']),
                data['repeat_visits'],
                data['tag']
            ))
            
            result = cursor.fetchone()
            print(f"✓ Inserted/Updated data for {data['date']}: ID {result['id']}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n🎉 Successfully inserted sample data for {len(sample_data)} days!")
        print("You can now check pgAdmin and test your Streamlit dashboard!")
        
    except Exception as e:
        print(f"Error inserting sample data: {e}")
        raise

def check_data():
    """Check what data exists in both tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check click_logs
        cursor.execute("SELECT COUNT(*) as count FROM click_logs")
        click_logs_count = cursor.fetchone()['count']
        print(f"📊 click_logs table has {click_logs_count} records")
        
        # Check daily_click_summary
        cursor.execute("SELECT COUNT(*) as count FROM daily_click_summary")
        summary_count = cursor.fetchone()['count']
        print(f"📊 daily_click_summary table has {summary_count} records")
        
        # Show recent summary data
        cursor.execute("""
            SELECT date, project_name, total_clicks, avg_time_on_page, repeat_visits 
            FROM daily_click_summary 
            ORDER BY date DESC 
            LIMIT 5
        """)
        summaries = cursor.fetchall()
        
        print("\n📈 Recent daily summaries:")
        for summary in summaries:
            print(f"  {summary['date']}: {summary['total_clicks']} clicks, {summary['avg_time_on_page']:.1f}s avg, {summary['repeat_visits']} repeat visits")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error checking data: {e}")

if __name__ == "__main__":
    print("🚀 Testing with real Railway database...")
    print("=" * 50)
    
    try:
        # Create table if needed
        create_daily_summary_table()
        
        # Insert sample data
        insert_sample_data()
        
        # Check current data
        check_data()
        
        print("\n✅ Test completed successfully!")
        print("Now you can:")
        print("1. Check pgAdmin to see the daily_click_summary table")
        print("2. Run your Streamlit dashboard to visualize the data")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
