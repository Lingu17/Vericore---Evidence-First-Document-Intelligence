"""
Evidence Confidence Scoring Service.
Computes categorical evidence confidence (HIGH, MEDIUM, LOW) based on semantic retrieval
quality AND lexical grounding.

Confidence reflects whether the retrieved evidence actually supports the question:
- HIGH requires strong semantic relevance AND strong lexical grounding (the top chunk
  literally contains most of the question's content terms), OR an exceptionally high
  hybrid score. It is never granted for semantic similarity alone.
- MEDIUM: passes the relevance gate but grounding or semantic strength is weaker.
- LOW: below the gate / zero retrieved sources / weak grounding.
"""

from app.core.config import settings
from app.models.schemas import ConfidenceLevel, SourceEvidence


def _legacy_confidence(
    scores: list[float],
    similarity_threshold: float
) -> ConfidenceLevel:
    """Backward-compatible confidence derived from similarity scores alone."""
    max_score = max(scores)

    if max_score < similarity_threshold:
        return ConfidenceLevel.LOW

    if max_score >= 0.58:
        return ConfidenceLevel.HIGH
    elif max_score >= 0.54 and len(scores) >= 2 and sorted(scores, reverse=True)[1] >= 0.50:
        return ConfidenceLevel.HIGH
    elif max_score >= similarity_threshold:
        return ConfidenceLevel.MEDIUM

    return ConfidenceLevel.LOW


def _grounded_confidence(
    hybrid_score: float,
    semantic_score: float,
    coverage_score: float
) -> ConfidenceLevel:
    """
    Grounding-aware confidence on the hybrid scale.

    LOW: hybrid below the gate floor OR almost no lexical grounding.
    HIGH: full lexical grounding (>= 85% of question terms present) with a decent
          semantic score, OR a very high hybrid score.
    MEDIUM: otherwise.
    """
    if hybrid_score < settings.CONFIDENCE_MIN_HYBRID:
        return ConfidenceLevel.LOW
    if coverage_score < settings.CONFIDENCE_MIN_COVERAGE:
        return ConfidenceLevel.LOW

    if (
        coverage_score >= settings.CONFIDENCE_HIGH_COVERAGE
        and semantic_score >= settings.CONFIDENCE_HIGH_SEMANTIC
    ):
        return ConfidenceLevel.HIGH

    if hybrid_score >= 0.75 and semantic_score >= 0.45:
        return ConfidenceLevel.HIGH

    return ConfidenceLevel.MEDIUM


def calculate_evidence_confidence(
    sources: list[SourceEvidence],
    similarity_threshold: float = settings.SIMILARITY_THRESHOLD
) -> ConfidenceLevel:
    """
    Evaluates evidence retrieval strength.
    Uses grounded (hybrid) scoring when the retriever provided semantic/coverage
    scores; otherwise falls back to the legacy similarity-only scoring.
    """
    if not sources:
        return ConfidenceLevel.LOW

    scores = [s.similarity_score for s in sources if s.similarity_score is not None]
    if not scores:
        return ConfidenceLevel.LOW

    top = sources[0]
    if top.semantic_score is not None and top.coverage_score is not None:
        return _grounded_confidence(
            hybrid_score=float(top.similarity_score or 0.0),
            semantic_score=float(top.semantic_score),
            coverage_score=float(top.coverage_score)
        )

    return _legacy_confidence(scores, similarity_threshold)