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
        self.db_url = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL") or os.getenv("DB_URL")
        if not self.db_url:
            raise Exception("No database URL found in environment variables")
    
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
            
            print(f"Found {len(clicks)} clicks for {target_date}")
            
            # Aggregate data
            total_clicks = len(clicks)
            project_name = "lubobali_portfolio"  # Your main project
            
            # Calculate average time on page
            times = [click['time_on_page'] for click in clicks if click['time_on_page']]
            avg_time_on_page = sum(times) / len(times) if times else 0
            
            # Device split analysis
            device_counts = defaultdict(int)
            for click in clicks:
                user_agent = click.get('user_agent', '').lower()
                if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
                    device_counts['Mobile'] += 1
                else:
                    device_counts['Desktop'] += 1
            
            # Top referrers analysis
            referrer_counts = defaultdict(int)
            for click in clicks:
                referrer = click.get('referrer', '').strip()
                if not referrer or referrer == 'null' or referrer == '':
                    referrer_counts['Direct Traffic'] += 1
                else:
                    # Clean up referrer URL
                    if referrer.startswith('http'):
                        referrer_counts[referrer] += 1
                    else:
                        referrer_counts['Direct Traffic'] += 1
            
            # Top pages analysis
            page_counts = defaultdict(int)
            for click in clicks:
                page_name = click.get('page_name', 'unknown')
                # Clean page names
                if page_name.startswith('/'):
                    page_name = page_name
                elif not page_name.startswith('/') and page_name != 'home':
                    page_name = f'/{page_name}'
                elif page_name == 'home' or page_name == '':
                    page_name = 'home'
                page_counts[page_name] += 1
            
            # Count repeat visits (same session_id)
            session_ids = [click['session_id'] for click in clicks if click.get('session_id')]
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
            print(f"✅ Successfully aggregated {total_clicks} clicks for {target_date}")
            print(f"📊 Summary: {total_clicks} clicks, {len(set(session_ids))} sessions, {avg_time_on_page:.1f}s avg time")
            
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
