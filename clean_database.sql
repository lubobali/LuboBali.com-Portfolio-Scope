-- Clean Database Script
-- This will delete ALL existing data and start fresh
-- Only run this if you want to completely reset your analytics data

-- Delete all existing click logs
DELETE FROM click_logs;

-- Reset the auto-increment counter to start from 1
ALTER SEQUENCE click_logs_id_seq RESTART WITH 1;

-- Verify the table is empty
SELECT COUNT(*) as total_records FROM click_logs;
