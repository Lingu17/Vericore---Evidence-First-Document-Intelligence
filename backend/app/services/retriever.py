"""
Token-Optimized Retriever Service for DocuPilot.
Coordinates deterministic query normalization, deduplication, threshold gating,
and adaptive evidence context sizing (1–3 chunks).
"""

import re
from typing import Optional
from app.core.config import settings
from app.core.logging import logger
from app.models.schemas import SourceEvidence
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store_service


def normalize_query_text(query: str) -> str:
    """Normalizes query text (lowercase, strips punctuation & extra whitespace)."""
    if not query:
        return ""
    q = query.strip().lower()
    # Normalize question marks, periods, commas, extra spaces
    q = re.sub(r"[?!.,;:\"']+", " ", q)
    q = re.sub(r"\s+", " ", q)
    return q.strip()


def calculate_text_overlap_ratio(text1: str, text2: str) -> float:
    """Calculates word-level Jaccard similarity to detect near-duplicate chunks."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union)


class RetrieverService:
    def __init__(
        self,
        top_k: int = settings.TOP_K,
        final_context_chunks: int = settings.FINAL_CONTEXT_CHUNKS,
        similarity_threshold: float = settings.SIMILARITY_THRESHOLD,
        high_relevance_threshold: float = settings.HIGH_RELEVANCE_THRESHOLD,
        strong_relevance_threshold: float = settings.STRONG_RELEVANCE_THRESHOLD
    ):
        self.top_k = top_k
        self.final_context_chunks = final_context_chunks
        self.similarity_threshold = similarity_threshold
        self.high_relevance_threshold = high_relevance_threshold
        self.strong_relevance_threshold = strong_relevance_threshold

    def retrieve(
        self,
        query: str,
        document_id_filter: Optional[str] = None
    ) -> list[SourceEvidence]:
        """
        Token-optimized retrieval pipeline:
        1. Normalize query
        2. Vector search in ChromaDB (Top-K)
        3. Relevance threshold filtering (rejects chunks < similarity_threshold)
        4. Near-duplicate and identical chunk removal
        5. Adaptive context sizing:
           - score >= high_relevance_threshold: 1 chunk
           - score >= strong_relevance_threshold: 2 chunks
           - score >= similarity_threshold: max 3 chunks
        """
        normalized_query = normalize_query_text(query)
        if not normalized_query:
            return []

        # 1. Embed query
        query_embedding = embedding_service.embed_text(normalized_query)
        if not query_embedding:
            return []

        # 2. Query ChromaDB with optional document scope filter
        raw_results = vector_store_service.search(
            query_embedding=query_embedding,
            top_k=self.top_k,
            document_id_filter=document_id_filter
        )

        if not raw_results:
            logger.info("ChromaDB returned 0 results.")
            return []

        # 3. Sort by similarity descending
        raw_results.sort(key=lambda x: x["similarity"], reverse=True)
        top_score = raw_results[0]["similarity"]

        # Relevance gate
        if top_score < self.similarity_threshold:
            logger.info(
                f"Relevance Gate: Top candidate similarity ({top_score:.3f}) is below "
                f"threshold ({self.similarity_threshold}). Halting retrieval with 0 LLM calls."
            )
            return []

        # 4. Remove exact and near-duplicates (> 75% overlap)
        deduped_candidates: list[dict] = []
        for candidate in raw_results:
            sim = candidate["similarity"]
            if sim < self.similarity_threshold:
                continue

            text = candidate["text"]
            is_duplicate = False
            for existing in deduped_candidates:
                if candidate["chunk_id"] == existing["chunk_id"]:
                    is_duplicate = True
                    break
                # Check near-duplicate text overlap
                overlap = calculate_text_overlap_ratio(text, existing["text"])
                if overlap > 0.75:
                    is_duplicate = True
                    break

            if not is_duplicate:
                deduped_candidates.append(candidate)

        if not deduped_candidates:
            return []

        # 5. Adaptive Context Sizing
        # - Very high relevance: send 1 chunk
        # - Strong relevance: send 2 chunks
        # - Moderate relevance: send at most final_context_chunks (3)
        if top_score >= self.high_relevance_threshold:
            target_chunks_count = 1
        elif top_score >= self.strong_relevance_threshold:
            target_chunks_count = 2
        else:
            target_chunks_count = self.final_context_chunks

        selected_candidates = deduped_candidates[:target_chunks_count]

        # 6. Format into SourceEvidence objects
        sources: list[SourceEvidence] = []
        for res in selected_candidates:
            meta = res["metadata"]
            sources.append(
                SourceEvidence(
                    document_id=meta.get("document_id", ""),
                    filename=meta.get("filename", "Document"),
                    page=int(meta.get("page", 1)),
                    section=meta.get("section", "General"),
                    evidence=res["text"],
                    chunk_id=res["chunk_id"],
                    similarity_score=round(res["similarity"], 4)
                )
            )

        logger.info(
            f"Adaptive Retrieval: Top score {top_score:.3f} -> Selected {len(sources)} "
            f"evidence chunk(s) (Limit: {target_chunks_count})."
        )
        return sources


retriever_service = RetrieverService()
