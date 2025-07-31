#!/usr/bin/env python3
"""
Clean Database - Remove Test Data and Start Fresh
Clears all test clicks to prepare for real visitor tracking
"""

import os
import psycopg2
from datetime import datetime

def clean_database():
    """Clear all test data from click_logs and daily_click_summary"""
    
    # Database connection
    db_url = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL") or os.getenv("DB_URL")
    if not db_url:
        db_url = "postgresql://postgres:vZDarOmyRiNkTEDOGjDkDVOWakMLxymj@yamabiko.proxy.rlwy.net:20282/railway"
    
    try:
        with psycopg2.connect(db_url) as conn:
            with conn.cursor() as cursor:
                print("🧹 CLEANING DATABASE - REMOVING TEST DATA")
                print("=" * 50)
                
                # Check current data counts
                cursor.execute("SELECT COUNT(*) FROM click_logs")
                click_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM daily_click_summary")
                summary_count = cursor.fetchone()[0]
                
                print(f"📊 Current data:")
                print(f"   • click_logs: {click_count} records")
                print(f"   • daily_click_summary: {summary_count} records")
                print()
                
                # Confirm deletion
                confirm = input("🗑️  Are you sure you want to DELETE ALL data? (type 'YES' to confirm): ")
                
                if confirm.upper() == 'YES':
                    # Clear both tables
                    cursor.execute("DELETE FROM daily_click_summary")
                    deleted_summary = cursor.rowcount
                    
                    cursor.execute("DELETE FROM click_logs")
                    deleted_clicks = cursor.rowcount
                    
                    # Reset auto-increment sequences if they exist
                    try:
                        cursor.execute("ALTER SEQUENCE click_logs_id_seq RESTART WITH 1")
                        cursor.execute("ALTER SEQUENCE daily_click_summary_id_seq RESTART WITH 1")
                    except:
                        # Sequences might not exist depending on table structure
                        pass
                    
                    conn.commit()
                    
                    print("✅ DATABASE CLEANED SUCCESSFULLY!")
                    print(f"   • Deleted {deleted_clicks} click records")
                    print(f"   • Deleted {deleted_summary} summary records")
                    print(f"   • Reset ID sequences")
                    print()
                    print("🚀 Your analytics are now ready for REAL visitor data!")
                    print("📈 The tracking will start capturing genuine user behavior.")
                    print()
                    print("💡 Next steps:")
                    print("   1. Share your portfolio link on LinkedIn/social media")
                    print("   2. Wait for real visitors to explore your site") 
                    print("   3. Check your dashboard in a few days for real insights!")
                    
                else:
                    print("❌ Operation cancelled. No data was deleted.")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    clean_database()
