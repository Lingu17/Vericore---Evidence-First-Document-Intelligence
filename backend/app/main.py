"""
DocuPilot FastAPI Main Application Entrypoint.
Provides RESTful APIs for evidence-first document intelligence, local embeddings, and grounded QA.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.access import workspace_access
from app.api import chat, documents, health, lab
from app.core.config import settings
from app.core.logging import logger
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes singletons and warms up local embedding model on startup."""
    if settings.ENV == "production" and not settings.WORKSPACE_PASSWORD:
        raise RuntimeError("Production requires WORKSPACE_PASSWORD for owner access.")
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

app.middleware("http")(workspace_access)

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
    logger.error(f"Unhandled server exception on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your request.",
            "detail": None
        }
    )

# Register routers
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(lab.router)


@app.get("/")
async def root():
    if static_path.is_dir():
        return FileResponse(static_path / "index.html")
    return {
        "app": "DocuPilot",
        "tagline": "Ask your documents. Verify every answer.",
        "status": "online",
        "documentation": "/docs"
    }


# Docker serves the existing React build and API from one origin.
static_path = Path(__file__).resolve().parent.parent / "static"
if static_path.is_dir():
    app.mount("/assets", StaticFiles(directory=static_path / "assets"), name="assets")

    @app.get("/app")
    async def workspace_page():
        return FileResponse(static_path / "index.html")

    @app.get("/{asset_name}", include_in_schema=False)
    async def static_file(asset_name: str):
        candidate = static_path / asset_name
        if candidate.is_file() and candidate.parent == static_path:
            return FileResponse(candidate)
        return JSONResponse({"detail": "Not found."}, status_code=404)
