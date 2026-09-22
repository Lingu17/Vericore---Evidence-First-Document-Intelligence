"""Health and diagnostics endpoints for DocuPilot."""

from fastapi import APIRouter
from app.core.config import settings
from app.models.schemas import HealthResponse
from app.services.vector_store import vector_store_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Returns application health, loaded embedding model, and vector count."""
    doc_count = len(vector_store_service.get_all_documents())
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        embedding_model=settings.EMBEDDING_MODEL,
        llm_provider="Groq" if settings.GROQ_API_KEY else "Local Grounded Engine",
        vector_store_documents=doc_count
    )
