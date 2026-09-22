"""
DocuPilot Configuration Settings.
Optimized for minimum token usage, local execution, and strict evidence grounding.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # LLM Provider Configuration
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    USE_MOCK_LLM: bool = False

    # Generation Parameters (Token Optimization)
    MAX_OUTPUT_TOKENS: int = 128
    TEMPERATURE: float = 0.0
    MAX_HISTORY_MESSAGES: int = 2

    # Vector Database & Embeddings (Local ₹0 Cost)
    CHROMA_PATH: str = "./chroma_db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Retrieval & Adaptive Context Parameters
    TOP_K: int = 5
    FINAL_CONTEXT_CHUNKS: int = 3
    SIMILARITY_THRESHOLD: float = 0.48         # Cosine relevance cutoff for MiniLM
    STRONG_RELEVANCE_THRESHOLD: float = 0.54   # Cosine: select 2 chunks if score >= this
    HIGH_RELEVANCE_THRESHOLD: float = 0.62     # Cosine: select 1 chunk if score >= this

    # Hybrid Retrieval (semantic + lexical grounding)
    # Candidate pool fetched from ChromaDB before reranking.
    CANDIDATE_POOL_SIZE: int = 25
    # hybrid = min(1.0, cosine + COVERAGE_BONUS_WEIGHT * coverage^2)
    COVERAGE_BONUS_WEIGHT: float = 0.50
    # Drop candidates below this raw cosine similarity after reranking.
    MIN_CANDIDATE_COSINE: float = 0.20
    # Lower bounds the LEXICAL_OVERRIDE (below sketch) considers candidates.
    LEXICAL_OVERRIDE_MIN_COSINE: float = 0.25
    LEXICAL_OVERRIDE_MIN_COVERAGE: float = 0.85
    LEXICAL_OVERRIDE_MIN_TERMS: int = 2
    # Semantic gate: a query is supported when its top cosine reaches this bar
    # OR a candidate satisfies the lexical override (grounded but diluted chunk).
    SEMANTIC_GATE_THRESHOLD: float = 0.55
    # Adaptive sizing on the hybrid score (1/2/3 chunks).
    HYBRID_HIGH_RELEVANCE_THRESHOLD: float = 0.85
    HYBRID_STRONG_RELEVANCE_THRESHOLD: float = 0.70

    # Evidence Confidence (grounding-aware)
    CONFIDENCE_MIN_HYBRID: float = 0.45
    CONFIDENCE_MIN_COVERAGE: float = 0.50
    CONFIDENCE_HIGH_COVERAGE: float = 0.85
    CONFIDENCE_HIGH_SEMANTIC: float = 0.40

    # Ingestion & Chunking (Character-based)
    CHUNK_SIZE: int = 1200
    CHUNK_OVERLAP: int = 150

    # Upload & Processing Limits
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".txt"}

    # Server Settings
    ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


settings = Settings()
