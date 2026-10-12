"""Additive comparison, source inspection, server provider status and evaluation APIs."""
import json
import os
from pathlib import Path
from time import perf_counter
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.core.config import settings
from app.models.schemas import SourceEvidence, ChatRequest
from app.api.chat import query_knowledge_base
from app.services.vector_store import vector_store_service as store
from app.services.comparison import compare_passages
from app.services.llm import llm_service
from app.api.documents import upload_document
from fastapi import UploadFile
from io import BytesIO

router = APIRouter(prefix="/api", tags=["Evidence Lab"])


@router.post("/demo")
async def load_demo():
    documents = []
    for version in (2025, 2026):
        path = settings.BASE_DIR / "sample_documents" / f"Employee_Policy_{version}.txt"
        result = await upload_document(UploadFile(filename=path.name, file=BytesIO(path.read_bytes())))
        documents.append(result)
    return {"documents": documents}


class Pair(BaseModel):
    left_id: str = Field(min_length=1, max_length=100)
    right_id: str = Field(min_length=1, max_length=100)


class ProviderCredentials(BaseModel):
    api_key: str = Field(min_length=1, max_length=1000, repr=False)
    model: str = Field(default=settings.GROQ_MODEL, min_length=1, max_length=100)


def validated_provider(credentials):
    if not settings.WORKSPACE_PASSWORD:
        raise HTTPException(403, "Enable owner authentication before submitting provider credentials.")
    try:
        return llm_service.validate_connection(credentials.api_key, credentials.model)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(400, "Groq connection could not be validated. Check the key or retry later.") from None


@router.post("/provider/test")
def test_provider(credentials: ProviderCredentials):
    validated_provider(credentials)
    return {"status": "connected", "provider": "Groq", "model": credentials.model}


@router.post("/provider")
def configure_provider(credentials: ProviderCredentials):
    client = validated_provider(credentials)
    # This is one authenticated owner workspace, not a per-user credential vault.
    # Runtime credentials are deliberately never written to disk or returned.
    llm_service.activate_credentials(client, credentials.api_key, credentials.model)
    return provider()


@router.delete("/provider")
def clear_runtime_provider():
    if not settings.WORKSPACE_PASSWORD:
        raise HTTPException(403, "Owner authentication is required.")
    llm_service.restore_environment()
    return provider()


def passages(document_id):
    if not store.get_document(document_id):
        raise HTTPException(404, "Document not found.")
    data = store.collection.get(where={"document_id": document_id}, include=["documents", "metadatas"])
    result = []
    for sid, text, meta in zip(data["ids"], data["documents"], data["metadatas"]):
        result.append(SourceEvidence(chunk_id=sid, document_id=document_id,
                      filename=meta["filename"], page=meta["page"],
                      section=meta.get("section"), evidence=text))
    return sorted(result, key=lambda s: (s.page, s.chunk_id))


@router.get("/documents/{document_id}/passages")
def get_passages(document_id: str):
    return {"passages": passages(document_id)}


@router.post("/compare")
def compare(pair: Pair):
    return {"changes": compare_passages(passages(pair.left_id), passages(pair.right_id)),
            "method": "original_passage_similarity"}


@router.get("/provider")
def provider():
    return {"provider": "Groq",
            "configured": bool(llm_service.api_key),
            "model": llm_service.model,
            "owner_configuration_enabled": bool(settings.WORKSPACE_PASSWORD),
            "mode": "local extraction" if settings.USE_MOCK_LLM or not llm_service.api_key else "Groq",
            "timeout_seconds": settings.PROVIDER_TIMEOUT_SECONDS,
            "credential_management": "Server environment or temporary owner configuration. Submitted keys stay in server memory and expire on restart. No per-user credential vault."}


def run_directory():
    path = Path(settings.CHROMA_PATH) / "evaluation_runs"
    path.mkdir(parents=True, exist_ok=True)
    return path


@router.get("/evaluations")
def evaluations():
    return {"runs": [json.loads(p.read_text(encoding="utf-8"))
                     for p in sorted(run_directory().glob("*.json"), reverse=True)]}


@router.post("/evaluations")
async def evaluate(pair: Pair):
    left, right = passages(pair.left_id), passages(pair.right_id)
    # Fixed questions and independently declared criteria for the included policy corpus.
    cases = [
        ("How many annual leave days do employees receive in each policy version?", ["20 annual leave days", "25 annual leave days"], False),
        ("How many remote work days per week are allowed in each policy version?", ["remotely 2 days", "remotely 3 days"], False),
        ("What is the employee stock option vesting schedule?", [], True),
    ]
    results = []
    expected_docs = {pair.left_id, pair.right_id}
    for question, criteria, unknown in cases:
        start = perf_counter()
        response = await query_knowledge_base(ChatRequest(question=question, document_ids=[pair.left_id, pair.right_id]))
        source_docs = {s.document_id for s in response.sources}
        relevant = [s for s in response.sources if s.document_id in expected_docs]
        supported = [c for c in response.claims if c.status == "supported"]
        expected_chunks = {s.chunk_id for s in left + right if any(value in s.evidence for value in criteria)}
        retrieved_chunks = set(response.retrieval_chunk_ids)
        passed = (response.status == "not_found" and response.answer == "Information not available in the uploaded documents.") if unknown else (
            response.status == "answered" and all(value in response.answer for value in criteria)
            and expected_docs.issubset(source_docs) and bool(response.potential_conflicts))
        results.append({"question": question, "expected_criteria": criteria, "must_refuse": unknown,
                        "must_flag_potential_conflict": not unknown,
                        "potential_conflict_detected": bool(response.potential_conflicts),
                        "passed": passed, "response": response.model_dump(mode="json"),
                        "latency_ms": round((perf_counter()-start)*1000, 2),
                        "retrieval_precision": len(retrieved_chunks & expected_chunks)/len(retrieved_chunks) if retrieved_chunks and not unknown else None,
                        "retrieval_recall": len(retrieved_chunks & expected_chunks)/len(expected_chunks) if expected_chunks else None,
                        "unknown_answer_correct": passed if unknown else None,
                        "citation_coverage": len(supported)/len(response.claims) if response.claims else None,
                        "unsupported_claim_rate": (len(response.claims)-len(supported))/len(response.claims) if response.claims else None,
                        "source_document_precision": len(relevant)/len(response.sources) if response.sources else None,
                        "source_document_recall": len(source_docs & expected_docs)/2 if not unknown else None})
    run = {"id": uuid4().hex, "created_at": datetime.now(timezone.utc).isoformat(),
           "dataset": "employee-policy-v1", "provider": provider(),
           "documents": [s.model_dump() for s in left + right], "results": results,
           "passed": sum(r["passed"] for r in results), "total": len(results),
           "usage_tokens": None, "cost": None}
    path = run_directory() / (run["created_at"].replace(":", "-") + "-" + run["id"] + ".json")
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(run, indent=2), encoding="utf-8")
    os.replace(temp, path)
    return run
