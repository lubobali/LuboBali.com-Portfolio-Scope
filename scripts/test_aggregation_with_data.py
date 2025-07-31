#!/usr/bin/env python3
"""
Test script to run daily aggregation with real click data
This will process actual clicks from click_logs into daily_click_summary
"""

import os
from datetime import date, timedelta, datetime
from daily_aggregator import DailyAggregator

def main():
    print("🧪 Testing Daily Aggregation with Real Data")
    print("=" * 50)
    
    # You need to set your Railway DATABASE_URL here
    # Get it from Railway Variables tab and paste it below:
    database_url = input("Paste your DATABASE_URL from Railway Variables: ").strip()
    
    if not database_url:
        print("❌ No DATABASE_URL provided. Exiting.")
        return
    
    # Set the environment variable
    os.environ['DATABASE_URL'] = database_url
    
    try:
        # Create aggregator instance
        aggregator = DailyAggregator()
        
        # Get date range to aggregate (last few days)
        today = date.today()
        dates_to_process = [
            today - timedelta(days=3),  # 3 days ago
            today - timedelta(days=2),  # 2 days ago  
            today - timedelta(days=1),  # yesterday
            today                       # today
        ]
        
        print(f"📅 Processing dates: {[str(d) for d in dates_to_process]}")
        print()
        
        for target_date in dates_to_process:
            print(f"🔄 Processing {target_date}...")
            result = aggregator.aggregate_day(target_date)
            
            if result['success']:
                print(f"✅ Successfully processed {target_date}")
                print(f"   📊 Summary: {result['summary']}")
            else:
                print(f"❌ Failed to process {target_date}: {result['error']}")
            print()
        
        print("🎉 Aggregation test complete!")
        print("🔍 Check pgAdmin daily_click_summary table to see results")
        print("📊 Run your Streamlit dashboard to visualize the data")
        
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    main()
