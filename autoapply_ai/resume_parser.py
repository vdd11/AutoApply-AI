from __future__ import annotations
import re
from pathlib import Path
from typing import Iterable
COMMON_SKILLS = ["python","sql","pandas","numpy","scikit-learn","machine learning","statistics","data visualization","matplotlib","plotly","tableau","power bi","excel","dashboard","streamlit","airflow","etl","aws","azure","gcp","postgresql","mysql","sqlite","spark","nlp","regression","classification","a/b testing","hypothesis testing","research","physics","mathematics","teaching","communication"]
def extract_text_from_pdf(path: str | Path) -> str:
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)
def extract_text_from_upload(uploaded_file) -> str:
    name = getattr(uploaded_file, "name", "uploaded_resume")
    data = uploaded_file.read()
    if name.lower().endswith(".pdf"):
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(data); tmp_path = tmp.name
        return extract_text_from_pdf(tmp_path)
    return data.decode("utf-8", errors="ignore")
def extract_email(text: str) -> str:
    m = re.search(r"[\w.\-+]+@[\w\-]+\.[\w.\-]+", text); return m.group(0) if m else ""
def extract_name(text: str) -> str:
    lines=[ln.strip() for ln in text.splitlines() if ln.strip()]
    for ln in lines[:8]:
        if len(ln.split()) in (2,3) and not any(x in ln.lower() for x in ["resume","email","linkedin","github"]): return ln[:80]
    return "Candidate"
def extract_skills(text: str, skills: Iterable[str] = COMMON_SKILLS) -> list[str]:
    lower=text.lower(); return sorted({s for s in skills if s.lower() in lower})
def build_profile_from_text(session_id: str, text: str, target_roles: str, location: str, seniority: str):
    from .models import ResumeProfile
    return ResumeProfile(session_id=session_id,name=extract_name(text),email=extract_email(text),raw_text=text,skills=", ".join(extract_skills(text)),target_roles=target_roles,preferred_location=location,seniority=seniority)
