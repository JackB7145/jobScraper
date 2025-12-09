# scraper.py
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin

LINKEDIN_BASE_URL = "https://www.linkedin.com"

def scrape_linkedin_jobs(
    keywords: str = "software engineering intern",
    location: str = "Canada",
    time_range_hours: int = 5400
) -> List[Dict[str, Optional[str]]]:
    """
    Scrape LinkedIn guest job postings via their /jobs-guest/jobs/api endpoint.
    Returns a list of dicts with keys: title, company, location, link, posted.
    """
    URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {
        "keywords": keywords,
        "f_TPR": f"r{time_range_hours}",
        "location": location
    }

    headers = {"User-Agent": "Mozilla/5.0"}  # Some LinkedIn pages block default requests

    resp = requests.get(URL, params=params, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch jobs. Status code: {resp.status_code}")
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
