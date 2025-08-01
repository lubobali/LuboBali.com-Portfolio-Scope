# FastAPI Click Tracking API for lubobali.com portfolio website
# Accepts click events and stores them in PostgreSQL database
# Deployed on Railway with PostgreSQL plugin

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import hashlib
from datetime import datetime
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import threading

# Create FastAPI app instance
app = FastAPI(
    title="Portfolio Click Tracker API",
    description="API to track clicks and user engagement on lubobali.com",
    version="1.0.0"
)

# Initialize scheduler
scheduler = AsyncIOScheduler()

# Add CORS middleware to allow requests from Framer website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Startup event to create database tables and start scheduler
@app.on_event("startup")
async def startup_event():
    """Initialize database tables and start scheduler on startup"""
    print("Starting up Portfolio Click Tracker API...")
    try:
        create_tables()
        print("API startup complete!")
        
        # Start the scheduler
        start_scheduler()
        print("✅ Daily aggregation scheduler started!")
        
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        print("API will start anyway - database may be created later")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown of scheduler"""
    print("Shutting down scheduler...")
    scheduler.shutdown()
    print("✅ Scheduler stopped")

def run_daily_aggregation():
    """Function to run daily aggregation (executed by scheduler)"""
    print(f"🕛 Starting scheduled daily aggregation at {datetime.now()}")
    try:
        # Import here to avoid circular imports
        from daily_aggregator import DailyAggregator
        
        # Run aggregation in a separate thread to avoid blocking
        def run_aggregation():
            try:
                aggregator = DailyAggregator()
                aggregator.run_daily_aggregation(days_back=1)
                print("✅ Scheduled aggregation completed successfully!")
            except Exception as e:
                print(f"❌ Scheduled aggregation failed: {e}")
        
        # Run in thread to avoid blocking the main event loop
        thread = threading.Thread(target=run_aggregation)
        thread.start()
        
    except Exception as e:
        print(f"❌ Error starting scheduled aggregation: {e}")

def start_scheduler():
    """Start the APScheduler for daily aggregation"""
    try:
        # Add the daily aggregation job
        # TESTING: Run at 01:29 UTC (5 minutes from now) for immediate test
        scheduler.add_job(
            run_daily_aggregation,
            CronTrigger(hour=1, minute=29, timezone='UTC'),
            id='daily_aggregation',
            name='Daily Analytics Aggregation',
            replace_existing=True
        )
        
        # Start the scheduler
        scheduler.start()
        print(f"📅 Scheduler configured to run daily at 01:29 UTC (TESTING - 5 min from now)")
        
    except Exception as e:
        print(f"❌ Failed to start scheduler: {e}")

# Define Pydantic model for incoming click data
class ClickEvent(BaseModel):
    page_name: str = Field(..., description="Name of the project/page being tracked")
    tag: Optional[str] = Field(None, description="Category tag for the project")
    time_on_page: int = Field(..., description="Time spent on page in seconds")
    session_id: str = Field(..., description="Unique session identifier")
    referrer: Optional[str] = Field(None, description="Source URL that led to this page")
    user_agent: str = Field(..., description="Browser user agent string")
    ip: Optional[str] = Field(None, description="Client IP address (optional)")

# Database connection function
def get_db_connection():
    """Create and return PostgreSQL database connection"""
    try:
        # Get database URL from environment variable (Railway provides this)
        db_url = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
        if not db_url:
            raise Exception("No database URL found in environment variables")
        
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Function to hash IP address for privacy
def hash_ip(ip_address: str) -> str:
    """Hash IP address using SHA256 for privacy"""
    if not ip_address:
        return None
    return hashlib.sha256(ip_address.encode()).hexdigest()[:16]

# Function to create database tables if they don't exist
def create_tables():
    """Create click_logs table if it doesn't exist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create click_logs table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS click_logs (
            id SERIAL PRIMARY KEY,
            page_name TEXT NOT NULL,
            tag TEXT,
            time_on_page INTEGER NOT NULL,
            session_id TEXT NOT NULL,
            referrer TEXT,
            user_agent TEXT NOT NULL,
            ip_hash TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✓ Database tables created/verified successfully")
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        # Don't raise - let the app start anyway

# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Portfolio Click Tracker API is running", "status": "healthy"}

# Main click tracking endpoint
@app.post("/api/track-click")
async def track_click(click_data: ClickEvent, request: Request):
    """
    Track a click event from the portfolio website
    Accepts JSON payload with page info and stores in database
    """
    try:
        # Get client IP from request if not provided
        client_ip = click_data.ip or request.client.host
        ip_hash = hash_ip(client_ip) if client_ip else None
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert click data into click_logs table
        insert_query = """
        INSERT INTO click_logs (
            page_name, tag, user_agent, referrer, 
            session_id, time_on_page, ip_hash
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, timestamp
        """
        
        cursor.execute(insert_query, (
            click_data.page_name,
            click_data.tag,
            click_data.user_agent,
            click_data.referrer,
            click_data.session_id,
            click_data.time_on_page,
            ip_hash
        ))
        
        # Get the inserted record details
        result = cursor.fetchone()
        
        # Commit transaction and close connection
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "Click tracked successfully",
            "click_id": result["id"],
            "timestamp": result["timestamp"].isoformat()
        }
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save click data")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Get recent clicks endpoint (for debugging/testing)
@app.get("/api/recent-clicks")
async def get_recent_clicks(limit: int = 10):
    """
    Get recent click events for debugging purposes
    Returns last N clicks from the database
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query recent clicks without exposing sensitive data
        query = """
        SELECT id, timestamp, page_name, tag, referrer, 
               time_on_page, session_id
        FROM click_logs 
        ORDER BY timestamp DESC 
        LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        clicks = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "clicks": clicks,
            "count": len(clicks)
        }
        
    except Exception as e:
        print(f"Error fetching clicks: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch click data")

# Manual aggregation trigger endpoint (for testing)
@app.post("/api/trigger-aggregation")
async def trigger_aggregation():
    """
    Manually trigger daily aggregation for testing purposes
    """
    try:
        print("🔧 Manual aggregation triggered via API")
        run_daily_aggregation()
        
        return {
            "success": True,
            "message": "Daily aggregation triggered successfully",
            "note": "Check logs for execution details"
        }
        
    except Exception as e:
        print(f"Error triggering aggregation: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger aggregation")

# Database test function
def test_connection():
    """Test database connection and print success message"""
    try:
        conn = get_db_connection()
        print("Database connection successful!")
        conn.close()
    except Exception as e:
        print(f"Database connection failed: {e}")