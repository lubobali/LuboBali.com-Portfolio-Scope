#!/usr/bin/env python3
"""
Step 8: Portfolio Analytics Analysis & Insights
Generate LinkedIn-worthy insights from your analytics data
"""

import os
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import json

class PortfolioInsightAnalyzer:
    def __init__(self):
        """Initialize with database connection"""
        self.db_url = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL") or os.getenv("DB_URL")
        if not self.db_url:
            # For local development
            self.db_url = "postgresql://postgres:vZDarOmyRiNkTEDOGjDkDVOWakMLxymj@yamabiko.proxy.rlwy.net:20282/railway"
    
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url)
    
    def fetch_top_performing_projects(self, days_back=7):
        """Find which projects/pages get the most engagement"""
        query = """
        SELECT 
            project_name,
            SUM(total_clicks) as total_clicks,
            AVG(avg_time_on_page) as avg_engagement_time,
            COUNT(*) as days_active
        FROM daily_click_summary 
        WHERE date >= %s
        GROUP BY project_name
        ORDER BY total_clicks DESC
        LIMIT 10
        """
        
        with self.get_connection() as conn:
            cutoff_date = datetime.now().date() - timedelta(days=days_back)
            df = pd.read_sql_query(query, conn, params=[cutoff_date])
            return df
    
    def analyze_traffic_sources(self, days_back=7):
        """Analyze where your traffic comes from"""
        query = """
        SELECT 
            date,
            top_referrers
        FROM daily_click_summary 
        WHERE date >= %s AND top_referrers IS NOT NULL
        """
        
        with self.get_connection() as conn:
            cutoff_date = datetime.now().date() - timedelta(days=days_back)
            df = pd.read_sql_query(query, conn, params=[cutoff_date])
            
            # Parse JSON referrers and aggregate
            all_referrers = {}
            for _, row in df.iterrows():
                try:
                    referrers = json.loads(row['top_referrers'])
                    for ref, count in referrers.items():
                        all_referrers[ref] = all_referrers.get(ref, 0) + count
                except:
                    continue
            
            return all_referrers
    
    def get_device_insights(self, days_back=7):
        """Analyze device usage patterns"""
        query = """
        SELECT 
            date,
            device_split
        FROM daily_click_summary 
        WHERE date >= %s AND device_split IS NOT NULL
        """
        
        with self.get_connection() as conn:
            cutoff_date = datetime.now().date() - timedelta(days=days_back)
            df = pd.read_sql_query(query, conn, params=[cutoff_date])
            
            # Parse JSON device data and aggregate
            all_devices = {}
            for _, row in df.iterrows():
                try:
                    devices = json.loads(row['device_split'])
                    for device, count in devices.items():
                        all_devices[device] = all_devices.get(device, 0) + count
                except:
                    continue
            
            return all_devices
    
    def generate_linkedin_insights(self, days_back=7):
        """Generate ready-to-post LinkedIn insights"""
        print(f"🔍 Analyzing last {days_back} days of portfolio analytics...")
        print("=" * 60)
        
        # Get top projects
        top_projects = self.fetch_top_performing_projects(days_back)
        
        # Get traffic sources  
        referrers = self.analyze_traffic_sources(days_back)
        
        # Get device data
        devices = self.get_device_insights(days_back)
        
        # Calculate totals
        total_clicks = top_projects['total_clicks'].sum()
        avg_time = top_projects['avg_engagement_time'].mean()
        
        print(f"📊 PORTFOLIO ANALYTICS INSIGHTS")
        print(f"📅 Period: Last {days_back} days")
        print(f"🖱️  Total Clicks: {total_clicks}")
        print(f"⏱️  Average Time on Page: {avg_time:.1f} seconds")
        print()
        
        # Top performing projects
        print("🏆 TOP PERFORMING PROJECTS:")
        for idx, row in top_projects.head(5).iterrows():
            print(f"   {idx+1}. {row['project_name']}: {row['total_clicks']} clicks ({row['avg_engagement_time']:.1f}s avg)")
        print()
        
        # Traffic sources
        if referrers:
            print("🌐 TRAFFIC SOURCES:")
            sorted_refs = sorted(referrers.items(), key=lambda x: x[1], reverse=True)
            for ref, count in sorted_refs[:5]:
                percentage = (count / sum(referrers.values())) * 100
                print(f"   • {ref}: {count} clicks ({percentage:.1f}%)")
        print()
        
        # Device breakdown
        if devices:
            print("📱 DEVICE BREAKDOWN:")
            sorted_devices = sorted(devices.items(), key=lambda x: x[1], reverse=True)
            for device, count in sorted_devices:
                percentage = (count / sum(devices.values())) * 100
                print(f"   • {device}: {count} clicks ({percentage:.1f}%)")
        print()
        
        # Generate LinkedIn post suggestions
        print("📝 LINKEDIN POST IDEAS:")
        print("=" * 40)
        
        if referrers and len(referrers) > 0:
            top_referrer = max(referrers.items(), key=lambda x: x[1])
            ref_percentage = (top_referrer[1] / sum(referrers.values())) * 100
            
            print(f"💡 Post Idea 1:")
            print(f"   '{ref_percentage:.0f}% of traffic to my portfolio came from {top_referrer[0]} this week!'")
            print(f"   'My {top_projects.iloc[0]['project_name']} project is clearly resonating with the community 🚀'")
            print()
        
        if len(top_projects) > 1:
            print(f"💡 Post Idea 2:")
            print(f"   'Portfolio analytics update: {top_projects.iloc[0]['project_name']} is my most viewed project'")
            print(f"   'with {top_projects.iloc[0]['total_clicks']} clicks and {top_projects.iloc[0]['avg_engagement_time']:.1f}s average engagement!'")
            print()
        
        if devices:
            mobile_percentage = sum(count for device, count in devices.items() if 'mobile' in device.lower()) / sum(devices.values()) * 100
            if mobile_percentage > 50:
                print(f"💡 Post Idea 3:")
                print(f"   '{mobile_percentage:.0f}% of my portfolio visitors are on mobile! 📱'")
                print(f"   'Always designing with mobile-first in mind pays off!'")
        
        print("\n🎯 Ready to share your data-driven insights on LinkedIn!")

def main():
    """Run the analysis"""
    analyzer = PortfolioInsightAnalyzer()
    
    # Generate insights for different time periods
    print("🚀 WEEKLY INSIGHTS (Last 7 days)")
    analyzer.generate_linkedin_insights(days_back=7)
    
    print("\n" + "="*80 + "\n")
    
    print("📈 MONTHLY INSIGHTS (Last 30 days)")  
    analyzer.generate_linkedin_insights(days_back=30)

if __name__ == "__main__":
    main()
