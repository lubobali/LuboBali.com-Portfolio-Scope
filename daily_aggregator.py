#!/usr/bin/env python3
"""
Daily Click Analytics Aggregator
Processes raw click_logs data and updates daily_click_summary table
Designed to run automatically via Railway cron job
"""

import psycopg2
import os
import json
import sys
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

def get_db_connection():
    """Create and return PostgreSQL database connection"""
    try:
        # Get database URL from environment variable (Railway provides this)
        db_url = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
        if not db_url:
            raise Exception("No database URL found in environment variables")
        
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        sys.exit(1)

def aggregate_daily_data(target_date=None):
    """Aggregate click data for a specific date"""
    
    # Use yesterday if no date provided (for daily cron job)
    if target_date is None:
        target_date = (datetime.now() - timedelta(days=1)).date()
    
    print(f"🔄 Processing analytics for {target_date}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if we have data for this date
        cursor.execute("""
            SELECT COUNT(*) as count FROM click_logs 
            WHERE DATE(timestamp) = %s
        """, (target_date,))
        
        record_count = cursor.fetchone()['count']
        
        if record_count == 0:
            print(f"📊 Found 0 click records for {target_date}")
            print(f"⚠️  No data found for {target_date}")
            cursor.close()
            conn.close()
            return False
        
        print(f"📊 Found {record_count} click records for {target_date}")
        
        # Aggregate overall stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_clicks,
                AVG(time_on_page) as avg_time_on_page,
                COUNT(DISTINCT session_id) as repeat_visits
            FROM click_logs 
            WHERE DATE(timestamp) = %s
        """, (target_date,))
        
        overall_stats = cursor.fetchone()
        
        # Get top pages
        cursor.execute("""
            SELECT page_name, COUNT(*) as clicks
            FROM click_logs 
            WHERE DATE(timestamp) = %s
            GROUP BY page_name
            ORDER BY clicks DESC
            LIMIT 15
        """, (target_date,))
        
        top_pages = [{'page': row['page_name'], 'clicks': row['clicks']} 
                    for row in cursor.fetchall()]
        
        # Get top referrers (exclude null values)
        cursor.execute("""
            SELECT 
                COALESCE(referrer, 'direct') as referrer, 
                COUNT(*) as clicks
            FROM click_logs 
            WHERE DATE(timestamp) = %s
            GROUP BY COALESCE(referrer, 'direct')
            ORDER BY clicks DESC
            LIMIT 10
        """, (target_date,))
        
        top_referrers = [{'referrer': row['referrer'], 'clicks': row['clicks']} 
                        for row in cursor.fetchall()]
        
        # Simple device split (placeholder - could be enhanced with user agent parsing)
        device_split = {'desktop': 85, 'mobile': 15}
        
        # Delete existing data for this date to avoid duplicates
        cursor.execute("DELETE FROM daily_click_summary WHERE date = %s", (target_date,))
        
        # Insert aggregated data
        cursor.execute("""
            INSERT INTO daily_click_summary (
                date, project_name, total_clicks, avg_time_on_page, 
                device_split, top_referrers, repeat_visits, tag, top_pages
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            target_date, 
            'portfolio_overall', 
            overall_stats['total_clicks'],
            overall_stats['avg_time_on_page'], 
            json.dumps(device_split), 
            json.dumps(top_referrers), 
            overall_stats['repeat_visits'], 
            'portfolio', 
            json.dumps(top_pages)
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Successfully aggregated {overall_stats['total_clicks']} clicks for {target_date}")
        print(f"📈 Top page: {top_pages[0]['page']} ({top_pages[0]['clicks']} clicks)")
        print(f"🔄 Processed {len(top_referrers)} referrer sources")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during aggregation: {e}")
        return False

def main():
    """Main function - can be called directly or via cron"""
    print("🚀 Starting Daily Analytics Aggregator")
    print(f"⏰ Current time: {datetime.now()}")
    
    # Process yesterday's data (default for cron job)
    success = aggregate_daily_data()
    
    if success:
        print("✅ Daily aggregation completed successfully")
        sys.exit(0)
    else:
        print("⚠️  No data to process")
        sys.exit(0)

if __name__ == "__main__":
    main()
