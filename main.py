# main.py
import os
import requests
from scraper import scrape_linkedin_jobs
from formatter import format_jobs_email

# --- CONFIG ---
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
MAILGUN_DOMAIN  = os.environ.get("DOMAIN")

raw_recipients = os.environ.get("EMAIL")
if not raw_recipients:
    raise ValueError("EMAIL env var missing.")

RECIPIENTS = [email.strip() for email in raw_recipients.split(",")]

FROM_EMAIL = f"job-alert@{MAILGUN_DOMAIN}"

if not MAILGUN_API_KEY or not MAILGUN_DOMAIN or not RECIPIENTS:
    raise ValueError("Missing one or more required environment variables.")

# --- SCRAPE ---
jobs = scrape_linkedin_jobs(
    keywords="software engineering intern",
    location="Toronto, Ontario, Canada",
    time_range_hours=3600
)

if not jobs:
    print("No new jobs found.")
    exit(0)

# --- FORMAT EMAIL ---
email_data = format_jobs_email(jobs)
if not email_data:
    print("No valid jobs found after validation.")
    exit(0)

# --- SEND EMAIL via Mailgun ---
data = {
    "from": f"Job Alert <{FROM_EMAIL}>",
    "to": RECIPIENTS,        # <-- send to the whole list
    "subject": email_data.subject,
    "text": email_data.body_text,
    "html": email_data.body_html
}

response = requests.post(
    f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
    auth=("api", MAILGUN_API_KEY),
    data=data
)

if response.status_code == 200:
    print("Email sent successfully.")
else:
    print("Failed to send email:", response.status_code, response.text)
