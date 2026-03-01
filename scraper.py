import requests
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

KEYWORDS = [
    "cloud", "engineer", "devops", "aws", "azure", "software", "developer",
    "backend", "frontend", "full stack", "python", "java", "react"
]

def is_relevant(title):
    title_lower = title.lower()
    return any(kw in title_lower for kw in KEYWORDS)

def make_id(title, company):
    raw = f"{title.lower().strip()}{company.lower().strip()}"
    return hashlib.md5(raw.encode()).hexdigest()

def extract_tags(title):
    tag_map = {
        "aws": "AWS", "azure": "Azure", "cloud": "Cloud",
        "devops": "DevOps", "python": "Python", "java": "Java",
        "react": "React", "backend": "Backend", "frontend": "Frontend",
        "engineer": "Engineering", "developer": "Development"
    }
    found = []
    t = title.lower()
    for key, label in tag_map.items():
        if key in t and label not in found:
            found.append(label)
    return found[:4] if found else ["IT", "Fresher"]

def scrape_newoffcampus():
    jobs = []
    try:
        r = requests.get("https://newoffcampusjobs.com/", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for card in soup.select("article.post")[:15]:
            title_el = card.select_one("h2.entry-title a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if not is_relevant(title):
                continue
            jobs.append({
                "id": make_id(title, "newoffcampus"),
                "title": title,
                "company": "Various",
                "location": "India",
                "salary": "As per company",
                "experience": "Fresher",
                "type": "Full Time",
                "source": "newoffcampusjobs.com",
                "link": title_el.get("href", "#"),
                "posted": "Today",
                "tags": extract_tags(title)
            })
    except Exception as e:
        print(f"Error scraping newoffcampusjobs: {e}")
    return jobs

def scrape_job4freshers():
    jobs = []
    try:
        r = requests.get("https://job4freshers.co.in/", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for card in soup.select("h2.entry-title")[:15]:
            a = card.select_one("a")
            if not a:
                continue
            title = a.get_text(strip=True)
            if not is_relevant(title):
                continue
            jobs.append({
                "id": make_id(title, "job4freshers"),
                "title": title,
                "company": "Various",
                "location": "India",
                "salary": "As per company",
                "experience": "Fresher",
                "type": "Full Time",
                "source": "job4freshers.co.in",
                "link": a.get("href", "#"),
                "posted": "Today",
                "tags": extract_tags(title)
            })
    except Exception as e:
        print(f"Error scraping job4freshers: {e}")
    return jobs

def deduplicate(all_jobs):
    seen = {}
    unique = []
    for job in all_jobs:
        if job["id"] not in seen:
            seen[job["id"]] = True
            unique.append(job)
    return unique

def run_all_scrapers():
    all_jobs = []
    scrapers = [scrape_newoffcampus, scrape_job4freshers]
    
    for scraper in scrapers:
        try:
            jobs = scraper()
            all_jobs.extend(jobs)
            print(f"✅ {scraper.__name__}: {len(jobs)} jobs found")
        except Exception as e:
            print(f"❌ {scraper.__name__} failed: {e}")
    
    unique_jobs = deduplicate(all_jobs)
    print(f"🎯 Total unique jobs: {len(unique_jobs)}")
    return unique_jobs
