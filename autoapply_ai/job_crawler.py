from __future__ import annotations

import hashlib
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .job_sources import HEADERS, _job, is_reasonably_relevant, dedupe_jobs
from .models import Job

TITLE_WORDS = re.compile(r"(data|analyst|analytics|scientist|machine learning|business intelligence|bi|research analyst|sql|python)", re.I)


def crawl_job_links(page_url: str, limit: int = 25, strict: bool = True) -> tuple[list[Job], list[str]]:
    """Lightweight portfolio-safe crawler for public job listing pages.

    It does not log in, bypass CAPTCHAs, or auto-apply. It only extracts visible job-like links.
    """
    errors: list[str] = []
    try:
        parsed = urlparse(page_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return [], ["Invalid URL. Use a full https:// job board or careers-page URL."]
        r = requests.get(page_url, headers=HEADERS, timeout=20)
        r.raise_for_status()
    except Exception as exc:
        return [], [f"Crawler failed: {exc}"]

    soup = BeautifulSoup(r.text, "html.parser")
    jobs: list[Job] = []
    for a in soup.find_all("a", href=True):
        text = " ".join(a.get_text(" ").split())
        href = urljoin(page_url, a["href"])
        if not text or len(text) < 6 or not TITLE_WORDS.search(text):
            continue
        context = " ".join(a.parent.get_text(" ").split()) if a.parent else text
        company = urlparse(page_url).netloc.replace("www.", "")
        job = _job("Careers Page", text[:180], company, "Remote/Unspecified", href, context[:3000])
        if is_reasonably_relevant(job, strict=strict):
            jobs.append(job)
        if len(jobs) >= limit * 2:
            break
    return dedupe_jobs(jobs)[:limit], errors
