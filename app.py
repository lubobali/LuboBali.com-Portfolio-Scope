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

# Create FastAPI app instance
app = FastAPI(
    title="Portfolio Click Tracker API",
    description="API to track clicks and user engagement on lubobali.com",
    version="1.0.0"
)

# Add CORS middleware to allow requests from Framer website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lubobali.com", "https://www.lubobali.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Startup event to create database tables
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    print("Starting up Portfolio Click Tracker API...")
    create_tables()
    print("API startup complete!")

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
        raise

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

# Run the application
if __name__ == "__main__":
    # Get port from environment variable (Railway sets this automatically)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


def test_connection():
    """Test database connection and print success message"""
    try:
        conn = get_db_connection()
        print("Database connection successful!")
        conn.close()
    except Exception as e:
        print(f"Database connection failed: {e}")