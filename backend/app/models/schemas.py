"""
Pydantic Schemas for DocuPilot REST API & Internal domain models.
Enforces strict typing and validation across ingestion, retrieval, and chat.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    INDEXED = "indexed"
    PROCESSING = "processing"
    FAILED = "failed"
    ALREADY_EXISTS = "already_exists"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ChatStatus(str, Enum):
    ANSWERED = "answered"
    NOT_FOUND = "not_found"


# -------------------------------------------------------------
# Document & Ingestion Schemas
# -------------------------------------------------------------

class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page: int
    section: Optional[str] = "General"
    text: str
    token_count: Optional[int] = None


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_hash: str
    page_count: int
    chunk_count: int
    status: DocumentStatus = DocumentStatus.INDEXED
    created_at: str
    suggested_questions: list[str] = Field(default_factory=list)


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    pages: int
    chunks: int
    status: str
    message: Optional[str] = None
    suggested_questions: list[str] = Field(default_factory=list)


class DocumentDetail(BaseModel):
    document_id: str
    filename: str
    file_type: str
    pages: int
    chunks: int
    status: str
    created_at: str
    suggested_questions: list[str] = Field(default_factory=list)


class DocumentListResponse(BaseModel):
    total: int
    documents: list[DocumentDetail]


# -------------------------------------------------------------
# Chat & Retrieval Schemas
# -------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class SourceEvidence(BaseModel):
    document_id: str
    filename: str
    page: int
    section: Optional[str] = "General"
    evidence: str
    chunk_id: str
    similarity_score: Optional[float] = None
    semantic_score: Optional[float] = None
    coverage_score: Optional[float] = None


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    conversation_history: list[ChatMessage] = Field(default_factory=list)
    document_id: Optional[str] = Field(None, description="Optional filter to single document")


class ChatResponse(BaseModel):
    status: ChatStatus
    answer: str
    confidence: ConfidenceLevel
    sources: list[SourceEvidence] = Field(default_factory=list)
    suggested_followups: list[str] = Field(default_factory=list)


class SuggestedQuestionsResponse(BaseModel):
    document_id: str
    filename: str
    questions: list[str]


class HealthResponse(BaseModel):
    status: str
    version: str
    embedding_model: str
    llm_provider: str
    vector_store_documents: int
