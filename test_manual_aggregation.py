#!/usr/bin/env python3
"""
Test Daily Aggregator Locally using Railway Internal URL
"""

import os
import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date, timedelta

# Test if we can connect using the same URL that app.py uses
DATABASE_URL = "postgresql://postgres:ZeuqoKYiHqzUxCQtCTOOJDWhMLDVrpJd@postgres.railway.internal:5432/railway"

def test_daily_aggregation():
    """Test the daily aggregation manually"""
    try:
        print("🔍 Testing daily aggregation...")
        
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        # Get yesterday's date
        yesterday = date.today() - timedelta(days=1)
        print(f"📅 Aggregating data for: {yesterday}")
        
        # Check if we already have a summary for yesterday
        cur.execute(
            "SELECT * FROM daily_click_summary WHERE summary_date = %s",
            (yesterday,)
        )
        existing = cur.fetchone()
        
        if existing:
            print(f"⚠️ Summary already exists for {yesterday}: {existing['total_clicks']} clicks")
            return
        
        # Get clicks for yesterday
        cur.execute("""
            SELECT 
                session_id,
                page_name,
                visit_duration,
                time_on_page,
                user_agent,
                referrer
            FROM click_logs 
            WHERE DATE(timestamp) = %s
        """, (yesterday,))
        
        clicks = cur.fetchall()
        print(f"📊 Found {len(clicks)} clicks for {yesterday}")
        
        if len(clicks) == 0:
            print("❌ No clicks found for yesterday. Nothing to aggregate.")
            return
            
        # Calculate summary statistics
        total_clicks = len(clicks)
        unique_sessions = len(set(click['session_id'] for click in clicks))
        unique_pages = len(set(click['page_name'] for click in clicks))
        
        avg_duration = sum(click.get('visit_duration', 0) for click in clicks) / total_clicks if total_clicks > 0 else 0
        avg_time_on_page = sum(click.get('time_on_page', 0) for click in clicks) / total_clicks if total_clicks > 0 else 0
        
        # Count page views
        page_views = {}
        for click in clicks:
            page = click['page_name']
            page_views[page] = page_views.get(page, 0) + 1
        
        # Count referrers
        referrers = {}
        for click in clicks:
            ref = click.get('referrer', 'direct')
            referrers[ref] = referrers.get(ref, 0) + 1
        
        # Insert summary
        cur.execute("""
            INSERT INTO daily_click_summary (
                summary_date,
                total_clicks,
                unique_sessions,
                unique_pages,
                avg_visit_duration,
                avg_time_on_page,
                page_views,
                referrer_breakdown
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            yesterday,
            total_clicks,
            unique_sessions,
            unique_pages,
            avg_duration,
            avg_time_on_page,
            json.dumps(page_views),
            json.dumps(referrers)
        ))
        
        summary_id = cur.fetchone()['id']
        conn.commit()
        
        print(f"✅ Daily summary created successfully!")
        print(f"   ID: {summary_id}")
        print(f"   Date: {yesterday}")
        print(f"   Total Clicks: {total_clicks}")
        print(f"   Unique Sessions: {unique_sessions}")
        print(f"   Unique Pages: {unique_pages}")
        print(f"   Avg Duration: {avg_duration:.2f}ms")
        print(f"   Top Pages: {dict(list(page_views.items())[:3])}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_daily_aggregation()
