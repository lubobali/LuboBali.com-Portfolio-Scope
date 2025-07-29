#!/usr/bin/env python3
"""
Railway Cron Job Entry Point for Daily Analytics Aggregation
Runs daily at midnight UTC to process click_logs into daily_click_summary
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from daily_aggregator import DailyAggregator

def main():
    """
    Railway cron job main function
    Processes yesterday's analytics data automatically
    """
    print(f"🕛 Railway Cron Job Started at {datetime.now()} UTC")
    print("=" * 50)
    
    try:
        # Initialize aggregator
        aggregator = DailyAggregator()
        
        # Connect to database
        aggregator.connect_db()
        
        # Process yesterday's data (since this runs at midnight)
        yesterday = date.today() - timedelta(days=1)
        result = aggregator.process_date(yesterday)
        
        if result:
            print(f"✅ Railway Cron: Successfully processed {result['total_clicks']} clicks for {yesterday}")
            print(f"📊 Summary: {result['unique_sessions']} sessions, {result['avg_time_on_page']}s avg time")
        else:
            print(f"⚠️  Railway Cron: No data found for {yesterday}")
        
        # Close connection
        aggregator.close_db()
        
        print("🎉 Railway Cron Job Completed Successfully!")
        
    except Exception as e:
        print(f"💥 Railway Cron Job Failed: {e}")
        sys.exit(1)  # Exit with error code for Railway monitoring

if __name__ == "__main__":
    main()
