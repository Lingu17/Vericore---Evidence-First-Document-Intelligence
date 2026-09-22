"""
Token-Optimized Retriever Service for DocuPilot.
Coordinates deterministic query normalization, deduplication, threshold gating,
and adaptive evidence context sizing (1–3 chunks).

Hybrid retrieval (dense + lexical grounding):
- Semantic cosine search fetches a candidate pool from ChromaDB.
- A lexical coverage score measures how many question content keywords literally
  appear in a candidate (strong signal that the chunk directly contains the answer).
- Candidates are reranked by hybrid = min(1, cosine + weight * coverage^2) so a chunk
  that directly contains the answer outranks a merely semantically related chunk.
- The relevance gate accepts a query when either the top cosine passes the semantic
  threshold OR the best grounded candidate satisfies the lexical override (cosine
  floor + coverage floor + min matched terms), keeping unsupported questions NOT_FOUND.
"""

import re
from typing import Optional
from app.core.config import settings
from app.core.logging import logger
from app.models.schemas import SourceEvidence
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store_service
from app.utils.text import calculate_keyword_coverage, extract_query_keywords


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


def _hybrid_score(cosine_similarity: float, coverage: float) -> float:
    """Combines semantic similarity with lexical grounding (direct-answer emphasis)."""
    bonus = settings.COVERAGE_BONUS_WEIGHT * (coverage ** 2)
    return max(0.0, min(1.0, cosine_similarity + bonus))


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
        self.candidate_pool_size = settings.CANDIDATE_POOL_SIZE
        self.min_candidate_cosine = settings.MIN_CANDIDATE_COSINE
        self.lexical_override_min_cosine = settings.LEXICAL_OVERRIDE_MIN_COSINE
        self.lexical_override_min_coverage = settings.LEXICAL_OVERRIDE_MIN_COVERAGE
        self.lexical_override_min_terms = settings.LEXICAL_OVERRIDE_MIN_TERMS
        self.semantic_gate_threshold = settings.SEMANTIC_GATE_THRESHOLD
        self.hybrid_high_relevance_threshold = settings.HYBRID_HIGH_RELEVANCE_THRESHOLD
        self.hybrid_strong_relevance_threshold = settings.HYBRID_STRONG_RELEVANCE_THRESHOLD

    def retrieve(
        self,
        query: str,
        document_id_filter: Optional[str] = None
    ) -> list[SourceEvidence]:
        """
        Hybrid retrieval pipeline:
        1. Normalize query + extract content keywords
        2. Vector search candidate pool in ChromaDB (cosine)
        3. Lexical coverage scoring + hybrid reranking
        4. Relevance gate (semantic threshold OR lexical override)
        5. Near-duplicate and identical chunk removal
        6. Adaptive context sizing on hybrid score (1-3 chunks)
        """
        normalized_query = normalize_query_text(query)
        if not normalized_query:
            return []

        keywords = extract_query_keywords(normalized_query)

        # 1. Embed query
        query_embedding = embedding_service.embed_text(normalized_query)
        if not query_embedding:
            return []

        # 2. Query ChromaDB with optional document scope filter
        raw_results = vector_store_service.search(
            query_embedding=query_embedding,
            top_k=self.candidate_pool_size,
            document_id_filter=document_id_filter
        )

        if not raw_results:
            logger.info("ChromaDB returned 0 results.")
            return []

        # 3. Score lexical coverage + hybrid rank for every candidate
        for res in raw_results:
            coverage, matched_terms = calculate_keyword_coverage(keywords, res["text"])
            res["coverage"] = coverage
            res["matched_terms"] = matched_terms
            res["hybrid"] = _hybrid_score(res["similarity"], coverage)
            res["_cos"] = res["similarity"]

        top_cosine = max(res["similarity"] for res in raw_results)

        # Best grounded candidate (highest coverage among reasonably similar chunks)
        grounded_candidates = [r for r in raw_results if r["similarity"] >= self.lexical_override_min_cosine]
        best_grounded = None
        if grounded_candidates:
            best_grounded = max(grounded_candidates, key=lambda r: (r["coverage"], r["matched_terms"], r["hybrid"]))

        # 4. Relevance gate: a query is supported if
        #    (a) the top cosine clears the semantic gate threshold, OR
        #    (b) a candidate both clears the lexical override (it essentially contains
        #        the answer terms) and is similar enough to the query.
        supported = top_cosine >= self.semantic_gate_threshold
        if not supported and best_grounded is not None:
            override_ok = (
                best_grounded["similarity"] >= self.lexical_override_min_cosine
                and best_grounded["coverage"] >= self.lexical_override_min_coverage
                and best_grounded["matched_terms"] >= self.lexical_override_min_terms
            )
            if override_ok:
                supported = True
                logger.info(
                    f"Lexical override accepted: cosine={best_grounded['similarity']:.3f}, "
                    f"coverage={best_grounded['coverage']:.2f}, terms={best_grounded['matched_terms']}."
                )

        if not supported:
            logger.info(
                f"Relevance Gate: Top cosine ({top_cosine:.3f}) is below semantic gate "
                f"({self.semantic_gate_threshold}) with no grounded override. Halting retrieval."
            )
            return []

        # Filter out weak candidates, then sort by hybrid score descending
        candidates = [r for r in raw_results if r["similarity"] >= self.min_candidate_cosine]
        candidates.sort(key=lambda x: (x["hybrid"], x["_cos"]), reverse=True)

        # 5. Remove exact and near-duplicates (> 75% overlap)
        deduped_candidates: list[dict] = []
        for candidate in candidates:
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

        # 6. Adaptive Context Sizing on the hybrid score
        top_hybrid = deduped_candidates[0]["hybrid"]
        if top_hybrid >= self.hybrid_high_relevance_threshold:
            target_chunks_count = 1
        elif top_hybrid >= self.hybrid_strong_relevance_threshold:
            target_chunks_count = 2
        else:
            target_chunks_count = self.final_context_chunks

        selected_candidates = deduped_candidates[:target_chunks_count]

        # 7. Format into SourceEvidence objects
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
                    similarity_score=round(res["hybrid"], 4),
                    semantic_score=round(res["similarity"], 4),
                    coverage_score=round(res["coverage"], 4)
                )
            )

        logger.info(
            f"Hybrid Retrieval: top cosine {top_cosine:.3f}, top hybrid {top_hybrid:.3f} "
            f"-> Selected {len(sources)} evidence chunk(s) (Limit: {target_chunks_count})."
        )
        return sources


retriever_service = RetrieverService()