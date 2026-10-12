from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core import accounts, access
from app.core.tenant import current_user
from app.services.llm import llm_service


def new_account(client):
    email = uuid4().hex + "@example.com"
    result = client.post("/api/auth/register", json={"email": email, "name": "Test", "password": "test-password-123"})
    assert result.status_code == 200, result.text
    return result.json()["user"], email


def connect(user):
    selection = current_user.set(user)
    try:
        llm_service.activate_credentials(None, "test-account-key", settings.GROQ_MODEL)
    finally:
        current_user.reset(selection)


def test_public_registration_session_setup_and_logout(monkeypatch):
    monkeypatch.setattr(settings, "PUBLIC_ACCOUNTS", True)
    monkeypatch.setattr(settings, "ENV", "production")
    access._requests.clear()
    client = TestClient(app, base_url="https://testserver")
    assert client.get("/api/documents").status_code == 401
    user, email = new_account(client)
    assert client.get("/api/auth/status").json()["user"]["email"] == email
    assert client.get("/api/documents").status_code == 428
    assert client.get("/app", follow_redirects=False).headers["location"] == "/setup"
    assert client.post("/api/provider", json={"api_key":"secret"}, headers={"Origin":"https://evil.example"}).status_code == 403
    connect(user)
    assert client.get("/api/documents").status_code == 200
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/documents").status_code == 401
    assert client.post("/api/auth/login", json={"username":email,"password":"wrong"}).status_code == 401
    login = client.post("/api/auth/login", json={"username":email,"password":"test-password-123"})
    assert login.status_code == 200
    assert "HttpOnly" in login.headers["set-cookie"] and "Secure" in login.headers["set-cookie"]
    with accounts.database() as db:
        stored = db.execute("SELECT password FROM users WHERE id=?", (user["id"],)).fetchone()[0]
    assert "test-password" not in stored


def test_user_documents_keys_and_evaluations_are_isolated(monkeypatch):
    monkeypatch.setattr(settings, "PUBLIC_ACCOUNTS", True)
    access._requests.clear()
    a, b = TestClient(app), TestClient(app)
    ua, _ = new_account(a)
    ub, _ = new_account(b)
    connect(ua)
    assert not b.get("/api/auth/status").json()["provider_configured"]
    connect(ub)
    assert a.post("/api/demo").status_code == 200
    docs = a.get("/api/documents").json()["documents"]
    assert len(docs) == 2
    assert b.get("/api/documents").json()["documents"] == []
    document_id = docs[0]["document_id"]
    assert b.get(f"/api/documents/{document_id}/passages").status_code == 404
    assert b.delete(f"/api/documents/{document_id}").status_code == 404
    assert b.post("/api/compare", json={"left_id":document_id,"right_id":docs[1]["document_id"]}).status_code == 404
    result = a.post("/api/evaluations",json={"left_id":document_id,"right_id":docs[1]["document_id"]})
    assert result.status_code == 200 and result.json()["passed"] == 3
    assert b.get("/api/evaluations").json()["runs"] == []
    assert b.delete("/api/documents").status_code == 200
    assert len(a.get("/api/documents").json()["documents"]) == 2
    assert b.delete("/api/provider").status_code == 200
    assert a.get("/api/provider").json()["configured"]
    assert not b.get("/api/provider").json()["configured"]


def test_google_state_and_config_guards(monkeypatch):
    monkeypatch.setattr(settings, "PUBLIC_ACCOUNTS", True)
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "")
    client = TestClient(app)
    assert client.get("/api/auth/google").status_code == 503
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "test-client")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "test-secret")
    response = client.get("/api/auth/google", follow_redirects=False)
    assert response.status_code == 303
    assert "code_challenge_method=S256" in response.headers["location"]
    assert "test-secret" not in response.headers["location"]
    failed = client.get("/api/auth/google/callback?state=wrong&code=invalid", follow_redirects=False)
    assert failed.headers["location"] == "/login?error=google"


def test_google_callback_exchange_creates_account_and_rejects_replay(monkeypatch):
    import httpx
    from urllib.parse import urlsplit, parse_qs
    monkeypatch.setattr(settings, "PUBLIC_ACCOUNTS", True)
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "test-client")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "test-secret")
    subject = uuid4().hex
    class GoogleClient:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def post(self, url, data):
            assert data["client_secret"] == "test-secret"
            assert data["code_verifier"]
            return httpx.Response(200, json={"access_token":"test-token"}, request=httpx.Request("POST",url))
        async def get(self, url, headers):
            assert headers["Authorization"] == "Bearer test-token"
            return httpx.Response(200, json={"sub":subject,"email":subject+"@example.com","email_verified":True,"name":"Google Test"}, request=httpx.Request("GET",url))
    monkeypatch.setattr("app.api.auth.httpx.AsyncClient", GoogleClient)
    client = TestClient(app)
    start = client.get("/api/auth/google", follow_redirects=False)
    state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]
    callback = "/api/auth/google/callback?state="+state+"&code=test-code"
    result = client.get(callback, follow_redirects=False)
    assert result.headers["location"] == "/setup"
    assert client.get("/api/auth/status").json()["user"]["name"] == "Google Test"
    assert client.get(callback, follow_redirects=False).headers["location"] == "/login?error=google"


