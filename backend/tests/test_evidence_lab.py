from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import ChatResponse, SourceEvidence
from app.services.verification import verify_response, UNKNOWN
from app.services.comparison import compare_passages


def source(text="Employees receive 20 annual leave days per year.", **changes):
    return SourceEvidence(**dict(document_id="doc1", chunk_id="c1", filename="policy.txt",
                                 page=1, evidence=text, **changes))


@pytest.mark.parametrize("answer,expected", [
    ("Employees receive 20 annual leave days per year.", "answered"),
    ("Employees receive 90 annual leave days per year.", "not_found"),
    ("Employees receive 20 annual leave days per year. Employees receive stock options.", "answered"),
])
def test_verification_withholds_unsupported(answer, expected):
    response = verify_response(ChatResponse(status="answered", answer=answer, confidence="high", sources=[source()]))
    assert response.status == expected
    assert "stock options" not in response.answer
    if expected == "not_found":
        assert response.answer == UNKNOWN
        assert not response.sources


def test_empty_and_missing_metadata_fail_closed():
    for sources in ([], [source().model_copy(update={"document_id": ""})]):
        result = verify_response(ChatResponse(status="answered", answer=source().evidence, confidence="high", sources=sources))
        assert result.answer == UNKNOWN


def test_partial_and_contradicted_claims_are_withheld():
    for text, status in [("Employees receive 20 annual leave days per year and unlimited stock options.", "partially_supported"),
                         ("Employees receive 90 annual leave days per year.", "contradicted")]:
        result = verify_response(ChatResponse(status="answered", answer=text, confidence="high", sources=[source()]))
        assert result.answer == UNKNOWN
        assert result.claims[0].status == status


def test_policy_conflict_preserves_both_source_ids():
    right = source("Employees receive 25 annual leave days per year.").model_copy(update={"chunk_id": "c2", "document_id": "doc2"})
    result = verify_response(ChatResponse(status="answered", answer=source().evidence + "\n" + right.evidence,
                                         confidence="high", sources=[source(), right]))
    assert len(result.sources) == 2
    assert result.potential_conflicts[0]["left_chunk_id"] == "c1"
    assert result.potential_conflicts[0]["right_chunk_id"] == "c2"


def test_comparison():
    assert compare_passages([source()], [source()]) == []
    changes = compare_passages([source()], [source("Employees receive 25 annual leave days per year.")])
    assert changes[0]["kind"] == "modified"
    assert changes[0]["potential_conflict"]
    assert compare_passages([source()], [])[0]["kind"] == "removed"
    assert compare_passages([], [source()])[0]["kind"] == "added"
    unrelated = compare_passages([source()], [source("Satellite navigation uses orbital positioning systems.")])
    assert {c["kind"] for c in unrelated} == {"added", "removed"}


def test_real_policy_scenario(tmp_path, monkeypatch):
    from app.api import lab
    from app.core.config import settings
    monkeypatch.setattr(lab, "run_directory", lambda: tmp_path)
    monkeypatch.setattr(settings, "USE_MOCK_LLM", True)
    client = TestClient(app)
    ids = []
    try:
        for version in (2025, 2026):
            path = Path(__file__).parents[1] / "sample_documents" / f"Employee_Policy_{version}.txt"
            res = client.post("/api/documents/upload", files={"file": (path.name, path.read_bytes(), "text/plain")})
            assert res.status_code == 201, res.text
            ids.append(res.json()["document_id"])
        body = {"left_id": ids[0], "right_id": ids[1]}
        comparison = client.post("/api/compare", json=body)
        assert comparison.status_code == 200
        assert sum(c["kind"] == "modified" and "Employees" in c["before"]["evidence"] for c in comparison.json()["changes"]) == 2
        evaluation = client.post("/api/evaluations", json=body)
        assert evaluation.status_code == 200, evaluation.text
        run = evaluation.json()
        assert run["passed"] == 3, run
        assert len(client.get("/api/evaluations").json()["runs"]) == 1
        assert not client.get("/api/provider").json().get("api_key")
        assert client.post("/api/compare", json={"left_id": "missing", "right_id": ids[1]}).status_code == 404
    finally:
        for doc in ids:
            client.delete(f"/api/documents/{doc}")
