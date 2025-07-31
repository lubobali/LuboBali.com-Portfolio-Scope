#!/usr/bin/env python3
"""
Debug script to check what data the dashboard is receiving
"""

import os
import psycopg2
import pandas as pd
import json

# Database URL
DATABASE_URL = "postgresql://postgres:vZDarOmyRiNkTEDOGjDkDVOWakMLxymj@yamabiko.proxy.rlwy.net:20282/railway"

def debug_dashboard_data():
    """Debug what data the dashboard is loading"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        
        # Same query as dashboard
        query = """
        SELECT date, project_name, total_clicks, repeat_visits, avg_time_on_page, 
               device_split, top_referrers, top_pages
        FROM daily_click_summary 
        ORDER BY date DESC, total_clicks DESC
        LIMIT 100
        """
        
        print("🔍 Executing dashboard query...")
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        print(f"📊 Found {len(df)} records")
        print("\n📋 DataFrame columns:", df.columns.tolist())
        print("\n📋 DataFrame shape:", df.shape)
        
        if not df.empty:
            print("\n🔍 Sample data:")
            for i, row in df.iterrows():
                print(f"\nRecord {i+1}:")
                print(f"  Date: {row['date']}")
                print(f"  Project: {row['project_name']}")
                print(f"  Total clicks: {row['total_clicks']}")
                print(f"  Top pages (raw): {row['top_pages']}")
                print(f"  Top pages type: {type(row['top_pages'])}")
                
                # Try to parse JSON
                try:
                    if isinstance(row['top_pages'], str):
                        parsed = json.loads(row['top_pages'])
                        print(f"  Top pages (parsed): {parsed}")
                    else:
                        print(f"  Top pages (direct): {row['top_pages']}")
                except Exception as e:
                    print(f"  JSON parse error: {e}")
        
        # Test the parsing function
        print("\n🧪 Testing parse_json_column function:")
        
        def parse_json_column(df, column_name):
            """Same function as dashboard"""
            try:
                if column_name in df.columns:
                    return df[column_name].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
                return None
            except Exception as e:
                print(f"Parse error: {e}")
                return None
        
        top_pages_data = parse_json_column(df, 'top_pages')
        print(f"Parsed top_pages_data: {top_pages_data}")
        
        if top_pages_data is not None and not top_pages_data.empty:
            print("✅ Top pages data parsed successfully!")
            latest_pages = top_pages_data.iloc[0] if not top_pages_data.empty else {}
            print(f"Latest pages: {latest_pages}")
        else:
            print("❌ Top pages data is empty or failed to parse")
        
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    debug_dashboard_data()
