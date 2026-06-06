from .database import connect, init_db
from .models import ResumeProfile
from .config import DEMO_SESSION_ID
DEFAULT_PROFILE = ResumeProfile(session_id=DEMO_SESSION_ID,name="Vishal Desai",email="pullsquad11@gmail.com",raw_text="Applied Physics M.S. with Python, Pandas, NumPy, statistics, machine learning, research, tutoring, dashboards, recommender systems, and data visualization experience.",skills="Python, Pandas, NumPy, Matplotlib, SciPy, statistics, data visualization, machine learning, SQL, Streamlit, research, physics, mathematics, teaching, communication",target_roles="Data Analyst, Data Scientist, Business Intelligence Analyst, Education Data Analyst, Research Analyst",preferred_location="Remote",seniority="Entry-Level / Junior")
def save_profile(profile: ResumeProfile):
    init_db(); conn=connect()
    conn.execute("""INSERT INTO resumes(session_id,name,email,raw_text,skills,target_roles,preferred_location,seniority,updated_at) VALUES(?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(session_id) DO UPDATE SET name=excluded.name,email=excluded.email,raw_text=excluded.raw_text,skills=excluded.skills,target_roles=excluded.target_roles,preferred_location=excluded.preferred_location,seniority=excluded.seniority,updated_at=CURRENT_TIMESTAMP""", (profile.session_id,profile.name,profile.email,profile.raw_text,profile.skills,profile.target_roles,profile.preferred_location,profile.seniority))
    conn.commit(); conn.close()
def load_profile(session_id: str = DEMO_SESSION_ID) -> ResumeProfile:
    init_db(); conn=connect(); row=conn.execute("SELECT * FROM resumes WHERE session_id=?",(session_id,)).fetchone(); conn.close()
    if not row:
        save_profile(DEFAULT_PROFILE if session_id==DEMO_SESSION_ID else ResumeProfile(session_id=session_id)); return load_profile(session_id)
    keys=["session_id","name","email","raw_text","skills","target_roles","preferred_location","seniority"]
    return ResumeProfile(**{k: row[k] for k in keys})

def list_profiles():
    init_db(); conn=connect()
    rows=conn.execute("SELECT session_id,name,email,target_roles,updated_at FROM resumes ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]
