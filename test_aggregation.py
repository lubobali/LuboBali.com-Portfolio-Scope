#!/usr/bin/env python3
"""
Test script to manually run aggregation with Railway's public database URL
This will help us verify the aggregation logic works
"""

import os
from daily_aggregator import DailyAggregator
from datetime import date, timedelta

def test_aggregation():
    """Test the aggregation with Railway's database"""
    print("🧪 Testing Daily Aggregation...")
    print("=" * 50)
    
    try:
        # Create aggregator instance
        aggregator = DailyAggregator()
        
        # Test connection first
        conn = aggregator.get_db_connection()
        print("✅ Database connection successful!")
        conn.close()
        
        # Run aggregation for yesterday
        target_date = date.today() - timedelta(days=1)
        print(f"📊 Running aggregation for {target_date}")
        
        aggregator.aggregate_day(target_date)
        
        print("✅ Aggregation completed successfully!")
        
    except Exception as e:
        print(f"❌ Aggregation failed: {e}")
        raise

if __name__ == "__main__":
    test_aggregation()
