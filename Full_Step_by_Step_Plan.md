✅ Full Step-by-Step Plan: Build Portfolio Analytics Pipeline
🌐 Your Setup
Website: lubobali.com (hosted on Framer)

Domain: Namecheap

API + Database: Railway

Dashboard: Streamlit Cloud

AI Assistants: GitHub Copilot + ChatGPT

Laptop: Mac with M1 chip + latest macOS

🔧 Local Dev Setup
✅ Install Python 3.10+

✅ Install pip & venv: brew install python

✅ Install PostgreSQL client: brew install libpq

✅ Install Git + GitHub CLI: brew install git gh

✅ Create a project folder:

bash
Copy
Edit
mkdir lubo-portfolio-tracker && cd lubo-portfolio-tracker
python3 -m venv venv && source venv/bin/activate
🧠 Step 1: Design the Database Schema
Table 1: click_logs (raw logs)
Column	Type
id	UUID / INT
timestamp	TIMESTAMP
page_name	TEXT
tag	TEXT
user_agent	TEXT
referrer	TEXT
session_id	TEXT
time_on_page	INT (sec)
ip_hash	TEXT

Table 2: daily_click_summary (aggregated)
Column	Type
date	DATE
project_name	TEXT
total_clicks	INT
avg_time_on_page	FLOAT
device_split	JSON
top_referrers	JSON
repeat_visits	INT
tag	TEXT

🛠️ Step 2: Build the Click Tracking API (FastAPI or Flask)
✅ Create app.py

✅ Create POST endpoint: /api/track-click

✅ Accept JSON body with:

json
Copy
Edit
{
  "page_name": "airbnb-project",
  "tag": "data-viz",
  "time_on_page": 33,
  "session_id": "uuid-123",
  "referrer": "https://linkedin.com",
  "user_agent": "...",
  "ip": "optional"
}
✅ Parse and insert into click_logs

💡 Use GitHub Copilot:

Write comments like # create API to log click and let Copilot suggest full code

🌐 Step 3: Deploy API to Railway
✅ Push code to GitHub repo

✅ Create Railway project → Add PostgreSQL plugin

✅ Set up environment variables in Railway:

DB_URL, PORT, etc.

✅ Deploy Flask/FastAPI app

✅ Get live endpoint:

arduino
Copy
Edit
https://your-api-name.up.railway.app/api/track-click
💻 Step 4: Add Tracking to Framer Website ✅ COMPLETED
✅ **Created comprehensive `tracker.js` script** with PortfolioTracker class

✅ **Embedded script directly in Framer** (using custom code, not CDN for reliability)

✅ **Auto-initialization** on every page load with:
```js
const tracker = new PortfolioTracker('https://lubo-portfolio-tracker-production.up.railway.app/api/track-click');
window.portfolioTracker = tracker;
```

✅ **Advanced tracking features implemented:**
- Session ID generation (`sess_${timestamp}_${random}`) stored in localStorage
- Accurate time tracking with `Date.now()` timestamps
- Multiple event listeners: `beforeunload`, `visibilitychange`, `blur`
- Page name extraction and sanitization from URL/title
- Automatic payload creation with all required fields
- Error handling and console logging for debugging
- `keepalive: true` for reliable data transmission during page unload

✅ **Real payload structure:**
```js
{
  page_name: "data_engineer_lubo",    // Auto-generated from URL/title
  tag: "general",                     // Configurable via setTag()
  time_on_page: 520,                  // Actual seconds spent
  session_id: "sess_1753752986484_3g4m3q54c",
  referrer: "https://linkedin.com",   // Real referrer data
  user_agent: "Mozilla/5.0...",       // Full browser info
  ip: null                            // Backend handles IP extraction
}
```

✅ **Verified working data flow:**
- 🌐 **Website**: lubobali.com → 🚀 **API**: Railway FastAPI → 🗄️ **Database**: PostgreSQL
- **33+ real tracking records** captured and stored
- **pgAdmin connection** established for data viewing
- **Live tracking** from real website visitors

✅ **Manual tracking capability:** `portfolioTracker.track()` for testing

**Key Implementation Files:**
- `tracker.js` - Complete tracking script (embedded in Framer)
- Framer custom code integration
- Railway endpoint: `https://lubo-portfolio-tracker-production.up.railway.app/api/track-click`

🔁 Step 5: Create Daily Batch Pipeline ✅ **COMPLETED**
✅ Create daily_aggregator.py

✅ Write SQL to:

Count clicks per project

Group by tag, referrer, device

Avg time on page

Identify repeat visits (same session_id or IP hash)

✅ Write results to daily_click_summary

✅ Schedule to run once every 24h:

✅ **Railway Cron Job Deployed** - `lubo-daily-analytics-cron` service LIVE

✅ **Automated daily processing** at midnight UTC (`0 0 * * *`)

✅ **Real data processed** - 118 clicks aggregated successfully

📊 Step 6: Build Dashboard in Streamlit
✅ Create dashboard.py

✅ Use psycopg2 or sqlalchemy to connect to Railway DB

✅ Query daily_click_summary

✅ Build visuals:

st.bar_chart() for top projects

st.dataframe() for raw logs

st.line_chart() for trends

Add date filters, device filters, referrer filters

✅ Push dashboard code to GitHub

🚀 Step 7: Deploy Streamlit Dashboard
✅ Go to streamlit.io/cloud

✅ Connect your GitHub repo

✅ Set environment secrets (DB connection string)

✅ Deploy and share your dashboard link publicly

🧠 Step 8: Analyze + Expand
Review which tags/projects perform best

Post LinkedIn insights like:
“90% of clicks last week came from LinkedIn on my ML projects”

Build new projects based on that demand

Add more metrics over time (scroll tracking, campaign source, etc.)

🔥 GitHub Copilot Tips
Use comment-driven development (# fetch top projects)

Let Copilot suggest SQL queries, Python scripts, and JS functions

Review and tweak the generated code

Use the $10 Pro plan if you want faster, better AI code completions and access to Copilot Chat

🎯 Final Outcome
Fully automated daily tracking system

Visual dashboard with clear insights

Reusable, scalable, and 100% yours

Real project you can show off in your portfolio + LinkedIn