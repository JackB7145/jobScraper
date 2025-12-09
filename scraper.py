# scraper.py
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin

LINKEDIN_BASE_URL = "https://www.linkedin.com"

# Minimal geoId mapping for sanity. Add more if needed.
GEO_IDS = {
    "canada": "101174742",
    "toronto, ontario, canada": "102332259",
    "vancouver, british columbia, canada": "104994712",
    "montreal, quebec, canada": "106111837"
}

def resolve_geo_id(location: str) -> str:
    key = location.strip().lower()
    return GEO_IDS.get(key, GEO_IDS["canada"])


def scrape_linkedin_jobs(
    keywords: str = "software engineering intern",
    location: str = "Canada",
    time_range_hours: int = 5400
) -> List[Dict[str, Optional[str]]]:

    URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    geo_id = resolve_geo_id(location)

    params = {
        "keywords": keywords,
        "f_TPR": f"r{time_range_hours}",
        "location": location,
        "geoId": geo_id,
        "start": 0
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    resp = requests.get(URL, params=params, headers=headers)

    if resp.status_code != 200:
        print(f"[ERROR] HTTP {resp.status_code} — LinkedIn blocked the request.")
        return []

    if not resp.text.strip():
        print("[WARN] LinkedIn returned an empty response. "
              "Likely bad geoId or location string.")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []

    for job_li in soup.select("li"):
        title_el = job_li.select_one("h3")
        company_el = job_li.select_one("h4")
        loc_el = job_li.select_one(".job-search-card__location")
        link_el = job_li.select_one("a")
        date_el = job_li.select_one("time")

        link = link_el["href"] if link_el else None
        if link and link.startswith("/"):
            link = urljoin(LINKEDIN_BASE_URL, link)

        jobs.append({
            "title": title_el.get_text(strip=True) if title_el else None,
            "company": company_el.get_text(strip=True) if company_el else None,
            "location": loc_el.get_text(strip=True) if loc_el else None,
            "link": link,
            "posted": date_el["datetime"] if date_el else None
        })

    return jobs
