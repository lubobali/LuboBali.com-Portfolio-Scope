#!/bin/bash
# Script to run Streamlit dashboard with Railway database connection

export DATABASE_PUBLIC_URL="postgresql://postgres:vZDarOmyRiNkTEDOGjDkDVOWakMLxymj@yamabiko.proxy.rlwy.net:20282/railway"

source venv311/bin/activate
streamlit run dashboard.py
