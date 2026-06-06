from __future__ import annotations
import hashlib, secrets
from dataclasses import dataclass
from .database import connect, init_db

@dataclass
class User:
    user_id: str
    email: str
    name: str

def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 120_000).hex()

def ensure_auth_schema() -> None:
    init_db(); conn=connect()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password_hash TEXT,
        salt TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit(); conn.close()

def create_or_get_user(email: str, name: str = 'Candidate', password: str | None = None) -> User:
    ensure_auth_schema(); conn=connect()
    email=(email or 'demo@example.com').strip().lower()
    row=conn.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
    if row:
        conn.close(); return User(row['user_id'], row['email'], row['name'])
    user_id=hashlib.sha1((email+secrets.token_hex(8)).encode()).hexdigest()[:16]
    salt=secrets.token_hex(16)
    pw_hash=_hash_password(password, salt) if password else ''
    conn.execute('INSERT INTO users(user_id,email,name,password_hash,salt) VALUES(?,?,?,?,?)',(user_id,email,name or 'Candidate',pw_hash,salt))
    conn.commit(); conn.close()
    return User(user_id,email,name or 'Candidate')

def authenticate(email: str, password: str) -> User | None:
    ensure_auth_schema(); conn=connect()
    row=conn.execute('SELECT * FROM users WHERE email=?',((email or '').strip().lower(),)).fetchone(); conn.close()
    if not row or not row['password_hash']:
        return None
    return User(row['user_id'], row['email'], row['name']) if _hash_password(password,row['salt'])==row['password_hash'] else None
