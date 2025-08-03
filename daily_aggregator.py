#!/usr/bin/env python3
"""
Daily Analytics Aggregator for Portfolio Click Tracker
Processes raw click_logs and creates daily summary statistics
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date, timedelta
from collections import defaultdict, Counter
import json

class DailyAggregator:
    def __init__(self):
        """Initialize the aggregator with database connection"""
        # Try Railway's database environment variables
        self.db_url = (
            os.getenv("DATABASE_URL") or 
            os.getenv("DATABASE_PUBLIC_URL") or 
            os.getenv("PGURL") or
            os.getenv("DB_URL") or
            self._build_url_from_parts()
        )
        if not self.db_url:
            raise Exception("No database URL found in environment variables")
    
    def _build_url_from_parts(self):
        """Build database URL from individual environment variables (Railway style)"""
        host = os.getenv("PGHOST")
        port = os.getenv("PGPORT", "5432")
        database = os.getenv("PGDATABASE")
        user = os.getenv("PGUSER")
        password = os.getenv("PGPASSWORD")
        
        if all([host, database, user, password]):
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        return None
    
    def get_db_connection(self):
        """Create database connection"""
        try:
            return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
    
    def aggregate_day(self, target_date):
        """Aggregate click data for a specific date"""
        print(f"Starting aggregation for {target_date}")
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get all clicks for the target date
            query = """
            SELECT * FROM click_logs 
            WHERE DATE(timestamp) = %s
            ORDER BY timestamp
            """
            cursor.execute(query, (target_date,))
            clicks = cursor.fetchall()
            
            if not clicks:
                print(f"No clicks found for {target_date}")
                return
            
            print(f"Found {len(clicks)} raw click events for {target_date}")
            print(f"Deduplicating to unique pageviews (collapsing arrival+exit events)...")
            
            # --- NEW: collapse arrival+exit to one pageview per (session_id, page_name) ---
            pageviews = {}
            first_event_for_referrer = {}
            
            for c in clicks:
                key = (c.get('session_id'), c.get('page_name'))
                # keep first event for referrer (usually arrival)
                if key not in first_event_for_referrer:
                    first_event_for_referrer[key] = c
                prev = pageviews.get(key)
                # choose the event with the larger time_on_page (exit > arrival)
                cur_time = c.get('time_on_page') or 0
                prev_time = (prev.get('time_on_page') or 0) if prev else -1
                if prev is None or cur_time > prev_time:
                    pageviews[key] = c
            
            # Use deduped pageviews for metrics
            total_clicks = len(pageviews)  # unique pageviews, not raw rows
            project_name = "lubobali_portfolio"  # Your main project
            
            times = [pv.get('time_on_page') or 0 for pv in pageviews.values() if (pv.get('time_on_page') or 0) > 0]
            avg_time_on_page = round(sum(times) / len(times), 2) if times else 0
            
            # Device split (from chosen pageview event)
            device_counts = {"Mobile": 0, "Desktop": 0}
            for pv in pageviews.values():
                ua = (pv.get('user_agent') or '').lower()
                if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
                    device_counts['Mobile'] += 1
                else:
                    device_counts['Desktop'] += 1
            
            # Top referrers (prefer the first event per pageview, i.e., the arrival)
            referrer_counts = {}
            for key, first in first_event_for_referrer.items():
                referrer = (first.get('referrer') or '').strip()
                if not referrer or referrer == 'null':
                    referrer = 'Direct Traffic'
                elif not referrer.startswith('http'):
                    referrer = 'Direct Traffic'
                referrer_counts[referrer] = referrer_counts.get(referrer, 0) + 1
            
            # Top pages from chosen pageviews
            page_counts = {}
            for pv in pageviews.values():
                page_name = pv.get('page_name', 'unknown') or 'unknown'
                if page_name == '' or page_name == 'home': page_name = 'home'
                elif not page_name.startswith('/') and page_name != 'home': page_name = f'/{page_name}'
                page_counts[page_name] = page_counts.get(page_name, 0) + 1
            
            # Repeat visits based on unique sessions
            session_ids = [sid for (sid, _page) in pageviews.keys() if sid]
            unique_sessions = len(set(session_ids))
            repeat_visits = total_clicks - unique_sessions if unique_sessions > 0 else 0
            
            # Prepare data for insertion
            summary_data = {
                'date': target_date,
                'project_name': project_name,
                'total_clicks': total_clicks,
                'avg_time_on_page': round(avg_time_on_page, 2),
                'device_split': dict(device_counts),
                'top_referrers': dict(referrer_counts),
                'top_pages': dict(page_counts),
                'repeat_visits': repeat_visits,
                'tag': 'general'
            }
            
            # Delete existing data for this date (if any)
            delete_query = "DELETE FROM daily_click_summary WHERE date = %s"
            cursor.execute(delete_query, (target_date,))
            
            # Insert new aggregated data
            insert_query = """
            INSERT INTO daily_click_summary 
            (date, project_name, total_clicks, avg_time_on_page, device_split, 
             top_referrers, top_pages, repeat_visits, tag, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                summary_data['date'],
                summary_data['project_name'],
                summary_data['total_clicks'],
                summary_data['avg_time_on_page'],
                json.dumps(summary_data['device_split']),
                json.dumps(summary_data['top_referrers']),
                json.dumps(summary_data['top_pages']),
                summary_data['repeat_visits'],
                summary_data['tag'],
                datetime.now()
            ))
            
            conn.commit()
            print(f"✅ Successfully aggregated {len(clicks)} raw events → {total_clicks} unique pageviews for {target_date}")
            print(f"📊 Summary: {total_clicks} pageviews, {len(set(session_ids))} sessions, {avg_time_on_page:.1f}s avg time")
            
        except Exception as e:
            print(f"❌ Error during aggregation: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
    
    def run_daily_aggregation(self, days_back=1):
        """Run aggregation for the previous day(s)"""
        target_date = date.today() - timedelta(days=days_back)
        self.aggregate_day(target_date)

if __name__ == "__main__":
    # For manual testing
    aggregator = DailyAggregator()
    aggregator.run_daily_aggregation(days_back=1)
