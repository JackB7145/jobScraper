from pydantic import BaseModel, HttpUrl, constr
from typing import Optional, List
from datetime import datetime

class Job(BaseModel):
    title: constr(strip_whitespace=True, min_length=1)
    company: constr(strip_whitespace=True, min_length=1)
    link: HttpUrl
    location: Optional[str] = None
    posted: Optional[str] = None

class JobsEmailSchema(BaseModel):
    subject: str
    body_text: str
    body_html: str
    jobs: List[Job]
