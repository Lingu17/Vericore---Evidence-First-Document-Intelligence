from types import SimpleNamespace
import pytest
from app.core.config import settings
from app.services.llm import GroqProvider, ProviderOutput, generate_cache_key
from app.services.verification import verify_response, UNKNOWN
from app.models.schemas import SourceEvidence


def evidence():
    return [SourceEvidence(document_id="doc", chunk_id="c1", filename="policy.txt", page=1,
                           evidence="Employees receive 20 annual leave days per year.",
                           similarity_score=0.9, semantic_score=0.8, coverage_score=1)]


def fake_client(payload=None, error=None):
    def create(**kwargs):
        if error:
            raise error
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=payload))])
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))


@pytest.mark.parametrize("payload", ["not json", '{"answer": "invented"}',
    '{"status":"answered","answer":"Employees receive 90 annual leave days per year.","source_ids":["c1"]}',
    '{"status":"answered","answer":"Employees receive 20 annual leave days per year.","source_ids":["fake"]}'])
def test_malformed_or_unsupported_output_never_presented(payload, monkeypatch):
    monkeypatch.setattr(settings, "USE_MOCK_LLM", False)
    provider = GroqProvider(api_key="test-key")
    provider.client = fake_client(payload)
    response = verify_response(provider.generate_answer("How many annual leave days?", evidence(), []))
    assert "invented" not in response.answer
    assert "90" not in response.answer
    assert all(s.chunk_id == "c1" for s in response.sources)


@pytest.mark.parametrize("error", [TimeoutError("secret-key"), PermissionError("secret-key")])
def test_provider_failures_are_sanitized_and_fallback_is_grounded(error, monkeypatch, caplog):
    monkeypatch.setattr(settings, "USE_MOCK_LLM", False)
    provider = GroqProvider(api_key="test-key")
    provider.client = fake_client(error=error)
    response = verify_response(provider.generate_answer("How many annual leave days?", evidence(), []))
    assert response.answer == evidence()[0].evidence
    assert "secret-key" not in caplog.text


def test_provider_environment_resolution_and_timeout(monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "environment-test-key")
    monkeypatch.setattr(settings, "GROQ_MODEL", "environment-model")
    monkeypatch.setattr(settings, "USE_MOCK_LLM", False)
    provider = GroqProvider()
    assert provider.api_key == "environment-test-key"
    assert provider.model == "environment-model"
    assert provider.client.timeout == settings.PROVIDER_TIMEOUT_SECONDS
    assert provider.client.max_retries == 0


def test_empty_provider_response_and_schema():
    provider = GroqProvider()
    assert verify_response(provider.generate_answer("Question?", [], [])).answer == UNKNOWN
    with pytest.raises(ValueError):
        ProviderOutput.model_validate({"status": "other", "answer": "something"})
    assert generate_cache_key("q", "doc1", ["a"]) != generate_cache_key("q", "doc2", ["a"])


def test_owner_key_validation_activation_and_clear(monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.api import lab
    monkeypatch.setattr(settings, "WORKSPACE_PASSWORD", "owner-test-password")
    fake = SimpleNamespace(models=SimpleNamespace(list=lambda: SimpleNamespace(data=[SimpleNamespace(id="test-model")])))
    import app.services.llm as llm_module
    monkeypatch.setattr(llm_module, "Groq", lambda **kwargs: fake)
    for attribute in ("api_key", "model", "client", "_answer_cache"):
        monkeypatch.setattr(lab.llm_service, attribute, getattr(lab.llm_service, attribute))
    client = TestClient(app)
    payload = {"api_key": "test-secret-never-return", "model": "test-model"}
    assert client.post("/api/provider", json=payload).status_code == 401
    auth = ("owner", "owner-test-password")
    tested = client.post("/api/provider/test", json=payload, auth=auth)
    assert tested.status_code == 200
    assert "test-secret-never-return" not in tested.text
    activated = client.post("/api/provider", json=payload, auth=auth)
    assert activated.status_code == 200
    assert activated.json()["configured"]
    assert "test-secret-never-return" not in activated.text
    assert lab.llm_service.api_key == "test-secret-never-return"
    assert client.delete("/api/provider", auth=auth).status_code == 200
    assert lab.llm_service.api_key == settings.GROQ_API_KEY


def test_key_errors_do_not_echo_secrets(monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.api import lab
    monkeypatch.setattr(settings, "WORKSPACE_PASSWORD", "owner-test-password")
    def fail(**kwargs):
        raise PermissionError("sensitive-key-in-provider-exception")
    import app.services.llm as llm_module
    monkeypatch.setattr(llm_module, "Groq", fail)
    client = TestClient(app)
    auth = ("owner", "owner-test-password")
    response = client.post("/api/provider/test", json={"api_key": "sensitive-key-in-provider-exception"}, auth=auth)
    assert response.status_code == 400
    assert "sensitive-key" not in response.text
    too_long = "SECRET" * 200
    response = client.post("/api/provider", json={"api_key": too_long}, auth=auth)
    assert response.status_code == 422
    assert too_long not in response.text


def test_key_entry_requires_owner_foundation(monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app
    monkeypatch.setattr(settings, "WORKSPACE_PASSWORD", "")
    response = TestClient(app).post("/api/provider/test", json={"api_key": "test-key"})
    assert response.status_code == 403
