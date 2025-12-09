from bs4 import BeautifulSoup
from typing import Optional, List
from schemas import Job, JobsEmailSchema
from pydantic import ValidationError

def clean_html(raw: str) -> str:
    """Strip any HTML tags from a string."""
    return BeautifulSoup(raw or "", "html.parser").get_text(strip=True)

def format_jobs_email(jobs: List[dict]) -> Optional[JobsEmailSchema]:
    if not jobs:
        return None

    valid_jobs = []
    body_text = ""

    # Start HTML email with a professional header
    body_html = """
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin:0; padding:0;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 10px;">
            <h2 style="color: #2a7ae2; text-align:center;">New Software Engineering Intern Jobs</h2>
    """

    # Alternate card background colors
    colors = ["#ffffff", "#f9f9f9"]

    for idx, j in enumerate(jobs):
        j_clean = {
            "title": clean_html(j.get("title")),
            "company": clean_html(j.get("company")),
            "location": clean_html(j.get("location")),
            "link": j.get("link"),
            "posted": j.get("posted")
        }

        try:
            job_obj = Job(**j_clean)
        except ValidationError as e:
            print(f"Skipping invalid job: {j_clean}\nError: {e}")
            continue

        valid_jobs.append(job_obj)

        # Plain text fallback
        body_text += (
            f"Title: {job_obj.title}\n"
            f"Company: {job_obj.company}\n"
            f"Location: {job_obj.location}\n"
            f"Posted: {job_obj.posted}\n"
            f"Link: {job_obj.link}\n"
            "\n----------------------\n\n"
        )

        # HTML card with inline CSS and hover animation
        bg_color = colors[idx % len(colors)]
        body_html += f"""
        <div style="
            padding:15px; 
            margin-bottom:15px; 
            border-radius:8px; 
            background-color: {bg_color}; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        " onmouseover="this.style.transform='scale(1.02)'; this.style.boxShadow='0 4px 10px rgba(0,0,0,0.2)';" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 2px 5px rgba(0,0,0,0.1)';">
            <h3 style="margin:0; font-size:18px;">
                <a href="{job_obj.link}" style="text-decoration:none; color:#2a7ae2;">{job_obj.title}</a>
            </h3>
            <p style="margin:5px 0;"><strong>Company:</strong> {job_obj.company}</p>
            <p style="margin:5px 0;"><strong>Location:</strong> {job_obj.location or 'N/A'}</p>
            <p style="margin:5px 0;"><strong>Posted:</strong> {job_obj.posted or 'N/A'}</p>
            <a href="{job_obj.link}" style="display:inline-block; margin-top:10px; padding:8px 12px; background-color:#2a7ae2; color:#ffffff; border-radius:5px; text-decoration:none; font-size:14px;">View Job</a>
        </div>
        """

    body_html += """
        <p style="text-align:center; font-size:12px; color:#888;">You are receiving this email because you subscribed to job alerts.</p>
        </div>
    </body>
    </html>
    """

    if not valid_jobs:
        return None

    subject = f"{len(valid_jobs)} new software-engineering intern job(s)"
    return JobsEmailSchema(subject=subject, body_text=body_text, body_html=body_html, jobs=valid_jobs)
