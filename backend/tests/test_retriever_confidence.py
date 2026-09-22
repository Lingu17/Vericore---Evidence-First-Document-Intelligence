"""
Unit tests for Confidence and Retriever services.
Validates confidence calculation levels and similarity threshold gating.
"""

from app.models.schemas import ConfidenceLevel, SourceEvidence
from app.services.confidence import calculate_evidence_confidence


def test_confidence_high_with_strong_similarity():
    sources = [
        SourceEvidence(
            document_id="doc_1",
            filename="Leave.pdf",
            page=1,
            section="Annual Leave",
            evidence="Employees get 24 days.",
            chunk_id="doc_1-p1-c1",
            similarity_score=0.75
        ),
        SourceEvidence(
            document_id="doc_1",
            filename="Leave.pdf",
            page=1,
            section="Carry Forward",
            evidence="Up to 8 days can be carried over.",
            chunk_id="doc_1-p1-c2",
            similarity_score=0.60
        )
    ]
    confidence = calculate_evidence_confidence(sources, similarity_threshold=0.48)
    assert confidence == ConfidenceLevel.HIGH


def test_confidence_medium_with_moderate_similarity():
    sources = [
        SourceEvidence(
            document_id="doc_1",
            filename="Leave.pdf",
            page=1,
            section="General",
            evidence="Some policy text here.",
            chunk_id="doc_1-p1-c1",
            similarity_score=0.50
        )
    ]
    confidence = calculate_evidence_confidence(sources, similarity_threshold=0.48)
    assert confidence == ConfidenceLevel.MEDIUM


def test_confidence_low_when_below_threshold_or_empty():
    sources = [
        SourceEvidence(
            document_id="doc_1",
            filename="Leave.pdf",
            page=1,
            section="General",
            evidence="Irrelevant text.",
            chunk_id="doc_1-p1-c1",
            similarity_score=0.35
        )
    ]
    assert calculate_evidence_confidence(sources, similarity_threshold=0.48) == ConfidenceLevel.LOW
    assert calculate_evidence_confidence([], similarity_threshold=0.48) == ConfidenceLevel.LOW
