#!/usr/bin/env python3
"""
Enhanced Analytics - Direct from Raw Click Logs
Get detailed insights from individual click records
"""

import os
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
import json

def get_raw_analytics_insights():
    """Get insights directly from click_logs table"""
    
    # Database connection
    db_url = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL") or os.getenv("DB_URL")
    if not db_url:
        db_url = "postgresql://postgres:vZDarOmyRiNkTEDOGjDkDVOWakMLxymj@yamabiko.proxy.rlwy.net:20282/railway"
    
    with psycopg2.connect(db_url) as conn:
        # Get all click data from last 7 days
        query = """
        SELECT 
            page_name,
            tag,
            referrer,
            user_agent,
            time_on_page,
            timestamp,
            session_id
        FROM click_logs 
        WHERE timestamp >= %s
        ORDER BY timestamp DESC
        """
        
        cutoff_date = datetime.now() - timedelta(days=7)
        df = pd.read_sql_query(query, conn, params=[cutoff_date])
        
        if df.empty:
            print("❌ No click data found in the last 7 days")
            return
        
        print(f"🔍 DETAILED ANALYTICS FROM RAW CLICK LOGS")
        print(f"📅 Period: Last 7 days")
        print(f"🖱️  Total Clicks: {len(df)}")
        print("=" * 60)
        
        # Page performance
        print("🏆 TOP PAGES:")
        page_counts = df['page_name'].value_counts()
        for page, count in page_counts.head(10).items():
            avg_time = df[df['page_name'] == page]['time_on_page'].mean()
            percentage = (count / len(df)) * 100
            print(f"   • {page}: {count} clicks ({percentage:.1f}%) - {avg_time:.1f}s avg")
        print()
        
        # Referrer analysis
        print("🌐 TRAFFIC SOURCES:")
        referrer_counts = df['referrer'].value_counts()
        for ref, count in referrer_counts.head(10).items():
            percentage = (count / len(df)) * 100
            # Clean up referrer display
            clean_ref = ref if ref != 'direct' else 'Direct Traffic'
            if 'linkedin' in ref.lower():
                clean_ref = 'LinkedIn'
            elif 'google' in ref.lower():
                clean_ref = 'Google'
            print(f"   • {clean_ref}: {count} clicks ({percentage:.1f}%)")
        print()
        
        # Device analysis (from user_agent)
        print("📱 DEVICE INSIGHTS:")
        mobile_keywords = ['Mobile', 'Android', 'iPhone', 'iPad']
        is_mobile = df['user_agent'].str.contains('|'.join(mobile_keywords), case=False, na=False)
        
        mobile_count = is_mobile.sum()
        desktop_count = len(df) - mobile_count
        
        print(f"   • Mobile: {mobile_count} clicks ({(mobile_count/len(df)*100):.1f}%)")
        print(f"   • Desktop: {desktop_count} clicks ({(desktop_count/len(df)*100):.1f}%)")
        print()
        
        # Time engagement
        print("⏱️  ENGAGEMENT INSIGHTS:")
        avg_time = df['time_on_page'].mean()
        median_time = df['time_on_page'].median()
        high_engagement = (df['time_on_page'] > 60).sum()
        
        print(f"   • Average time on page: {avg_time:.1f} seconds")
        print(f"   • Median time on page: {median_time:.1f} seconds") 
        print(f"   • High engagement visits (>60s): {high_engagement} ({(high_engagement/len(df)*100):.1f}%)")
        print()
        
        # Session analysis
        unique_sessions = df['session_id'].nunique()
        print(f"👥 VISITOR INSIGHTS:")
        print(f"   • Unique sessions: {unique_sessions}")
        print(f"   • Average clicks per session: {len(df)/unique_sessions:.1f}")
        print()
        
        # Generate LinkedIn posts
        print("📝 READY-TO-POST LINKEDIN INSIGHTS:")
        print("=" * 50)
        
        # Top traffic source insight
        top_referrer = referrer_counts.index[0]
        top_ref_count = referrer_counts.iloc[0]
        top_ref_percentage = (top_ref_count / len(df)) * 100
        
        if 'linkedin' in top_referrer.lower():
            print(f"💡 LinkedIn Post 1:")
            print(f"\"🚀 Portfolio analytics update: {top_ref_percentage:.0f}% of my website traffic comes from LinkedIn!")
            print(f"My '{page_counts.index[0]}' project is clearly resonating with the tech community.")
            print(f"Average engagement time: {avg_time:.0f} seconds. Thanks for checking out my work! 🙏\"")
            print()
        
        # Mobile usage insight
        mobile_percentage = (mobile_count / len(df)) * 100
        print(f"💡 LinkedIn Post 2:")
        print(f"\"📱 {mobile_percentage:.0f}% of my portfolio visitors browse on mobile!")
        print(f"This reinforces why I always design with mobile-first principles.")
        print(f"User experience matters across all devices! #WebDev #UX\"")
        print()
        
        # Engagement insight
        print(f"💡 LinkedIn Post 3:")
        print(f"\"📊 Analytics insight: Visitors spend an average of {avg_time:.0f} seconds on my portfolio pages.")
        print(f"{high_engagement} people ({(high_engagement/len(df)*100):.0f}%) stayed longer than 1 minute!")
        print(f"Quality content and clear project documentation really pays off. #DataDriven\"")

if __name__ == "__main__":
    get_raw_analytics_insights()
