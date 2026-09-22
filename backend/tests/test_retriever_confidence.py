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


def test_grounded_confidence_high_when_full_coverage_and_semantic_match():
    sources = [
        SourceEvidence(
            document_id="doc_1",
            filename="Handbook.pdf",
            page=10,
            section="Hours of Work",
            evidence="Hours of Work The workweek runs 8:30 am to 5:30 pm.",
            chunk_id="doc_1-p10-c4",
            similarity_score=1.0,
            semantic_score=0.72,
            coverage_score=1.0
        )
    ]
    assert calculate_evidence_confidence(sources) == ConfidenceLevel.HIGH


def test_grounded_confidence_medium_when_weak_semantic_but_strong_coverage():
    # Grounded (covers all terms) but semantically diluted -> MEDIUM, never HIGH.
    sources = [
        SourceEvidence(
            document_id="doc_1",
            filename="Handbook.pdf",
            page=14,
            section="Performance Reviews, Salary Reviews",
            evidence="You will have your first performance review at the end of your first three (3) months.",
            chunk_id="doc_1-p14-c4",
            similarity_score=0.85,
            semantic_score=0.32,
            coverage_score=1.0
        )
    ]
    assert calculate_evidence_confidence(sources) == ConfidenceLevel.MEDIUM


def test_grounded_confidence_not_high_when_coverage_gap():
    # Semantically similar but missing a key term ("bonus") must never be HIGH.
    sources = [
        SourceEvidence(
            document_id="doc_1",
            filename="Handbook.pdf",
            page=14,
            section="Performance Reviews, Salary Reviews",
            evidence="Compensation increases are given at the Company's discretion.",
            chunk_id="doc_1-p14-c1",
            similarity_score=0.60,
            semantic_score=0.50,
            coverage_score=0.60
        )
    ]
    assert calculate_evidence_confidence(sources) == ConfidenceLevel.MEDIUM
