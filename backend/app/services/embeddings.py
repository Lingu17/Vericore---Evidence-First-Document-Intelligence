"""
Local Embedding Service for DocuPilot.
Uses sentence-transformers (all-MiniLM-L6-v2) for zero-cost, on-premise local vector embeddings.
"""

from typing import Optional
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.logging import logger


class EmbeddingService:
    _instance: Optional["EmbeddingService"] = None
    _model: Optional[SentenceTransformer] = None

    def __new__(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._initialize_model()
        return cls._instance

    def _initialize_model(self) -> None:
        """Initializes the SentenceTransformer model once."""
        model_name = settings.EMBEDDING_MODEL
        logger.info(f"Loading local embedding model: '{model_name}'...")
        try:
            self._model = SentenceTransformer(model_name)
            logger.info(f"Local embedding model '{model_name}' initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model '{model_name}': {e}")
            raise RuntimeError(f"Embedding model initialization failed: {e}")

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._initialize_model()
        return self._model  # type: ignore

    def embed_text(self, text: str) -> list[float]:
        """Generates embedding vector for a single string."""
        if not text:
            return []
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generates embedding vectors for a batch of strings."""
        if not texts:
            return []
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        return embeddings.tolist()


# Global singleton access
embedding_service = EmbeddingService()
