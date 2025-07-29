"""
API-based Daily Aggregator for Portfolio Analytics
Uses the FastAPI endpoint to fetch data instead of direct database connection
"""

import requests
import json
from datetime import datetime, date, timedelta
from collections import defaultdict, Counter

class APIDailyAggregator:
    def __init__(self, api_base_url="https://lubo-portfolio-tracker-production.up.railway.app"):
        self.api_base_url = api_base_url
    
    def get_raw_data_via_api(self, target_date):
        """
        Get click data for a specific date via API call
        Note: We'll need to add a GET endpoint to your API for this
        For now, let's simulate with the test data we created
        """
        # Since we don't have a GET endpoint yet, let's use the test records we just created
        print(f"📊 Simulating data fetch for {target_date}")
        
        # Mock data based on what we know exists in your database
        mock_data = [
            {'page_name': 'home', 'tag': 'general', 'time_on_page': 0, 'session_id': 'sess_1753752986484_3g4m3q54c', 'referrer': 'direct', 'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', 'timestamp': '2025-07-29T16:00:00'},
            {'page_name': 'home', 'tag': 'general', 'time_on_page': 183, 'session_id': 'sess_1753752986484_3g4m3q54c', 'referrer': 'direct', 'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', 'timestamp': '2025-07-29T16:05:00'},
            {'page_name': '/ibm', 'tag': 'general', 'time_on_page': 8, 'session_id': 'sess_1753752986484_3g4m3q54c', 'referrer': 'direct', 'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', 'timestamp': '2025-07-29T16:10:00'},
            {'page_name': '/resume', 'tag': 'general', 'time_on_page': 35, 'session_id': 'sess_other_session_123', 'referrer': 'https://linkedin.com', 'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)', 'timestamp': '2025-07-29T16:15:00'},
            {'page_name': '/about-me', 'tag': 'general', 'time_on_page': 510, 'session_id': 'sess_other_session_456', 'referrer': 'https://google.com', 'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'timestamp': '2025-07-29T16:20:00'},
            {'page_name': 'test_connection', 'tag': 'test', 'time_on_page': 5, 'session_id': 'test_session_123', 'referrer': 'direct', 'user_agent': 'test_agent', 'timestamp': '2025-07-29T16:28:50'},
            {'page_name': 'wake_test_1', 'tag': 'test', 'time_on_page': 1, 'session_id': 'wake_session', 'referrer': 'direct', 'user_agent': 'wake_agent', 'timestamp': '2025-07-29T16:31:01'},
            {'page_name': 'wake_test_2', 'tag': 'test', 'time_on_page': 1, 'session_id': 'wake_session', 'referrer': 'direct', 'user_agent': 'wake_agent', 'timestamp': '2025-07-29T16:31:03'},
            {'page_name': 'wake_test_3', 'tag': 'test', 'time_on_page': 1, 'session_id': 'wake_session', 'referrer': 'direct', 'user_agent': 'wake_agent', 'timestamp': '2025-07-29T16:31:06'},
        ]
        
        print(f"📊 Found {len(mock_data)} click records for {target_date}")
        return mock_data
    
    def analyze_daily_data(self, raw_data, target_date):
        """
        Analyze raw click data and generate summary statistics
        """
        if not raw_data:
            return None
        
        # Initialize counters
        page_clicks = Counter()
        referrers = Counter()
        devices = Counter()
        sessions = set()
        
        # Process each click record
        for record in raw_data:
            page_name = record['page_name']
            time_on_page = record['time_on_page']
            session_id = record['session_id']
            referrer = record['referrer']
            user_agent = record['user_agent']
            
            # Count clicks per page
            page_clicks[page_name] += 1
            
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
        all_times = [record['time_on_page'] for record in raw_data if record['time_on_page'] > 0]
        avg_time_on_page = sum(all_times) / len(all_times) if all_times else 0
        
        # Prepare data
        device_split = dict(devices)
        top_referrers = dict(referrers.most_common(5))
        top_pages = dict(page_clicks.most_common(10))
        
        summary = {
            'date': str(target_date),
            'project_name': 'lubobali_portfolio',
            'total_clicks': total_clicks,
            'unique_sessions': unique_sessions,
            'avg_time_on_page': round(avg_time_on_page, 2),
            'device_split': device_split,
            'top_referrers': top_referrers,
            'top_pages': top_pages,
            'repeat_visits': total_clicks - unique_sessions,
            'tag': 'general'
        }
        
        return summary
    
    def process_date(self, target_date=None):
        """
        Process data for a specific date
        """
        if target_date is None:
            target_date = date.today()  # Use today since we have today's data
        elif isinstance(target_date, str):
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        print(f"🔄 Processing analytics for {target_date}")
        
        # Get raw data
        raw_data = self.get_raw_data_via_api(target_date)
        
        if not raw_data:
            print(f"⚠️  No data found for {target_date}")
            return None
        
        # Analyze data
        summary = self.analyze_daily_data(raw_data, target_date)
        
        if summary:
            print(f"📈 Summary: {summary['total_clicks']} clicks, {summary['unique_sessions']} sessions, {summary['avg_time_on_page']}s avg time")
        
        return summary

def main():
    print("🧪 API-based Daily Aggregator Test")
    print("=" * 50)
    
    aggregator = APIDailyAggregator()
    
    # Process today's data
    result = aggregator.process_date()
    
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
        
        print("\n🎉 API-based aggregation works! The logic is solid.")
        print("\n💡 Next step: Add a GET endpoint to your FastAPI to fetch real data")
    else:
        print("❌ No results generated")

if __name__ == "__main__":
    main()
