"""
Test database connection using the exact same method as app.py
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def test_connection():
    try:
        # Use the exact same method as app.py
        db_url = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
        print(f"🔍 Database URL found: {db_url[:50]}...{db_url[-20:] if len(db_url) > 70 else db_url}")
        
        if not db_url:
            print("❌ No database URL found in environment variables")
            return False
        
        print("🔄 Attempting connection...")
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        
        print("✅ Connection successful!")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM click_logs;")
        result = cursor.fetchone()
        print(f"📊 Found {result['count']} records in click_logs table")
        
        cursor.close()
        conn.close()
        print("🔌 Connection closed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing database connection (same method as app.py)")
    print("=" * 50)
    test_connection()
