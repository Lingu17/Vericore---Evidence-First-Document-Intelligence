from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


def test_owner_boundary_applies_to_evidence_and_changes(monkeypatch):
    monkeypatch.setattr(settings, "WORKSPACE_USERNAME", "owner")
    monkeypatch.setattr(settings, "WORKSPACE_PASSWORD", "test-password")
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    for path in ("/api/documents", "/api/evaluations", "/api/provider", "/docs"):
        assert client.get(path).status_code == 401
        assert client.get(path, auth=("owner", "wrong")).status_code == 401
    assert client.get("/api/documents", auth=("owner", "test-password")).status_code == 200
    assert client.post("/api/chat", json={"question": "Leave?"}).status_code == 401
    assert client.get("/api/documents", headers={"Authorization": "Basic !!!"}).status_code == 401


def test_request_limit(monkeypatch):
    from app.core import access
    access._requests.clear()
    monkeypatch.setattr(settings, "REQUESTS_PER_MINUTE", 1)
    client = TestClient(app)
    first = client.post("/api/chat", json={"question": ""})
    assert first.status_code == 422
    second = client.post("/api/chat", json={"question": ""})
    assert second.status_code == 429
    assert second.headers["retry-after"] == "60"
    access._requests.clear()


def test_size_limit_before_parsing(monkeypatch):
    monkeypatch.setattr(settings, "MAX_FILE_SIZE_MB", 0)
    response = TestClient(app).post("/api/documents/upload", files={"file": ("test.txt", b"oversized", "text/plain")})
    assert response.status_code == 413


def test_owner_session_is_private_revocable_and_rejects_cross_origin(monkeypatch):
    from app.core import access
    access._requests.clear()
    monkeypatch.setattr(settings, "WORKSPACE_PASSWORD", "test-password")
    monkeypatch.setattr(settings, "ENV", "production")
    client = TestClient(app, base_url="https://testserver")
    assert client.get("/api/auth/status").json()["required"]
    bad = client.post("/api/auth/login", json={"username": "owner", "password": "bad"})
    assert bad.status_code == 401
    login = client.post("/api/auth/login", json={"username": "owner", "password": "test-password"})
    assert login.status_code == 200
    assert "HttpOnly" in login.headers["set-cookie"]
    assert "Secure" in login.headers["set-cookie"]
    assert "test-password" not in login.text
    assert client.get("/api/documents").status_code == 200
    assert client.post("/api/chat", json={"question": "Leave?"}, headers={"Origin": "https://evil.example"}).status_code == 403
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/documents").status_code == 401
    access._requests.clear()
