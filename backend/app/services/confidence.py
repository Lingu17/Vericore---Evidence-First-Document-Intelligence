"""
Evidence Confidence Scoring Service.
Computes categorical evidence confidence (HIGH, MEDIUM, LOW) based on semantic retrieval quality.
Never presents confidence as a fabricated probabilistic percentage.
"""

from app.core.config import settings
from app.models.schemas import ConfidenceLevel, SourceEvidence


def calculate_evidence_confidence(
    sources: list[SourceEvidence],
    similarity_threshold: float = settings.SIMILARITY_THRESHOLD
) -> ConfidenceLevel:
    """
    Evaluates evidence retrieval strength:
    - HIGH: Top chunk similarity >= 0.58 or (>= 0.54 with multiple matching chunks)
    - MEDIUM: Top chunk similarity >= similarity_threshold (0.48)
    - LOW: Below similarity_threshold or zero retrieved sources
    """
    if not sources:
        return ConfidenceLevel.LOW

    scores = [s.similarity_score for s in sources if s.similarity_score is not None]
    if not scores:
        return ConfidenceLevel.LOW

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
