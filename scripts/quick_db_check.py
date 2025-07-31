import psycopg2
import os
from datetime import datetime

# Use the same database URL pattern as your other scripts
DATABASE_URL = "postgresql://postgres:ZeuqoKYiHqzUxCQtCTOOJDWhMLDVrpJd@postgres.railway.internal:5432/railway"

try:
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Check recent clicks
    cur.execute('SELECT id, page_name, timestamp, session_id FROM click_logs ORDER BY timestamp DESC LIMIT 5')
    recent_clicks = cur.fetchall()

    print('🔍 Recent clicks:')
    for click in recent_clicks:
        print(f'  ID: {click[0]}, Page: {click[1]}, Time: {click[2]}, Session: {click[3]}')

    # Check if cron job has run recently
    cur.execute('SELECT summary_date, total_clicks FROM daily_click_summary ORDER BY summary_date DESC LIMIT 3')
    recent_summaries = cur.fetchall()

    print('\n📊 Recent daily summaries:')
    for summary in recent_summaries:
        print(f'  Date: {summary[0]}, Total clicks: {summary[1]}')

    # Check total counts
    cur.execute('SELECT COUNT(*) FROM click_logs')
    total_clicks = cur.fetchone()[0]
    
    cur.execute('SELECT COUNT(*) FROM daily_click_summary')
    total_summaries = cur.fetchone()[0]

    print(f'\n📈 Totals: {total_clicks} clicks, {total_summaries} daily summaries')

    cur.close()
    conn.close()
    print("\n✅ Database connection successful!")

except Exception as e:
    print(f"❌ Database error: {e}")
