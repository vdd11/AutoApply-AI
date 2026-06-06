from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

CORE_SKILLS = [
    "Python", "SQL", "Pandas", "NumPy", "Excel", "Tableau", "Power BI",
    "Statistics", "Machine Learning", "Data Visualization", "Dashboard", "ETL",
    "A/B Testing", "Regression", "Classification", "NLP", "APIs", "Git",
    "Streamlit", "Scikit-learn", "PostgreSQL", "BigQuery", "AWS", "Spark"
]

STOP = {"and", "the", "with", "for", "you", "our", "this", "that", "from", "will", "are", "data", "team", "role", "work", "job"}
WORD_RE = re.compile(r"[A-Za-z][A-Za-z+#.\-]{2,}")


def normalize_list(text: str | Iterable[str]) -> list[str]:
    if isinstance(text, str):
        parts = re.split(r",|\n|;", text)
    else:
        parts = list(text)
    return sorted({p.strip() for p in parts if str(p).strip()})


def keyword_hits(text: str, keywords: Iterable[str]) -> list[str]:
    lower = (text or "").lower()
    return sorted({kw for kw in keywords if kw and kw.lower() in lower})


def extract_job_keywords(description: str, limit: int = 35) -> list[str]:
    text = description or ""
    skill_hits = keyword_hits(text, CORE_SKILLS)
    words = [w.lower() for w in WORD_RE.findall(text) if w.lower() not in STOP and len(w) > 3]
    common = [w for w, _ in Counter(words).most_common(60)]
    out: list[str] = []
    for item in skill_hits + common:
        clean = item.strip()
        if clean and clean.lower() not in {x.lower() for x in out}:
            out.append(clean)
        if len(out) >= limit:
            break
    return out


def ats_keyword_coverage(job_description: str, resume_text: str, skills: str = "") -> dict:
    keywords = extract_job_keywords(job_description)
    resume_blob = f"{resume_text or ''} {skills or ''}".lower()
    present = [k for k in keywords if k.lower() in resume_blob]
    missing = [k for k in keywords if k.lower() not in resume_blob]
    coverage = round((len(present) / len(keywords) * 100), 1) if keywords else 0.0
    return {"coverage": coverage, "present": present, "missing": missing, "keywords": keywords}


def tailored_resume_bullets(job: dict, profile) -> list[str]:
    title = job.get("title", "this role")
    company = job.get("company", "the company")
    coverage = ats_keyword_coverage(job.get("description", ""), profile.raw_text, profile.skills)
    top = coverage["present"][:5] or normalize_list(profile.skills)[:5]
    missing = coverage["missing"][:3]
    bullets = [
        f"Built data-focused workflows using {', '.join(top[:3]) if top else 'Python and analytics'} to translate complex information into actionable insights.",
        f"Applied quantitative analysis, statistical reasoning, and technical communication skills to solve problems aligned with the {title} position at {company}.",
        f"Developed portfolio projects involving data ingestion, scoring, dashboarding, and recommendation logic to demonstrate practical data science readiness.",
    ]
    if missing:
        bullets.append(f"Targeted growth areas for this role include {', '.join(missing)}, based on the job description keyword gap.")
    return bullets


def interview_questions(job: dict) -> list[str]:
    title = job.get("title", "this role")
    company = job.get("company", "the company")
    return [
        f"Why are you interested in the {title} role at {company}?",
        "Walk me through a data project where you cleaned, analyzed, and communicated insights.",
        "How would you validate whether a dashboard metric is reliable?",
        "Describe a time you learned a technical tool quickly to solve a problem.",
        "How would you prioritize missing skills from a job description before an interview?",
    ]


def follow_up_message(job: dict, profile) -> str:
    return (
        f"Hello,\n\nI recently applied for the {job.get('title','role')} position at {job.get('company','your company')} "
        f"and wanted to express my continued interest. My background in {profile.skills.split(',')[0] if profile.skills else 'data analysis'}, "
        "quantitative problem-solving, and technical communication aligns well with the role. "
        "I would appreciate the opportunity to discuss how I can contribute to your team.\n\n"
        f"Best,\n{profile.name or 'Candidate'}"
    )
