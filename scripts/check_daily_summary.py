import psycopg2

# Use external Railway URL for database connection  
DATABASE_URL = "postgresql://postgres:ZeuqoKYiHqzUxCQtCTOOJDWhMLDVrpJd@viaduct.proxy.rlwy.net:29608/railway?sslmode=require"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Check daily_click_summary table
    cur.execute('SELECT summary_date, total_clicks, unique_sessions FROM daily_click_summary ORDER BY summary_date DESC LIMIT 10')
    summaries = cur.fetchall()

    print('📊 Daily Click Summary Table:')
    if summaries:
        for summary in summaries:
            print(f'  Date: {summary[0]}, Clicks: {summary[1]}, Sessions: {summary[2]}')
    else:
        print('  ❌ No data in daily_click_summary table')

    # Check if we have clicks from today that could be aggregated
    cur.execute("SELECT DATE(timestamp), COUNT(*) FROM click_logs GROUP BY DATE(timestamp) ORDER BY DATE(timestamp) DESC LIMIT 5")
    daily_clicks = cur.fetchall()

    print('\n📈 Clicks by day (from click_logs):')
    for day in daily_clicks:
        print(f'  Date: {day[0]}, Clicks: {day[1]}')

    cur.close()
    conn.close()
    print("\n✅ Database check complete!")

except Exception as e:
    print(f"❌ Database error: {e}")
