"""Single-owner sign-in with short-lived HttpOnly sessions. No credential persistence."""
import hashlib
import secrets
from threading import Lock
from time import monotonic
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field
from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["Owner access"])
_sessions = {}
_lock = Lock()
COOKIE = "vericore_owner"
LIFETIME = 8 * 60 * 60


class Login(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=1000)


def session_valid(token):
    if not token:
        return False
    digest = hashlib.sha256(token.encode()).hexdigest()
    with _lock:
        return _sessions.get(digest, 0) > monotonic()


@router.get("/status")
def status():
    return {"required": bool(settings.WORKSPACE_PASSWORD), "workspace": "Single-owner workspace"}


@router.post("/login")
def login(credentials: Login, response: Response):
    if not settings.WORKSPACE_PASSWORD:
        raise HTTPException(400, "Owner authentication is disabled on this local workspace.")
    if not (secrets.compare_digest(credentials.username.encode(), settings.WORKSPACE_USERNAME.encode())
            and secrets.compare_digest(credentials.password.encode(), settings.WORKSPACE_PASSWORD.encode())):
        raise HTTPException(401, "Invalid workspace credentials.")
    token = secrets.token_urlsafe(32)
    now = monotonic()
    with _lock:
        for expired in [key for key, deadline in _sessions.items() if deadline <= now]:
            del _sessions[expired]
        _sessions[hashlib.sha256(token.encode()).hexdigest()] = now + LIFETIME
    response.set_cookie(COOKIE, token, max_age=LIFETIME, httponly=True,
                        secure=settings.ENV == "production", samesite="strict", path="/")
    return {"status": "signed_in"}


@router.post("/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get(COOKIE)
    if token:
        with _lock:
            _sessions.pop(hashlib.sha256(token.encode()).hexdigest(), None)
    response.delete_cookie(COOKIE, path="/")
    return {"status": "signed_out"}
