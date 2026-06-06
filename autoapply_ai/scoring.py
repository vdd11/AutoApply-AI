from __future__ import annotations
import re
from typing import Iterable
from .relevance import classify_job, DATA_SKILLS
from .embeddings import semantic_similarity
from .quality import job_quality_score

WORD_RE=re.compile(r"[a-zA-Z][a-zA-Z+#.\-]{1,}")

CORE_MARKET_SKILLS = ["SQL","Python","Pandas","Excel","Tableau","Power BI","Statistics","Machine Learning","Dashboard","ETL","A/B testing","BigQuery","Snowflake","Looker","scikit-learn"]

def skill_hits(text: str, skills: Iterable[str]) -> list[str]:
    lower=text.lower(); return sorted({s for s in skills if s and s.lower() in lower})

def priority(score: float, classification: str, risks: list[str]) -> str:
    if classification=="Unrelated": return "Reject"
    if score>=88 and not risks: return "High"
    if score>=76: return "Medium"
    if score>=62: return "Low"
    return "Reject"

def score_job(job: dict, profile) -> dict:
    title=job.get("title",""); desc=job.get("description",""); text=f"{title} {desc} {job.get('location','')} {job.get('employment_type','')}"
    classification, risks=classify_job(title, desc)
    sim, sim_method = semantic_similarity(f"{profile.raw_text} {profile.skills} {profile.target_roles}", text)
    profile_skills=[s.strip() for s in profile.skills.split(',') if s.strip()]
    matched=skill_hits(text, profile_skills+DATA_SKILLS+CORE_MARKET_SKILLS)
    missing=[s for s in CORE_MARKET_SKILLS if s.lower() in text.lower() and s.lower() not in profile.skills.lower()]
    roles=[r.strip().lower() for r in profile.target_roles.split(',') if r.strip()]
    title_score=25 if any(r in title.lower() for r in roles) else 0
    keyword_score=min(len(matched)*4.5,32)
    semantic_score=sim*33
    base=20 if classification=="Data/Analytics" else 9 if classification=="Adjacent" else -35
    quality=job_quality_score(job)
    quality_component=(quality['job_quality_score']-50)*0.20
    score=base+title_score+keyword_score+semantic_score+quality_component
    if "remote" in f"{job.get('location','')} {desc}".lower(): score+=4
    if risks: score-=13*len(risks)
    if any(x in text.lower() for x in ["unpaid","commission only","volunteer"]):
        risks.append("Potential low-quality compensation signal"); score-=25
    score=round(max(0,min(100,score)),1)
    why=[]
    if matched: why.append("Matched skills: "+", ".join(matched[:10]))
    if title_score: why.append("Target role appears in title")
    why.append(f"Similarity: {sim:.2f} ({sim_method})")
    if quality['quality_flags']: why.append("Quality flags: "+quality['quality_flags'])
    return {
        "match_score":score,"priority":priority(score,classification,risks),"classification":classification,
        "why_match":" | ".join(why),"missing_skills":", ".join(sorted(set(missing))),"risk_flags":", ".join(sorted(set(risks))),
        "semantic_score":round(semantic_score,2),"keyword_score":round(keyword_score,2),"title_score":round(title_score,2),
        "job_quality_score":quality['job_quality_score'],"quality_flags":quality['quality_flags']
    }
