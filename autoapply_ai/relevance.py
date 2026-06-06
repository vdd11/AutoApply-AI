ALLOWED_TITLE_TERMS=["data analyst","data scientist","business analyst","bi analyst","business intelligence","analytics","research analyst","quantitative analyst","data engineer","machine learning","reporting analyst","insights analyst","education data"]
BLOCKED_TITLE_TERMS=["sales","account executive","recruiter","talent acquisition","customer support","customer success","nurse","therapist","attorney","lawyer","teacher","instructor","curriculum","marketing manager","product marketing","copywriter","bookkeeper","executive assistant"]
SENIOR_TERMS=["senior","staff","principal","lead","director","vp","head of","manager","10+ years","12+ years"]
DATA_SKILLS=["python","sql","pandas","numpy","excel","tableau","power bi","statistics","machine learning","dashboard","analytics","data visualization","regression","classification","etl","spark","airflow"]
def classify_job(title: str, description: str, allow_adjacent: bool=True):
    text=f"{title} {description}".lower(); flags=[]
    if any(t in title.lower() for t in BLOCKED_TITLE_TERMS): return "Unrelated", ["Blocked title category"]
    if any(t in text for t in SENIOR_TERMS): flags.append("May be too senior")
    title_ok=any(t in title.lower() for t in ALLOWED_TITLE_TERMS)
    hits=[s for s in DATA_SKILLS if s in text]
    if title_ok and hits: return "Data/Analytics", flags
    if allow_adjacent and len(hits)>=3 and any(x in text for x in ["analysis","research","report","dashboard","insight"]): return "Adjacent", flags
    return "Unrelated", flags or ["Insufficient data/analytics relevance"]
def build_queries(profile):
    skills=[s.strip().lower() for s in profile.skills.split(',') if s.strip()]
    base=["data analyst","junior data analyst","business intelligence analyst","research analyst","data scientist"]
    if "education" in profile.raw_text.lower() or "teaching" in profile.skills.lower(): base.append("education data analyst")
    tech=" ".join([s for s in ["python","sql","pandas","statistics"] if s in skills])
    return [f"{b} {tech}".strip() for b in base]
