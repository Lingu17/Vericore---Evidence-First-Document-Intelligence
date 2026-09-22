"""
Vector Store Service for DocuPilot using local ChromaDB.
Persists chunk embeddings, text, and rich metadata (document_id, filename, page, section, chunk_id).
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.core.logging import logger
from app.models.schemas import DocumentChunk, DocumentMetadata, DocumentStatus


class VectorStoreService:
    _instance: Optional["VectorStoreService"] = None

    def __new__(cls) -> "VectorStoreService":
        if cls._instance is None:
            cls._instance = super(VectorStoreService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initializes ChromaDB persistent client and document metadata catalog."""
        self.chroma_path = Path(settings.CHROMA_PATH)
        self.chroma_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.chroma_path / "documents_registry.json"

        logger.info(f"Initializing persistent ChromaDB at '{self.chroma_path}'...")
        self.client = chromadb.PersistentClient(
            path=str(self.chroma_path),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection_name = "docupilot_knowledge_base"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        # In-memory document metadata catalog persisted to JSON
        self._doc_registry: dict[str, dict[str, Any]] = self._load_registry()
        logger.info(
            f"ChromaDB ready. Collection '{self.collection_name}' contains "
            f"{self.collection.count()} chunks. Registered documents: {len(self._doc_registry)}."
        )

    def _load_registry(self) -> dict[str, dict[str, Any]]:
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load metadata registry: {e}. Starting fresh.")
        return {}

    def _save_registry(self) -> None:
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(self._doc_registry, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist document registry: {e}")

    def document_exists_by_hash(self, file_hash: str) -> Optional[DocumentMetadata]:
        """Checks if a document with the identical SHA-256 hash is already indexed."""
        for doc_data in self._doc_registry.values():
            if doc_data.get("file_hash") == file_hash:
                return DocumentMetadata(**doc_data)
        return None

    def get_document(self, document_id: str) -> Optional[DocumentMetadata]:
        """Retrieves metadata for a specific document ID."""
        doc_data = self._doc_registry.get(document_id)
        if doc_data:
            return DocumentMetadata(**doc_data)
        return None

    def get_all_documents(self) -> list[DocumentMetadata]:
        """Returns list of all registered documents sorted by creation date."""
        docs = [DocumentMetadata(**data) for data in self._doc_registry.values()]
        docs.sort(key=lambda d: d.created_at, reverse=True)
        return docs

    def add_document_chunks(
        self,
        document_id: str,
        filename: str,
        file_type: str,
        file_hash: str,
        page_count: int,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
        suggested_questions: list[str]
    ) -> DocumentMetadata:
        """Stores chunk embeddings, text, and metadata in ChromaDB."""
        if not chunks or not embeddings:
            raise ValueError("Cannot add empty chunks or embeddings to vector store.")

        ids = [c.chunk_id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [
            {
                "document_id": c.document_id,
                "filename": c.filename,
                "page": c.page,
                "section": c.section or "General",
                "chunk_id": c.chunk_id,
                "token_count": c.token_count or 0
            }
            for c in chunks
        ]

        # Upsert into ChromaDB
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,  # type: ignore
            documents=documents,
            metadatas=metadatas     # type: ignore
        )

        doc_meta = DocumentMetadata(
            document_id=document_id,
            filename=filename,
            file_type=file_type,
            file_hash=file_hash,
            page_count=page_count,
            chunk_count=len(chunks),
            status=DocumentStatus.INDEXED,
            created_at=datetime.now(timezone.utc).isoformat(),
            suggested_questions=suggested_questions
        )

        self._doc_registry[document_id] = doc_meta.model_dump()
        self._save_registry()

        logger.info(
            f"Successfully indexed document '{filename}' (ID: {document_id}) with "
            f"{len(chunks)} chunks in ChromaDB."
        )
        return doc_meta

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        document_id_filter: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Executes semantic vector similarity search against ChromaDB.
        Returns matched chunks with cosine distance / similarity.
        """
        if self.collection.count() == 0:
            return []

        where_clause = None
        if document_id_filter:
            where_clause = {"document_id": document_id_filter}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count()),
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )

        formatted_results: list[dict[str, Any]] = []

        if not results or not results.get("ids") or not results["ids"][0]:
            return []

        ids = results["ids"][0]
        docs = results["documents"][0] if results.get("documents") else []
        metas = results["metadatas"][0] if results.get("metadatas") else []
        distances = results["distances"][0] if results.get("distances") else []

        for chunk_id, doc_text, metadata, distance in zip(ids, docs, metas, distances):
            # ChromaDB cosine distance range: [0, 2]. Cosine similarity = 1 - distance
            similarity = max(0.0, min(1.0, 1.0 - float(distance)))
            formatted_results.append({
                "chunk_id": chunk_id,
                "text": doc_text,
                "metadata": metadata,
                "distance": distance,
                "similarity": similarity
            })

        return formatted_results

    def delete_document(self, document_id: str) -> bool:
        """Removes a document and all its chunks from ChromaDB and registry."""
        if document_id not in self._doc_registry:
            return False

        try:
            self.collection.delete(where={"document_id": document_id})
        except Exception as e:
            logger.warning(f"Error removing chunks from collection for {document_id}: {e}")

        del self._doc_registry[document_id]
        self._save_registry()
        logger.info(f"Deleted document ID '{document_id}' and all associated chunks.")
        return True

    def delete_all(self) -> None:
        """Purges all vectors and documents."""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self._doc_registry.clear()
        self._save_registry()
        logger.info("Cleared all documents and vector embeddings from ChromaDB.")


# Global singleton access
vector_store_service = VectorStoreService()
