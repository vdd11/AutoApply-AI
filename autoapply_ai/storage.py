from __future__ import annotations
import pandas as pd
from .database import connect, init_db
from .models import Job
from .scoring import score_job
def upsert_jobs(jobs: list[Job]) -> int:
    init_db(); conn=connect(); count=0
    for job in jobs:
        if not job.url: continue
        try:
            conn.execute("""INSERT INTO jobs(source_job_id,title,company,location,source,url,description,employment_type,salary,date_posted) VALUES(?,?,?,?,?,?,?,?,?,?)""",(job.source_job_id,job.title,job.company,job.location,job.source,job.url,job.description,job.employment_type,job.salary,job.date_posted)); count+=1
        except Exception: pass
    conn.commit(); conn.close(); return count
def score_all_jobs(profile, min_score: float=0) -> pd.DataFrame:
    init_db(); conn=connect(); jobs=pd.read_sql_query("SELECT * FROM jobs",conn)
    for _,row in jobs.iterrows():
        r=score_job(row.to_dict(),profile)
        conn.execute("""INSERT INTO job_scores(job_id,session_id,match_score,priority,classification,why_match,missing_skills,risk_flags,semantic_score,keyword_score,title_score,job_quality_score,quality_flags) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(job_id, session_id) DO UPDATE SET match_score=excluded.match_score,priority=excluded.priority,classification=excluded.classification,why_match=excluded.why_match,missing_skills=excluded.missing_skills,risk_flags=excluded.risk_flags,semantic_score=excluded.semantic_score,keyword_score=excluded.keyword_score,title_score=excluded.title_score,job_quality_score=excluded.job_quality_score,quality_flags=excluded.quality_flags,created_at=CURRENT_TIMESTAMP""",(int(row['id']),profile.session_id,r['match_score'],r['priority'],r['classification'],r['why_match'],r['missing_skills'],r['risk_flags'],r['semantic_score'],r['keyword_score'],r['title_score'],r.get('job_quality_score',0),r.get('quality_flags','')))
        conn.execute("INSERT OR IGNORE INTO applications(job_id,session_id,status) VALUES(?,?,?)",(int(row['id']),profile.session_id,'Saved'))
    conn.commit(); conn.close(); return ranked_jobs(profile.session_id,min_score=min_score)
def ranked_jobs(session_id: str, min_score: float=0, include_rejects: bool=False) -> pd.DataFrame:
    init_db(); conn=connect(); q="""SELECT j.*,s.match_score,s.priority,s.classification,s.why_match,s.missing_skills,s.risk_flags,s.semantic_score,s.keyword_score,s.title_score,COALESCE(a.status,'Saved') as status,COALESCE(a.notes,'') as notes FROM jobs j JOIN job_scores s ON j.id=s.job_id LEFT JOIN applications a ON a.job_id=j.id AND a.session_id=s.session_id WHERE s.session_id=? AND s.match_score>=?"""; params=[session_id,min_score]
    if not include_rejects: q += " AND s.priority != 'Reject' AND s.classification != 'Unrelated'"
    q += " ORDER BY s.match_score DESC,j.created_at DESC"
    df=pd.read_sql_query(q,conn,params=params); conn.close(); return df
def update_status(session_id: str, job_id: int, status: str, notes: str=""):
    init_db(); conn=connect(); conn.execute("""INSERT INTO applications(job_id,session_id,status,notes,updated_at) VALUES(?,?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(job_id,session_id) DO UPDATE SET status=excluded.status,notes=excluded.notes,updated_at=CURRENT_TIMESTAMP""",(job_id,session_id,status,notes)); conn.commit(); conn.close()

def record_event(session_id: str, job_id: int, event_type: str, note: str = ""):
    init_db(); conn=connect()
    conn.execute("INSERT INTO job_events(job_id,session_id,event_type,event_note) VALUES(?,?,?,?)",(job_id,session_id,event_type,note))
    conn.commit(); conn.close()

def mark_apply_opened(session_id: str, job_id: int):
    update_status(session_id, job_id, "Viewed")
    record_event(session_id, job_id, "apply_link_opened")
