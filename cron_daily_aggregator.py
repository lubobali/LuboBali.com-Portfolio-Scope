#!/usr/bin/env python3
"""
Railway Cron Job Entry Point for Daily Analytics Aggregator
Runs daily at midnight UTC to process previous day's click data
"""

import os
import sys
from datetime import datetime, timezone
from daily_aggregator import DailyAggregator

def main():
    """Main cron job execution"""
    start_time = datetime.now(timezone.utc)
    print(f"🕛 Railway Cron Job Started at {start_time}")
    print("=" * 50)
    
    try:
        # Initialize aggregator
        aggregator = DailyAggregator()
        
        # Run aggregation for yesterday
        print("🚀 Starting daily aggregation for previous day...")
        aggregator.run_daily_aggregation(days_back=1)
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        print("=" * 50)
        print(f"✅ Railway Cron Job Completed Successfully!")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🕐 Finished at {end_time}")
        
    except Exception as e:
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        print("=" * 50)
        print(f"💥 Railway Cron Job Failed: {e}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🕐 Failed at {end_time}")
        sys.exit(1)

if __name__ == "__main__":
    main()
