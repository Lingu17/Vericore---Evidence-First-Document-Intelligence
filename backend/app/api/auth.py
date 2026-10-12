"""Single-owner sign-in with short-lived HttpOnly sessions. No credential persistence."""
import hashlib
import secrets
from threading import Lock
from time import monotonic
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field
from app.core.config import settings
from app.core import accounts
from app.core.tenant import current_user
from fastapi.responses import RedirectResponse
import sqlite3
import re
import time
import httpx
from urllib.parse import urlencode

router = APIRouter(prefix="/api/auth", tags=["Owner access"])
_sessions = {}
_lock = Lock()
COOKIE = "vericore_owner"
LIFETIME = 8 * 60 * 60


class Login(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=1000)


class Registration(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    name: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=12, max_length=128, repr=False)


def public_user(response, user):
    response.set_cookie("vericore_session", accounts.create_session(user), max_age=LIFETIME,
                        httponly=True, secure=settings.ENV == "production", samesite="lax", path="/")
    return {"status": "signed_in", "user": user, "next": "/setup"}


@router.post("/register")
def register(credentials: Registration, response: Response):
    if not settings.PUBLIC_ACCOUNTS:
        raise HTTPException(404, "Registration unavailable.")
    email = credentials.email.strip().lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) or not credentials.name.strip():
        raise HTTPException(400, "Enter a valid email and name.")
    try:
        user = accounts.register(email, credentials.name.strip(), credentials.password)
    except sqlite3.IntegrityError:
        raise HTTPException(409, "An account already exists. Sign in instead.") from None
    return public_user(response, user)


def session_valid(token):
    if not token:
        return False
    digest = hashlib.sha256(token.encode()).hexdigest()
    with _lock:
        return _sessions.get(digest, 0) > monotonic()


@router.get("/status")
def status(request: Request):
    if settings.PUBLIC_ACCOUNTS:
        user = accounts.session_user(request.cookies.get("vericore_session"))
        configured = False
        if user:
            from app.services.llm import llm_service
            token = current_user.set(user)
            try:
                configured = bool(llm_service.api_key)
            finally:
                current_user.reset(token)
        return {"required": True, "public_accounts": True, "google_enabled": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
                "user": user, "provider_configured": configured}
    return {"required": bool(settings.WORKSPACE_PASSWORD), "public_accounts": False, "workspace": "Single-owner workspace"}


@router.post("/login")
def login(credentials: Login, response: Response):
    if settings.PUBLIC_ACCOUNTS:
        user = accounts.authenticate(credentials.username.strip().lower(), credentials.password)
        if not user:
            raise HTTPException(401, "Invalid email or password.")
        return public_user(response, user)
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
    accounts.revoke(request.cookies.get("vericore_session"))
    response.delete_cookie("vericore_session", path="/")
    token = request.cookies.get(COOKIE)
    if token:
        with _lock:
            _sessions.pop(hashlib.sha256(token.encode()).hexdigest(), None)
    response.delete_cookie(COOKIE, path="/")
    return {"status": "signed_out"}


_oauth = {}


@router.get("/google")
def google_start():
    if not settings.PUBLIC_ACCOUNTS or not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(503, "Google sign-in needs deployment credentials. Use email sign-in for now.")
    state, verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(64)
    import base64
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    with _lock:
        for old in [key for key, value in _oauth.items() if value[0] < time.time()]:
            del _oauth[old]
        _oauth[state] = (time.time() + 600, verifier)
    query = urlencode({"client_id": settings.GOOGLE_CLIENT_ID, "redirect_uri": settings.PUBLIC_BASE_URL.rstrip("/") + "/api/auth/google/callback",
                       "response_type": "code", "scope": "openid email profile", "state": state,
                       "code_challenge": challenge, "code_challenge_method": "S256", "prompt": "select_account"})
    response = RedirectResponse("https://accounts.google.com/o/oauth2/v2/auth?" + query, status_code=303)
    response.set_cookie("vericore_oauth", state, max_age=600, httponly=True, secure=settings.ENV == "production", samesite="lax", path="/api/auth")
    return response


@router.get("/google/callback")
async def google_callback(request: Request, state: str = "", code: str = ""):
    with _lock:
        pending = _oauth.pop(state, None)
    if not pending or pending[0] < time.time() or not secrets.compare_digest(state, request.cookies.get("vericore_oauth", "")) or not code:
        return RedirectResponse("/login?error=google", status_code=303)
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            exchange = await client.post("https://oauth2.googleapis.com/token", data={"client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET, "code": code, "code_verifier": pending[1],
                "grant_type": "authorization_code", "redirect_uri": settings.PUBLIC_BASE_URL.rstrip("/") + "/api/auth/google/callback"})
            exchange.raise_for_status()
            profile = await client.get("https://openidconnect.googleapis.com/v1/userinfo",
                                       headers={"Authorization": "Bearer " + exchange.json()["access_token"]})
            profile.raise_for_status()
            info = profile.json()
        if info.get("email_verified") is not True or not info.get("sub"):
            raise ValueError("Unverified account")
        user = accounts.google_account(info["sub"], info["email"].lower(), info.get("name", info["email"])[:80])
        response = RedirectResponse("/setup", status_code=303)
        public_user(response, user)
        response.delete_cookie("vericore_oauth", path="/api/auth")
        return response
    except Exception:
        return RedirectResponse("/login?error=google", status_code=303)
