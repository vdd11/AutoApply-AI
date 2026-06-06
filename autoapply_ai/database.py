import sqlite3
from pathlib import Path
from .config import DB_PATH, DATA_DIR
SCHEMA = """
CREATE TABLE IF NOT EXISTS resumes (session_id TEXT PRIMARY KEY,name TEXT,email TEXT,raw_text TEXT,skills TEXT,target_roles TEXT,preferred_location TEXT,seniority TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY AUTOINCREMENT,source_job_id TEXT,title TEXT NOT NULL,company TEXT,location TEXT,source TEXT,url TEXT UNIQUE,description TEXT,employment_type TEXT,salary TEXT,date_posted TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS job_scores (id INTEGER PRIMARY KEY AUTOINCREMENT,job_id INTEGER NOT NULL,session_id TEXT NOT NULL,match_score REAL,priority TEXT,classification TEXT,why_match TEXT,missing_skills TEXT,risk_flags TEXT,semantic_score REAL,keyword_score REAL,title_score REAL,job_quality_score REAL DEFAULT 0,quality_flags TEXT DEFAULT '',created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,UNIQUE(job_id, session_id),FOREIGN KEY(job_id) REFERENCES jobs(id));
CREATE TABLE IF NOT EXISTS applications (id INTEGER PRIMARY KEY AUTOINCREMENT,job_id INTEGER NOT NULL,session_id TEXT NOT NULL,status TEXT DEFAULT 'Saved',notes TEXT DEFAULT '',updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,UNIQUE(job_id, session_id),FOREIGN KEY(job_id) REFERENCES jobs(id));
CREATE TABLE IF NOT EXISTS prep_packets (id INTEGER PRIMARY KEY AUTOINCREMENT,job_id INTEGER NOT NULL,session_id TEXT NOT NULL,content TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,UNIQUE(job_id, session_id));
CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY,email TEXT UNIQUE NOT NULL,name TEXT NOT NULL,password_hash TEXT,salt TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS saved_searches (id INTEGER PRIMARY KEY AUTOINCREMENT,session_id TEXT NOT NULL,query TEXT NOT NULL,sources TEXT,strict_mode INTEGER DEFAULT 1,min_score INTEGER DEFAULT 60,results_count INTEGER DEFAULT 0,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS alerts(id INTEGER PRIMARY KEY AUTOINCREMENT,session_id TEXT,query TEXT,min_score INTEGER DEFAULT 80,frequency TEXT DEFAULT 'daily',active INTEGER DEFAULT 1,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS job_events (id INTEGER PRIMARY KEY AUTOINCREMENT,job_id INTEGER NOT NULL,session_id TEXT NOT NULL,event_type TEXT NOT NULL,event_note TEXT DEFAULT '',created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
"""
def connect(db_path: Path = DB_PATH):
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
def init_db(db_path: Path = DB_PATH):
    conn = connect(db_path); conn.executescript(SCHEMA)
    # lightweight migrations for older local databases
    cols=[r['name'] for r in conn.execute('PRAGMA table_info(job_scores)').fetchall()]
    if 'job_quality_score' not in cols: conn.execute('ALTER TABLE job_scores ADD COLUMN job_quality_score REAL DEFAULT 0')
    if 'quality_flags' not in cols: conn.execute("ALTER TABLE job_scores ADD COLUMN quality_flags TEXT DEFAULT ''")
    conn.commit(); conn.close()
