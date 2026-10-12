"""Optional single-owner deployment boundary; does not claim multi-user isolation."""
import base64
import secrets
from collections import deque
from threading import Lock
from time import monotonic
from urllib.parse import urlsplit
from fastapi.responses import JSONResponse, RedirectResponse
from app.core.config import settings

_requests = {}
_lock = Lock()


async def workspace_access(request, call_next):
    from app.api.auth import COOKIE, session_valid
    public_auth = request.url.path in {"/api/auth/login", "/api/auth/status"}
    if request.url.path.startswith(("/api/", "/app", "/docs", "/openapi")) and settings.WORKSPACE_PASSWORD and not public_auth:
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
            return JSONResponse({"detail": "Workspace sign-in required."}, status_code=401,
                                headers={"WWW-Authenticate": 'Basic realm="Vericore workspace", charset="UTF-8"'})
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
    if request.method in {"POST", "DELETE"} and request.cookies.get(COOKIE):
        # Prevent browser cross-origin submissions using an authenticated session.
        origin = request.headers.get("origin")
        same_host = origin and urlsplit(origin).netloc == request.headers.get("host")
        if origin and origin not in settings.CORS_ORIGINS and not same_host:
            return JSONResponse({"detail": "Cross-origin request rejected."}, status_code=403)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["X-Frame-Options"] = "DENY"
    return response
