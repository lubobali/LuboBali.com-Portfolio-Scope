#!/usr/bin/env python3
"""
Test script to verify database connection for the Portfolio Click Tracker API
Uses the same connection logic as app.py to ensure compatibility
"""

import sys
import os
from app import get_db_connection, test_connection

def main():
    """Main function to test database connection"""
    print("Testing database connection...")
    print("-" * 40)
    
    try:
        # Test using the existing test_connection function from app.py
        test_connection()
        
        # Additional detailed test
        print("\nPerforming detailed connection test...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"PostgreSQL version: {db_version[0]}")
        
        # Test if click_logs table exists
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'click_logs';
        """)
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✓ click_logs table exists")
            
            # Get table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'click_logs'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            print("\nTable structure:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} ({'nullable' if col['is_nullable'] == 'YES' else 'not null'})")
            
            # Count existing records
            cursor.execute("SELECT COUNT(*) FROM click_logs;")
            count = cursor.fetchone()
            print(f"\nExisting records in click_logs: {count[0]}")
            
        else:
            print("⚠ Warning: click_logs table does not exist")
            print("The table will be created automatically when the FastAPI app starts")
            print("You can also run the app once to create the table, or use schema.sql if available")
        
        cursor.close()
        conn.close()
        
        print("\n✓ All database tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def check_environment():
    """Check if required environment variables are set"""
    print("Checking environment variables...")
    print("-" * 40)
    
    db_url = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
    if db_url:
        # Don't print the full URL for security, just confirm it exists
        print("✓ Database URL found in environment")
        # Show just the database type from the URL
        if db_url.startswith('postgresql://') or db_url.startswith('postgres://'):
            print("✓ PostgreSQL connection string detected")
        else:
            print("⚠ Warning: Database URL doesn't appear to be PostgreSQL")
    else:
        print("✗ No DATABASE_URL or DB_URL found in environment variables")
        print("Make sure to set one of these environment variables with your PostgreSQL connection string")
        return False
    
    port = os.getenv("PORT", "8000")
    print(f"✓ Port: {port}")
    
    return True

if __name__ == "__main__":
    print("Portfolio Click Tracker - Database Connection Test")
    print("=" * 50)
    
    # Check environment first
    if not check_environment():
        print("\n✗ Environment check failed. Please fix environment variables before testing connection.")
        sys.exit(1)
    
    print()
    
    # Test database connection
    if main():
        print("\n🎉 Database connection test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Database connection test failed!")
        sys.exit(1)
