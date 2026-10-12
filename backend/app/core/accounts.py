"""SQLite accounts and hashed session tokens. Provider secrets are not stored here."""
import hashlib
import secrets
import sqlite3
import time
from pathlib import Path
from contextlib import contextmanager
from app.core.config import settings


@contextmanager
def database():
    path = Path(settings.CHROMA_PATH) / "accounts.sqlite3"
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS users (
          id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
          password TEXT, google_sub TEXT UNIQUE);
        CREATE TABLE IF NOT EXISTS sessions (
          digest TEXT PRIMARY KEY, user_id TEXT NOT NULL, expires REAL NOT NULL);
    """)
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
    return salt + ":" + digest


def register(email, name, password):
    with database() as db:
        user_id = secrets.token_hex(16)
        db.execute("INSERT INTO users(id,email,name,password) VALUES(?,?,?,?)",
                   (user_id, email, name, password_hash(password)))
    return {"id": user_id, "email": email, "name": name}


def authenticate(email, password):
    with database() as db:
        row = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    # Perform comparable expensive work even for unknown accounts.
    stored = row["password"] if row and row["password"] else None
    computed = password_hash(password, stored.split(":")[0] if stored else None)
    if not stored or not secrets.compare_digest(stored, computed):
        return None
    return {key: row[key] for key in ("id", "email", "name")}


def google_account(sub, email, name):
    with database() as db:
        row = db.execute("SELECT * FROM users WHERE google_sub=?", (sub,)).fetchone()
        if not row:
            # Do not silently link a password account by matching email.
            if db.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
                raise ValueError("Use your existing email/password account.")
            user_id = secrets.token_hex(16)
            db.execute("INSERT INTO users(id,email,name,google_sub) VALUES(?,?,?,?)", (user_id, email, name, sub))
            return {"id": user_id, "email": email, "name": name}
        return {key: row[key] for key in ("id", "email", "name")}


def create_session(user):
    token = secrets.token_urlsafe(32)
    with database() as db:
        db.execute("DELETE FROM sessions WHERE expires<=?", (time.time(),))
        db.execute("INSERT INTO sessions VALUES(?,?,?)",
                   (hashlib.sha256(token.encode()).hexdigest(), user["id"], time.time() + 28800))
    return token


def session_user(token):
    if not token:
        return None
    with database() as db:
        row = db.execute("SELECT u.id,u.email,u.name FROM users u JOIN sessions s ON s.user_id=u.id WHERE s.digest=? AND s.expires>?",
                         (hashlib.sha256(token.encode()).hexdigest(), time.time())).fetchone()
    return dict(row) if row else None


def revoke(token):
    if token:
        with database() as db:
            db.execute("DELETE FROM sessions WHERE digest=?", (hashlib.sha256(token.encode()).hexdigest(),))
