-- Project: Portfolio Website Click Tracker (lubobali.com)
-- Goal: Track clicks, sessions, referrer sources, device info, time spent
-- Tables: click_logs (raw), daily_click_summary (aggregated)
-- Used for: Analytics dashboard built in Streamlit
-- Define click_logs table to store raw page tracking info from my portfolio
-- Needs: serial id, timestamp, page_name, tag, user_agent, referrer, session_id, time_on_page, ip_hash
CREATE TABLE click_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    page_name TEXT NOT NULL,
    tag TEXT,
    user_agent TEXT NOT NULL,
    referrer TEXT,
    session_id TEXT NOT NULL,
    time_on_page INT NOT NULL,
    ip_hash TEXT
);

-- Define daily_click_summary table for aggregated analytics data
-- Aggregates clicks by date and project for dashboard visualization
-- Includes device breakdown, top referrers, and repeat visitor metrics
CREATE TABLE daily_click_summary (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    project_name TEXT NOT NULL,
    total_clicks INT NOT NULL DEFAULT 0,
    avg_time_on_page FLOAT,
    device_split JSON,
    top_referrers JSON,
    repeat_visits INT NOT NULL DEFAULT 0,
    tag TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(date, project_name, tag)
);