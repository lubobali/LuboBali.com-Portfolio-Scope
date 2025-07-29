"""
Daily Aggregator for Portfolio Analytics
Processes raw click_logs into daily_click_summary table
Run once per day to generate analytics insights
"""

import os
import psycopg2
from datetime import datetime, date, timedelta
import json
from collections import defaultdict, Counter

class DailyAggregator:
    def __init__(self):
        # Database connection using environment variables
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.connection = None
    
    def connect_db(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(self.db_url)
            print("✅ Connected to database")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def close_db(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("🔌 Database connection closed")
    
    def get_raw_data_for_date(self, target_date):
        """
        Get all click_logs for a specific date
        Returns: List of tuples with click data
        """
        cursor = self.connection.cursor()
        
        query = """
        SELECT 
            page_name,
            tag,
            time_on_page,
            session_id,
            referrer,
            user_agent,
            timestamp
        FROM click_logs 
        WHERE DATE(timestamp) = %s
        ORDER BY timestamp;
        """
        
        cursor.execute(query, (target_date,))
        results = cursor.fetchall()
        cursor.close()
        
        print(f"📊 Found {len(results)} click records for {target_date}")
        return results
    
    def analyze_daily_data(self, raw_data, target_date):
        """
        Analyze raw click data and generate summary statistics
        Returns: Dictionary with aggregated metrics
        """
        if not raw_data:
            return None
        
        # Initialize counters
        page_clicks = Counter()
        time_on_page_data = defaultdict(list)
        referrers = Counter()
        devices = Counter()
        sessions = set()
        
        # Process each click record
        for record in raw_data:
            page_name, tag, time_on_page, session_id, referrer, user_agent, timestamp = record
            
            # Count clicks per page
            page_clicks[page_name] += 1
            
            # Collect time on page data
            time_on_page_data[page_name].append(time_on_page)
            
            # Count referrers
            referrer_clean = referrer if referrer != 'direct' else 'Direct Traffic'
            referrers[referrer_clean] += 1
            
            # Basic device detection from user agent
            if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
                devices['Mobile'] += 1
            elif 'Tablet' in user_agent or 'iPad' in user_agent:
                devices['Tablet'] += 1
            else:
                devices['Desktop'] += 1
            
            # Track unique sessions
            sessions.add(session_id)
        
        # Calculate metrics
        total_clicks = len(raw_data)
        unique_sessions = len(sessions)
        
        # Calculate average time on page (overall)
        all_times = [record[2] for record in raw_data if record[2] > 0]  # Exclude 0-second visits
        avg_time_on_page = sum(all_times) / len(all_times) if all_times else 0
        
        # Prepare JSON data for storage
        device_split = dict(devices)
        top_referrers = dict(referrers.most_common(5))  # Top 5 referrers
        top_pages = dict(page_clicks.most_common(10))   # Top 10 pages
        
        summary = {
            'date': target_date,
            'project_name': 'lubobali_portfolio',  # Your project name
            'total_clicks': total_clicks,
            'unique_sessions': unique_sessions,
            'avg_time_on_page': round(avg_time_on_page, 2),
            'device_split': json.dumps(device_split),
            'top_referrers': json.dumps(top_referrers),
            'top_pages': json.dumps(top_pages),
            'repeat_visits': total_clicks - unique_sessions,  # Clicks minus unique sessions
            'tag': 'general'
        }
        
        return summary
    
    def save_daily_summary(self, summary_data):
        """
        Save aggregated data to daily_click_summary table
        Uses UPSERT to handle duplicate dates
        """
        cursor = self.connection.cursor()
        
        # UPSERT query - insert or update if date already exists
        query = """
        INSERT INTO daily_click_summary 
        (date, project_name, total_clicks, avg_time_on_page, device_split, top_referrers, top_pages, repeat_visits, tag, created_at)
        VALUES (%(date)s, %(project_name)s, %(total_clicks)s, %(avg_time_on_page)s, 
                %(device_split)s, %(top_referrers)s, %(top_pages)s, %(repeat_visits)s, %(tag)s, NOW())
        ON CONFLICT (date, project_name, tag) 
        DO UPDATE SET
            total_clicks = EXCLUDED.total_clicks,
            avg_time_on_page = EXCLUDED.avg_time_on_page,
            device_split = EXCLUDED.device_split,
            top_referrers = EXCLUDED.top_referrers,
            top_pages = EXCLUDED.top_pages,
            repeat_visits = EXCLUDED.repeat_visits,
            created_at = NOW();
        """
        
        try:
            cursor.execute(query, summary_data)
            self.connection.commit()
            print(f"✅ Daily summary saved for {summary_data['date']}")
        except Exception as e:
            self.connection.rollback()
            print(f"❌ Failed to save summary: {e}")
            raise
        finally:
            cursor.close()
    
    def process_date(self, target_date=None):
        """
        Main method to process data for a specific date
        If no date provided, processes yesterday's data
        """
        if target_date is None:
            target_date = date.today() - timedelta(days=1)  # Yesterday
        elif isinstance(target_date, str):
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        print(f"🔄 Processing analytics for {target_date}")
        
        # Get raw data
        raw_data = self.get_raw_data_for_date(target_date)
        
        if not raw_data:
            print(f"⚠️  No data found for {target_date}")
            return
        
        # Analyze data
        summary = self.analyze_daily_data(raw_data, target_date)
        
        if summary:
            # Save summary
            self.save_daily_summary(summary)
            print(f"📈 Summary: {summary['total_clicks']} clicks, {summary['unique_sessions']} sessions, {summary['avg_time_on_page']}s avg time")
        
        return summary

def main():
    """
    Main function - can be called directly or scheduled
    """
    # Check if we're in test mode
    import sys
    test_mode = '--test' in sys.argv
    
    if test_mode:
        print("🧪 Running in TEST MODE with mock data")
        test_with_mock_data()
        return
    
    aggregator = DailyAggregator()
    
    try:
        aggregator.connect_db()
        
        # Process yesterday's data by default
        # You can also specify a date: aggregator.process_date('2025-07-29')
        result = aggregator.process_date()
        
        if result:
            print("🎉 Daily aggregation completed successfully!")
        else:
            print("⚠️  No data to process")
            
    except Exception as e:
        print(f"💥 Error during aggregation: {e}")
    finally:
        aggregator.close_db()

def test_with_mock_data():
    """
    Test the aggregation logic with mock data
    """
    from datetime import datetime
    
    # Mock data similar to your actual database records
    mock_data = [
        ('home', 'general', 0, 'sess_1753752986484_3g4m3q54c', 'direct', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', datetime.now()),
        ('home', 'general', 183, 'sess_1753752986484_3g4m3q54c', 'direct', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', datetime.now()),
        ('/ibm', 'general', 8, 'sess_1753752986484_3g4m3q54c', 'direct', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', datetime.now()),
        ('/resume', 'general', 35, 'sess_other_session_123', 'https://linkedin.com', 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)', datetime.now()),
        ('/about-me', 'general', 510, 'sess_other_session_456', 'https://google.com', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', datetime.now()),
    ]
    
    # Create a mock aggregator to test the logic
    class MockAggregator(DailyAggregator):
        def __init__(self):
            pass  # Skip database connection
        
        def connect_db(self):
            pass
        
        def close_db(self):
            pass
    
    aggregator = MockAggregator()
    
    # Test the analysis logic
    from datetime import date
    today = date.today()
    
    print(f"📊 Testing analysis with {len(mock_data)} mock records")
    
    result = aggregator.analyze_daily_data(mock_data, today)
    
    if result:
        print("\n✅ Analysis Results:")
        print(f"📅 Date: {result['date']}")
        print(f"🔢 Total Clicks: {result['total_clicks']}")
        print(f"👥 Unique Sessions: {result['unique_sessions']}")
        print(f"⏱️  Average Time on Page: {result['avg_time_on_page']} seconds")
        print(f"🔄 Repeat Visits: {result['repeat_visits']}")
        print(f"📱 Device Split: {result['device_split']}")
        print(f"🔗 Top Referrers: {result['top_referrers']}")
        print(f"📄 Top Pages: {result['top_pages']}")
        
        print("\n🎉 Test completed successfully! The aggregation logic works.")
    else:
        print("❌ Test failed - no results generated")

if __name__ == "__main__":
    main()
