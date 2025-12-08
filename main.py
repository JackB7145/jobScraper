import os
import requests
from bs4 import BeautifulSoup

# --- CONFIG (loaded from environment variables) ---
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
MAILGUN_DOMAIN  = os.environ.get("DOMAIN")
RECIPIENT       = os.environ.get("EMAIL")
FROM_EMAIL      = f"job-alert@{MAILGUN_DOMAIN}"

if not MAILGUN_API_KEY or not MAILGUN_DOMAIN or not RECIPIENT:
    raise ValueError("Missing one or more required environment variables.")

# --- SCRAPE ---
URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
params = {
    "keywords": "software engineering intern",
    "f_TPR": "r3600",
    "location": "Toronto, Ontario, Canada"
}

resp = requests.get(URL, params=params, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(resp.text, "html.parser")

jobs = []
for job in soup.select("li"):
    title   = job.select_one("h3")
    company = job.select_one("h4")
    loc     = job.select_one(".job-search-card__location")
    link    = job.select_one("a")
    date    = job.select_one("time")

    jobs.append({
        "title":   title.get_text(strip=True)   if title else None,
        "company": company.get_text(strip=True) if company else None,
        "location": loc.get_text(strip=True)    if loc else None,
        "link":    link["href"]                 if link else None,
        "posted":  date["datetime"]             if date else None
    })

if not jobs:
    print("No new jobs found.")
    exit(0)

# --- COMPOSE EMAIL ---
body = ""
for j in jobs:
    body += f"Title: {j['title']}\n"
    body += f"Company: {j['company']}\n"
    body += f"Location: {j['location']}\n"
    body += f"Posted: {j['posted']}\n"
    body += f"Link: {j['link']}\n"
    body += "\n----------------------\n\n"

data = {
    "from":    f"Job Alert <{FROM_EMAIL}>",
    "to":      [RECIPIENT],
    "subject": f"{len(jobs)} new software-engineering intern job(s)",
    "text":    body
}

# --- SEND EMAIL via Mailgun API ---
response = requests.post(
    f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
    auth=("api", MAILGUN_API_KEY),
    data=data
)

if response.status_code == 200:
    print("Email sent successfully.")
else:
    print("Failed to send email:", response.text)
