"""
Integration tests for DocuPilot REST APIs.
Tests end-to-end ingestion, deduplication, retrieval, grounded QA, and unknown-question handling.
"""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
SAMPLES_DIR = Path(__file__).resolve().parent.parent / "sample_documents"


@pytest.fixture(autouse=True)
def clean_database():
    """Wipes vector store before and after tests."""
    client.delete("/api/documents")
    yield
    client.delete("/api/documents")


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "embedding_model" in data


def test_document_upload_and_deduplication():
    pdf_path = SAMPLES_DIR / "NovaTech_Leave_Policy.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    # 1. Initial upload
    response1 = client.post(
        "/api/documents/upload",
        files={"file": ("NovaTech_Leave_Policy.pdf", file_bytes, "application/pdf")}
    )
    assert response1.status_code == 201
    data1 = response1.json()
    assert data1["status"] == "indexed"
    assert data1["pages"] == 2
    assert data1["chunks"] > 0
    assert len(data1["suggested_questions"]) >= 3
    doc_id = data1["document_id"]

    # 2. Duplicate upload test
    response2 = client.post(
        "/api/documents/upload",
        files={"file": ("NovaTech_Leave_Policy.pdf", file_bytes, "application/pdf")}
    )
    assert response2.status_code == 201
    data2 = response2.json()
    assert data2["status"] == "already_exists"
    assert data2["document_id"] == doc_id
    assert "already indexed" in data2["message"]


def test_grounded_question_answering():
    # Ingest leave policy
    pdf_path = SAMPLES_DIR / "NovaTech_Leave_Policy.pdf"
    with open(pdf_path, "rb") as f:
        client.post(
            "/api/documents/upload",
            files={"file": ("NovaTech_Leave_Policy.pdf", f.read(), "application/pdf")}
        )

    # Ingest handbook
    handbook_path = SAMPLES_DIR / "NovaTech_Employee_Handbook.pdf"
    with open(handbook_path, "rb") as f:
        client.post(
            "/api/documents/upload",
            files={"file": ("NovaTech_Employee_Handbook.pdf", f.read(), "application/pdf")}
        )

    # Query 1: Annual Leave
    res1 = client.post("/api/chat", json={"question": "How many annual leaves does an employee receive?"})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] == "answered"
    assert len(data1["sources"]) > 0
    assert "24" in data1["answer"] or "leave" in data1["answer"].lower()
    assert any("Leave_Policy" in s["filename"] for s in data1["sources"])

    # Query 2: Probation period
    res2 = client.post("/api/chat", json={"question": "What is the probation period?"})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] == "answered"
    assert any("Handbook" in s["filename"] for s in data2["sources"])


def test_unknown_question_anti_hallucination():
    # Ingest leave policy only
    pdf_path = SAMPLES_DIR / "NovaTech_Leave_Policy.pdf"
    with open(pdf_path, "rb") as f:
        client.post(
            "/api/documents/upload",
            files={"file": ("NovaTech_Leave_Policy.pdf", f.read(), "application/pdf")}
        )

    # Query unsupported topic: Company revenue
    res = client.post("/api/chat", json={"question": "What was NovaTech's revenue last year?"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "not_found"
    assert data["confidence"] == "low"
    assert len(data["sources"]) == 0
    assert "couldn't find" in data["answer"].lower() or "not found" in data["answer"].lower()


def test_empty_question_rejected():
    res = client.post("/api/chat", json={"question": "   "})
    assert res.status_code == 400
