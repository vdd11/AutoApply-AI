from __future__ import annotations
from .database import connect, init_db

def create_alert(session_id: str, query: str, min_score: int = 80, frequency: str = 'daily') -> None:
    init_db(); conn=connect()
    conn.execute('''CREATE TABLE IF NOT EXISTS alerts(
        id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, query TEXT, min_score INTEGER,
        frequency TEXT, active INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.execute('INSERT INTO alerts(session_id,query,min_score,frequency) VALUES(?,?,?,?)',(session_id,query,min_score,frequency))
    conn.commit(); conn.close()

def list_alerts(session_id: str):
    init_db(); conn=connect(); rows=conn.execute('SELECT * FROM alerts WHERE session_id=? ORDER BY created_at DESC',(session_id,)).fetchall(); conn.close(); return [dict(r) for r in rows]
