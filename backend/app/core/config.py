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
    SIMILARITY_THRESHOLD: float = 0.48         # Calibrated relevance cutoff for MiniLM
    STRONG_RELEVANCE_THRESHOLD: float = 0.54   # Select 2 chunks if score >= this
    HIGH_RELEVANCE_THRESHOLD: float = 0.62     # Select 1 chunk if score >= this

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
