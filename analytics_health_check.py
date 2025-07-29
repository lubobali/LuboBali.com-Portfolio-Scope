#!/usr/bin/env python3
"""
Analytics Health Check
Verifies that the analytics pipeline is working correctly
Checks both real-time data flow and daily aggregation
"""

import psycopg2
import os
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

def get_db_connection():
    """Create and return PostgreSQL database connection"""
    try:
        db_url = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
        if not db_url:
            raise Exception("No database URL found in environment variables")
        
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def check_analytics_health():
    """Check the health of the analytics pipeline"""
    print("🔍 Analytics Pipeline Health Check")
    print("=" * 50)
    
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # 1. Check raw click logs
        cursor.execute("SELECT COUNT(*) as total FROM click_logs")
        total_clicks = cursor.fetchone()['total']
        print(f"📊 Total clicks in database: {total_clicks:,}")
        
        # 2. Check recent activity (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) as recent 
            FROM click_logs 
            WHERE timestamp > NOW() - INTERVAL '24 hours'
        """)
        recent_clicks = cursor.fetchone()['recent']
        print(f"🕒 Clicks in last 24 hours: {recent_clicks:,}")
        
        # 3. Check daily summary table
        cursor.execute("SELECT COUNT(*) as summary_days FROM daily_click_summary")
        summary_days = cursor.fetchone()['summary_days']
        print(f"📈 Days in summary table: {summary_days}")
        
        # 4. Check latest aggregated date
        cursor.execute("""
            SELECT date, total_clicks 
            FROM daily_click_summary 
            ORDER BY date DESC 
            LIMIT 1
        """)
        latest_summary = cursor.fetchone()
        if latest_summary:
            print(f"📅 Latest aggregated date: {latest_summary['date']} ({latest_summary['total_clicks']} clicks)")
        else:
            print("⚠️  No data in summary table")
        
        # 5. Check for gaps in aggregation
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        cursor.execute("""
            SELECT COUNT(*) as has_data 
            FROM click_logs 
            WHERE DATE(timestamp) = %s
        """, (yesterday,))
        yesterday_raw = cursor.fetchone()['has_data']
        
        cursor.execute("""
            SELECT COUNT(*) as has_summary 
            FROM daily_click_summary 
            WHERE date = %s
        """, (yesterday,))
        yesterday_summary = cursor.fetchone()['has_summary']
        
        print(f"\n🔄 Yesterday ({yesterday}) status:")
        print(f"   Raw clicks: {yesterday_raw}")
        print(f"   Aggregated: {'✅ Yes' if yesterday_summary > 0 else '❌ No'}")
        
        # 6. Overall health assessment
        print(f"\n🎯 Health Assessment:")
        health_score = 0
        
        if total_clicks > 0:
            print("   ✅ Database has click data")
            health_score += 1
        else:
            print("   ❌ No click data found")
        
        if summary_days > 0:
            print("   ✅ Daily aggregation working")
            health_score += 1
        else:
            print("   ❌ No daily aggregation data")
        
        if yesterday_raw > 0 and yesterday_summary > 0:
            print("   ✅ Recent data is aggregated")
            health_score += 1
        elif yesterday_raw > 0:
            print("   ⚠️  Recent data needs aggregation")
        else:
            print("   ℹ️  No recent data to aggregate")
            health_score += 1
        
        print(f"\n🏆 Overall Health: {health_score}/3")
        
        if health_score >= 2:
            print("✅ Analytics pipeline is healthy!")
            return True
        else:
            print("⚠️  Analytics pipeline needs attention")
            return False
            
    except Exception as e:
        print(f"❌ Error during health check: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    """Main function"""
    check_analytics_health()

if __name__ == "__main__":
    main()
