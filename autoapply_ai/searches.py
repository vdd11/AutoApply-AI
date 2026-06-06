from __future__ import annotations

import pandas as pd
from .database import connect, init_db


def save_search(session_id: str, query: str, sources: str, strict: bool, min_score: int, results_count: int) -> None:
    init_db(); conn = connect()
    conn.execute(
        "INSERT INTO saved_searches(session_id, query, sources, strict_mode, min_score, results_count) VALUES(?,?,?,?,?,?)",
        (session_id, query, sources, int(strict), int(min_score), int(results_count)),
    )
    conn.commit(); conn.close()


def recent_searches(session_id: str, limit: int = 10) -> pd.DataFrame:
    init_db(); conn = connect()
    df = pd.read_sql_query(
        "SELECT * FROM saved_searches WHERE session_id=? ORDER BY created_at DESC LIMIT ?",
        conn,
        params=[session_id, limit],
    )
    conn.close(); return df
