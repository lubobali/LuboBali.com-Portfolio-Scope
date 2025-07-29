#!/usr/bin/env python3
"""
Manual Analytics Aggregator
Run this script manually to aggregate data for any specific date
Usage: python manual_aggregator.py [YYYY-MM-DD]
If no date provided, processes yesterday's data
"""

import sys
from datetime import datetime, date
from daily_aggregator import aggregate_daily_data

def main():
    """Main function for manual aggregation"""
    
    target_date = None
    
    # Check if date was provided as argument
    if len(sys.argv) > 1:
        try:
            target_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
            print(f"🎯 Processing data for specified date: {target_date}")
        except ValueError:
            print("❌ Invalid date format. Use YYYY-MM-DD (e.g., 2025-07-29)")
            sys.exit(1)
    else:
        # Default to yesterday
        from datetime import timedelta
        target_date = (datetime.now() - timedelta(days=1)).date()
        print(f"📅 No date specified, processing yesterday: {target_date}")
    
    # Run aggregation
    print("🚀 Starting manual aggregation...")
    success = aggregate_daily_data(target_date)
    
    if success:
        print(f"✅ Manual aggregation completed for {target_date}")
        print("🔄 Dashboard will show updated data on next refresh")
    else:
        print(f"⚠️  No data found for {target_date}")

if __name__ == "__main__":
    main()
