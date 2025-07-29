#!/usr/bin/env python3
"""
Test script to directly hit the tracking API
"""

import requests
import json
import time
from datetime import datetime

def test_tracking_api():
    """Test the tracking API endpoint directly"""
    
    api_url = "https://lubo-portfolio-tracker-production.up.railway.app/api/track-click"
    
    # Test payload
    test_data = {
        "page_name": "test_page_manual",
        "tag": "manual_test", 
        "time_on_page": 15,
        "session_id": f"test_session_{int(time.time())}",
        "referrer": "manual_test",
        "user_agent": "TestScript/1.0"
    }
    
    print(f"🚀 Testing API at: {api_url}")
    print(f"📊 Sending data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            api_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"📝 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("🎉 SUCCESS! Check pgAdmin for new record.")
        else:
            print("❌ FAILED! Check your API logs.")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_tracking_api()
