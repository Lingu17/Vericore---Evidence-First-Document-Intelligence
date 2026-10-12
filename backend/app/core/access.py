"""Optional single-owner deployment boundary; does not claim multi-user isolation."""
import base64
import asyncio
import secrets
from collections import deque
from threading import Lock
from time import monotonic
from urllib.parse import urlsplit
from fastapi.responses import JSONResponse, RedirectResponse
from app.core.config import settings

_requests = {}
_lock = Lock()
_workspace_locks = {}


async def workspace_access(request, call_next):
    from app.api.auth import COOKIE, session_valid
    from app.core import accounts
    from app.core.tenant import current_user
    user = accounts.session_user(request.cookies.get("vericore_session")) if settings.PUBLIC_ACCOUNTS else None
    public_auth = request.url.path in {"/api/auth/login", "/api/auth/status", "/api/auth/register", "/api/auth/google", "/api/auth/google/callback"}
    if settings.PUBLIC_ACCOUNTS and not public_auth and request.url.path.startswith(("/api/", "/app", "/setup", "/docs", "/openapi")):
        if not user:
            if request.url.path in {"/app", "/setup"}:
                return RedirectResponse("/login", status_code=303)
            return JSONResponse({"detail": "Sign in to your account."}, status_code=401)
        selection = current_user.set(user)
        try:
            from app.services.llm import llm_service
            configured = bool(llm_service.api_key)
        finally:
            current_user.reset(selection)
        if not configured and request.url.path == "/app":
            return RedirectResponse("/setup", status_code=303)
        if not configured and request.url.path.startswith("/api/") and not request.url.path.startswith(("/api/provider", "/api/auth/")):
            return JSONResponse({"detail": "Connect your Groq API key first.", "setup_required": True}, status_code=428)
    if request.url.path.startswith(("/api/", "/app", "/docs", "/openapi")) and settings.WORKSPACE_PASSWORD and not settings.PUBLIC_ACCOUNTS and not public_auth:
        authorization = request.headers.get("authorization", "")
        try:
            scheme, encoded = authorization.split(" ", 1)
            username, password = base64.b64decode(encoded, validate=True).decode().split(":", 1)
            authorized = scheme.lower() == "basic" and secrets.compare_digest(username.encode(), settings.WORKSPACE_USERNAME.encode()) and secrets.compare_digest(password.encode(), settings.WORKSPACE_PASSWORD.encode())
        except (ValueError, UnicodeError):
            authorized = False
        authorized = authorized or session_valid(request.cookies.get(COOKIE))
        if not authorized:
            if request.url.path == "/app":
                return RedirectResponse("/login", status_code=303)
            return JSONResponse({"detail": "Workspace sign-in required."}, status_code=401)
    if request.url.path.startswith("/api/") and request.method in {"POST", "DELETE"}:
        # Local process protection. A production proxy should enforce distributed limits.
        key = request.client.host if request.client else "unknown"
        now = monotonic()
        with _lock:
            expired = [host for host, times in _requests.items() if not times or times[-1] < now - 60]
            for host in expired:
                del _requests[host]
            times = _requests.setdefault(key, deque())
            while times and times[0] < now - 60:
                times.popleft()
            if len(times) >= settings.REQUESTS_PER_MINUTE:
                return JSONResponse({"detail": "Too many requests. Retry in a minute."}, status_code=429,
                                    headers={"Retry-After": "60"})
            times.append(now)
    if request.method in {"POST", "DELETE"} and (request.cookies.get(COOKIE) or settings.PUBLIC_ACCOUNTS):
        # Prevent browser cross-origin submissions using an authenticated session.
        origin = request.headers.get("origin")
        same_host = origin and urlsplit(origin).netloc == request.headers.get("host")
        if origin and origin not in settings.CORS_ORIGINS and not same_host:
            return JSONResponse({"detail": "Cross-origin request rejected."}, status_code=403)
    selection = current_user.set(user)
    try:
        if user and request.url.path.startswith("/api/"):
            # Serialize account operations to avoid registry/provider races.
            workspace_lock = _workspace_locks.setdefault(user["id"], asyncio.Lock())
            async with workspace_lock:
                response = await call_next(request)
        else:
            response = await call_next(request)
    finally:
        current_user.reset(selection)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["X-Frame-Options"] = "DENY"
    return response
