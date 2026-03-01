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
