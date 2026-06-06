from __future__ import annotations

import hashlib
import html
import re
from typing import List, Tuple

import requests

from .models import Job
from .relevance import classify_job

REMOTIVE_API = "https://remotive.com/api/remote-jobs"
ARBEITNOW_API = "https://www.arbeitnow.com/api/job-board-api"
REMOTEOK_API = "https://remoteok.com/api"

HEADERS = {
    "User-Agent": "AutoApplyAI/1.0 (+https://github.com/) job-search-portfolio-project",
    "Accept": "application/json,text/plain,*/*",
}


def clean_html(text: str) -> str:
    text = html.unescape(str(text or ""))
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def source_id(source: str, url: str, title: str, company: str) -> str:
    key = f"{source}|{url}|{title}|{company}".lower()
    return hashlib.sha1(key.encode()).hexdigest()[:16]


def _job(source: str, title: str, company: str, location: str, url: str, description: str,
         employment_type: str = "", salary: str = "", date_posted: str = "") -> Job:
    return Job(
        source_id(source, url, title, company),
        title.strip(),
        company.strip(),
        location.strip() or "Remote/Unspecified",
        source,
        url.strip(),
        clean_html(description),
        employment_type.strip(),
        salary.strip(),
        str(date_posted or ""),
    )


def is_reasonably_relevant(job: Job, strict: bool = True) -> bool:
    """Pre-filter obvious junk before it reaches scoring.

    Strict mode keeps Data/Analytics and strong Adjacent roles. Broad mode allows more adjacent roles.
    """
    classification, risks = classify_job(job.title, job.description)
    if classification == "Data/Analytics":
        return True
    if not strict and classification == "Adjacent" and len(risks) <= 1:
        return True
    return False


def dedupe_jobs(jobs: list[Job]) -> list[Job]:
    seen = set()
    out: list[Job] = []
    for job in jobs:
        key = (job.url or f"{job.title}|{job.company}").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(job)
    return out


def fetch_remotive_jobs(query: str, limit: int = 50) -> List[Job]:
    r = requests.get(REMOTIVE_API, params={"search": query}, headers=HEADERS, timeout=20)
    r.raise_for_status()
    jobs: list[Job] = []
    for item in r.json().get("jobs", [])[: max(limit * 2, limit)]:
        jobs.append(_job(
            "Remotive",
            item.get("title", ""),
            item.get("company_name", ""),
            item.get("candidate_required_location", "Remote"),
            item.get("url", ""),
            item.get("description", ""),
            item.get("job_type", ""),
            item.get("salary", "") or "",
            item.get("publication_date", ""),
        ))
    return jobs


def fetch_arbeitnow_jobs(query: str, limit: int = 50) -> List[Job]:
    r = requests.get(ARBEITNOW_API, headers=HEADERS, timeout=20)
    r.raise_for_status()
    out: list[Job] = []
    tokens = [t.lower() for t in query.split() if len(t) > 2]
    for item in r.json().get("data", []):
        text = f"{item.get('title','')} {item.get('description','')} {' '.join(item.get('tags',[]) or [])}".lower()
        if tokens and not any(tok in text for tok in tokens):
            continue
        out.append(_job(
            "Arbeitnow",
            item.get("title", ""),
            item.get("company_name", ""),
            ", ".join(item.get("location", []) or ["Remote/Unspecified"]),
            item.get("url", ""),
            item.get("description", ""),
            ", ".join(item.get("job_types", []) or []),
            "",
            item.get("created_at", ""),
        ))
        if len(out) >= limit * 2:
            break
    return out


def fetch_remoteok_jobs(query: str, limit: int = 50) -> List[Job]:
    r = requests.get(REMOTEOK_API, headers=HEADERS, timeout=20)
    r.raise_for_status()
    payload = r.json()
    out: list[Job] = []
    tokens = [t.lower() for t in query.split() if len(t) > 2]
    for item in payload:
        if not isinstance(item, dict) or not item.get("position"):
            continue
        tags = " ".join(item.get("tags", []) or [])
        text = f"{item.get('position','')} {item.get('description','')} {tags}".lower()
        if tokens and not any(tok in text for tok in tokens):
            continue
        out.append(_job(
            "RemoteOK",
            item.get("position", ""),
            item.get("company", ""),
            item.get("location", "Remote"),
            item.get("url", "") or item.get("apply_url", ""),
            f"{tags} {item.get('description','')}",
            ", ".join(item.get("tags", []) or []),
            item.get("salary", "") or "",
            item.get("date", ""),
        ))
        if len(out) >= limit * 2:
            break
    return out


def fetch_jobs(query: str, limit: int = 50, sources: list[str] | None = None, strict: bool = True) -> Tuple[list[Job], list[str]]:
    sources = sources or ["Remotive", "Arbeitnow", "RemoteOK"]
    jobs: list[Job] = []
    errors: list[str] = []
    fetchers = {
        "Remotive": fetch_remotive_jobs,
        "Arbeitnow": fetch_arbeitnow_jobs,
        "RemoteOK": fetch_remoteok_jobs,
    }
    for source in sources:
        fn = fetchers.get(source)
        if not fn:
            continue
        try:
            jobs.extend(fn(query, limit))
        except Exception as exc:  # API outages should not crash the dashboard.
            errors.append(f"{source} failed: {exc}")
    relevant = [job for job in dedupe_jobs(jobs) if is_reasonably_relevant(job, strict=strict)]
    return relevant[:limit], errors
