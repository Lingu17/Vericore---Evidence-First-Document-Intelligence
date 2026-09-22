"""
DocuPilot FastAPI Main Application Entrypoint.
Provides RESTful APIs for evidence-first document intelligence, local embeddings, and grounded QA.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import chat, documents, health
from app.core.config import settings
from app.core.logging import logger
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes singletons and warms up local embedding model on startup."""
    logger.info("=" * 60)
    logger.info("DOCUPILOT: Evidence-First Document Intelligence")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"Embedding Model: {settings.EMBEDDING_MODEL}")
    logger.info(f"ChromaDB Path: {settings.CHROMA_PATH}")
    logger.info(f"Groq Model: {settings.GROQ_MODEL} (API Key: {'Configured' if settings.GROQ_API_KEY else 'Mock/Fallback'})")
    logger.info(f"Similarity Threshold: {settings.SIMILARITY_THRESHOLD}, Top-K: {settings.TOP_K}")

    # Eagerly initialize embedding model and vector store
    _ = embedding_service.model
    _ = vector_store_service.collection
    logger.info("DocuPilot backend services initialized and ready.")

    yield

    logger.info("Shutting down DocuPilot backend.")


app = FastAPI(
    title="DocuPilot API",
    description="Evidence-first document intelligence and grounded RAG workspace API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers for clean B2B JSON responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your request.",
            "detail": str(exc) if settings.ENV == "development" else None
        }
    )

# Register routers
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {
        "app": "DocuPilot",
        "tagline": "Ask your documents. Verify every answer.",
        "status": "online",
        "documentation": "/docs"
    }
