from flask import Flask, jsonify
from flask_cors import CORS
from scraper import run_all_scrapers
from apscheduler.schedulers.background import BackgroundScheduler
import threading
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

job_cache = {"jobs": [], "last_updated": None}
cache_lock = threading.Lock()

def refresh_jobs():
    print("🔄 Refreshing job listings...")
    jobs = run_all_scrapers()
    with cache_lock:
        job_cache["jobs"] = jobs
        job_cache["last_updated"] = datetime.now().isoformat()
    print(f"✅ Cache updated: {len(jobs)} jobs")

@app.route("/")
def home():
    return jsonify({
        "status": "JobRadar Backend is running! 🎯",
        "endpoints": {
            "/api/jobs": "Get all jobs",
            "/api/health": "Health check",
            "/api/refresh": "Manually refresh jobs"
        }
    })

@app.route("/api/jobs")
def get_jobs():
    with cache_lock:
        return jsonify({
            "jobs": job_cache["jobs"],
            "total": len(job_cache["jobs"]),
            "last_updated": job_cache["last_updated"]
        })

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "jobs_cached": len(job_cache["jobs"]),
        "last_updated": job_cache["last_updated"]
    })

@app.route("/api/refresh")
def manual_refresh():
    threading.Thread(target=refresh_jobs).start()
    return jsonify({"message": "Refresh started in background"})

if __name__ == "__main__":
    # Run initial scrape
    refresh_jobs()
    
    # Schedule automatic refreshes every 6 hours
    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_jobs, "interval", hours=6)
    scheduler.start()
    
    # Get port from environment variable (Render provides this)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
```

**Commit all these files!**

---

### **Step 2: Sign Up on Render**

1. Go to **https://render.com**
2. Click **"Get Started"** or **"Sign Up"**
3. Choose **"Sign up with GitHub"**
4. Click **"Authorize Render"**

---

### **Step 3: Create New Web Service**

1. On Render dashboard, click the **"New +"** button (top right)
2. Select **"Web Service"**

---

### **Step 4: Connect Your GitHub Repository**

1. You'll see **"Connect a repository"**
2. Click **"Configure account"** (if needed)
3. Select your GitHub account
4. Grant access to your repositories
5. Find **`jobradar-backend`** in the list
6. Click **"Connect"**

---

### **Step 5: Configure Your Service**

Render will auto-fill most settings from your `render.yaml`, but verify:

| Field | Value |
|-------|-------|
| **Name** | `jobradar-backend` (or any name you like) |
| **Region** | Choose closest to you (e.g., Singapore, Oregon) |
| **Branch** | `main` (or `master`) |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT` |

---

### **Step 6: Choose Free Plan**

1. Scroll down to **"Instance Type"**
2. Select **"Free"** (it's at the bottom)
3. **Important**: Free tier spins down after 15 minutes of inactivity, but spins back up when accessed

---

### **Step 7: Deploy!**

1. Scroll to the bottom
2. Click the big blue **"Create Web Service"** button
3. ☕ Wait 2-5 minutes while Render:
   - Clones your repo
   - Installs Python packages
   - Runs your scraper
   - Deploys your API

---

### **Step 8: Monitor the Deployment**

You'll see a **live log** of the deployment:
```
==> Cloning from https://github.com/yourname/jobradar-backend...
==> Installing dependencies...
==> Running pip install -r requirements.txt
==> Starting application...
✅ scrape_newoffcampus: 12 jobs found
✅ scrape_job4freshers: 15 jobs found
🎯 Total unique jobs: 25
==> Service is live! 🎉
```

---

### **Step 9: Get Your Backend URL**

Once deployed, at the top of the page you'll see:
```
https://jobradar-backend-abc123.onrender.com
