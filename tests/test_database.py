from autoapply_ai.database import init_db, connect

def test_database_initializes():
    init_db(); conn=connect()
    tables=[r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    conn.close()
    assert 'jobs' in tables and 'resumes' in tables and 'job_scores' in tables
