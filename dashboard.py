"""
Portfolio Analytics Dashboard
Built with Streamlit - displays analytics data from lubobali.com
"""

import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime, date, timedelta

# Configure the page
st.set_page_config(
    page_title="Lubo's Portfolio Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection function
@st.cache_resource
def get_database_connection():
    """Create and cache database connection to Railway PostgreSQL"""
    try:
        # Get database URL from environment variable (same as your FastAPI app)
        db_url = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL") or os.getenv("DB_URL")
        
        # For local development, use the Railway database URL directly
        if not db_url:
            db_url = "postgresql://postgres:vZDarOmyRiNkTEDOGjDkDVOWakMLxymj@yamabiko.proxy.rlwy.net:20282/railway"
        
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

@st.cache_data(ttl=1)  # Cache for 1 second to force refresh
def load_daily_summary():
    """Load daily click summary data"""
    try:
        # Create a new connection each time (don't reuse cached connection)
        db_url = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL") or os.getenv("DB_URL")
        
        # For local development, use the Railway database URL directly
        if not db_url:
            db_url = "postgresql://postgres:vZDarOmyRiNkTEDOGjDkDVOWakMLxymj@yamabiko.proxy.rlwy.net:20282/railway"
        
        conn = psycopg2.connect(db_url)
        
        query = """
        SELECT date, project_name, total_clicks, repeat_visits, avg_time_on_page, 
               device_split, top_referrers, top_pages
        FROM daily_click_summary 
        ORDER BY date DESC, total_clicks DESC
        LIMIT 100
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def parse_json_column(df, column_name):
    """Parse JSON column safely"""
    try:
        if column_name in df.columns:
            return df[column_name].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
        return None
    except:
        return None

# Title and header
st.title("📊 Portfolio Analytics Dashboard")
st.markdown("**Real-time insights from lubobali.com**")

# Sidebar info
st.sidebar.markdown("### 🎯 Dashboard Info")
st.sidebar.markdown("- **Website**: lubobali.com")
st.sidebar.markdown("- **Data Source**: Railway PostgreSQL") 
st.sidebar.markdown("- **Updates**: Daily at midnight UTC")

# Database connection test
st.sidebar.markdown("### 🔌 Connection Status")
if st.sidebar.button("Test Database Connection"):
    conn = get_database_connection()
    if conn:
        st.sidebar.success("✅ Connected to Railway PostgreSQL")
        conn.close()
    else:
        st.sidebar.error("❌ Connection failed")

# Main dashboard content
st.markdown("---")

# Load and display data
with st.spinner("Loading analytics data..."):
    df = load_daily_summary()

if df is not None and not df.empty:
    st.success(f"📈 Loaded {len(df)} records from daily analytics")
    
    # Parse JSON columns
    top_pages_data = parse_json_column(df, 'top_pages')
    device_split_data = parse_json_column(df, 'device_split') 
    top_referrers_data = parse_json_column(df, 'top_referrers')
    
    # Basic metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_clicks = df['total_clicks'].sum()
        st.metric("Total Clicks", f"{total_clicks:,}")
    
    with col2:
        total_repeat_visits = df['repeat_visits'].sum()
        st.metric("Repeat Visits", f"{total_repeat_visits:,}")
    
    with col3:
        avg_time = df['avg_time_on_page'].mean()
        st.metric("Avg Time on Page", f"{avg_time:.1f}s")
    
    with col4:
        total_days = df['date'].nunique()
        st.metric("Days Tracked", total_days)
    
    st.markdown("---")
    
    # 📊 Interactive Charts Section
    st.markdown("## 📊 Interactive Analytics Dashboard")
    
    # Charts in two columns
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # 1. Top Pages Bar Chart
        if top_pages_data is not None and not top_pages_data.empty:
            st.markdown("### 🏆 Top Pages Performance")
            
            # Extract page data from the first (latest) record
            latest_pages = top_pages_data.iloc[0] if not top_pages_data.empty else {}
            
            if latest_pages:
                pages_df = pd.DataFrame([
                    {"Page": page, "Clicks": clicks} 
                    for page, clicks in latest_pages.items()
                ]).sort_values("Clicks", ascending=True)  # Sort for horizontal bar
                
                # Create horizontal bar chart
                fig_pages = px.bar(
                    pages_df, 
                    x="Clicks", 
                    y="Page",
                    orientation='h',
                    title="Page Clicks Distribution",
                    color="Clicks",
                    color_continuous_scale="viridis"
                )
                fig_pages.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_pages, use_container_width=True)
    
    with chart_col2:
        # 2. Device Split Pie Chart
        if device_split_data is not None and not device_split_data.empty:
            st.markdown("### 📱 Device Distribution")
            
            # Extract device data from the first (latest) record
            latest_devices = device_split_data.iloc[0] if not device_split_data.empty else {}
            
            if latest_devices:
                device_df = pd.DataFrame([
                    {"Device": device, "Users": count}
                    for device, count in latest_devices.items()
                ])
                
                # Create pie chart
                fig_devices = px.pie(
                    device_df,
                    values="Users",
                    names="Device", 
                    title="Desktop vs Mobile Traffic",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_devices.update_layout(height=400)
                st.plotly_chart(fig_devices, use_container_width=True)
    
    # Second row of charts
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        # 3. Traffic Sources (Referrers)
        if top_referrers_data is not None and not top_referrers_data.empty:
            st.markdown("### 🌐 Traffic Sources")
            
            # Extract referrer data from the first (latest) record
            latest_referrers = top_referrers_data.iloc[0] if not top_referrers_data.empty else {}
            
            if latest_referrers:
                referrers_df = pd.DataFrame([
                    {"Source": ref, "Visits": count}
                    for ref, count in latest_referrers.items()
                ]).sort_values("Visits", ascending=False)
                
                # Create bar chart
                fig_referrers = px.bar(
                    referrers_df,
                    x="Source",
                    y="Visits",
                    title="Top Traffic Sources",
                    color="Visits",
                    color_continuous_scale="blues"
                )
                fig_referrers.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig_referrers, use_container_width=True)
    
    with chart_col4:
        # 4. Engagement Metrics Gauge
        st.markdown("### ⏱️ Engagement Score")
        
        # Calculate engagement score based on time on page
        avg_time_score = min(avg_time / 60, 5)  # Max 5 minutes = 100%
        engagement_score = (avg_time_score / 5) * 100
        
        # Create gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = engagement_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Engagement Score (%)"},
            delta = {'reference': 70},  # Good benchmark
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}
        ))
        fig_gauge.update_layout(height=400)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    st.markdown("---")
    
    # Display raw data table
    st.markdown("### 📊 Recent Analytics Summary")
    st.dataframe(df.head(10), use_container_width=True)
        
else:
    st.warning("⚠️ No analytics data found. Please check your database connection and ensure the daily aggregator has run.")
    st.info("💡 **Next Steps:**\n1. Add your Railway database password above\n2. Ensure your daily aggregator has collected data\n3. Refresh this dashboard")
