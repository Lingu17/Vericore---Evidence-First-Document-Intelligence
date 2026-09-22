"""
Unit tests for suggested-question generation and filtering.
Verifies that template/OCR artifacts, document titles, title-policy questions,
non-answerable headings, and duplicate/near-duplicate questions are filtered out
while meaningful, grounded questions are preserved.
"""

from pathlib import Path

from app.services.suggestions import generate_suggested_questions

SAMPLE_HANDBOOK = r"C:\Users\HP\Desktop\Sample employee handbook 1.pdf"


def test_spaced_ocr_artifact_filtered():
    headings = ["S A M P L E", "D R A F T", "Dress Code"]
    qs = generate_suggested_questions("handbook.pdf", headings, full_text="Dress Code policy.")
    assert not any("S A M P L E" in q or "D R A F T" in q for q in qs)
    assert any("Dress Code" in q for q in qs)


def test_document_title_heading_filtered():
    # 'Employee Handbook' matches the file title; 'Hours of Work' is real content.
    headings = ["Employee Handbook", "Hours of Work", "Dress Code"]
    qs = generate_suggested_questions(
        "Sample employee handbook 1.pdf", headings, full_text="Hours of Work from 8:30 am. Dress Code policy."
    )
    assert not any("Employee Handbook" in q for q in qs)
    assert any("working hours" in q.lower() for q in qs)


def test_policy_on_document_title_filtered():
    # 'What is the policy on <title>?' must not be generated from a filename-matched heading.
    headings = ["Novatech Time-Off & Leave Policy", "Annual Leave", "Sick Leave"]
    qs = generate_suggested_questions(
        "NovaTech_Leave_Policy.pdf", headings, full_text="Annual leave accrual. Sick and medical leave rules."
    )
    assert not any("Time-Off & Leave Policy" in q or "Time-off & Leave Policy" in q for q in qs)
    assert any("annual leave" in q.lower() for q in qs)


def test_non_answerable_heading_filtered():
    # Numbered filler dividers, greetings and pure numbers produce no questions.
    headings = ["1. WELCOME TO NOVATECH", "42", "M E M O", "Probationary Period"]
    qs = generate_suggested_questions(
        "NovaTech_Employee_Handbook.pdf", headings, full_text="Probationary period is 6 months."
    )
    assert not any("WELCOME" in q or "WELCOME" in q.upper() for q in qs)
    assert not any(q.strip().startswith(("42", "42?")) for q in qs)
    assert any("probation" in q.lower() for q in qs)


def test_near_duplicate_filtered():
    # A heading-derived paraphrase of an already-chosen curated question is dropped.
    headings = ["Performance Reviews", "Annual Leave"]
    qs = generate_suggested_questions(
        "handbook.pdf", headings,
        full_text="Performance reviews are held quarterly. Annual leave accrues 24 days."
    )
    assert len([q for q in qs if "performance review" in q.lower()]) <= 1
    assert len(qs) >= 2


def test_meaningful_questions_preserved():
    headings = ["Sick Leave", "Medical Insurance", "Performance Reviews"]
    generated = set(q.lower() for q in generate_suggested_questions(
        "handbook.pdf", headings,
        full_text="Sick leave allowance. Medical insurance coverage. Performance review process."
    ))
    assert "what is the policy and allowance for sick and medical leave?" in generated
    assert "what health and medical insurance coverage is provided?" in generated
    assert "how and when are employee performance reviews conducted?" in generated


def test_always_at_least_three_questions():
    headings: list[str] = []
    qs = generate_suggested_questions("empty.pdf", headings, full_text="Some policy text.")
    assert len(qs) >= 3


def test_sample_handbook_no_junk():
    """End-to-end guard for the exact regressions reported in the UI."""
    if not Path(SAMPLE_HANDBOOK).exists():
        return
    from app.services.document_parser import DocumentParser

    parsed = DocumentParser.parse(Path(SAMPLE_HANDBOOK).name, Path(SAMPLE_HANDBOOK).read_bytes())
    qs = generate_suggested_questions(Path(SAMPLE_HANDBOOK).name, parsed.headings, parsed.full_text)
    assert len(qs) >= 3
    assert not any("S A M P L E" in q for q in qs)
    assert not any("Employee Handbook" in q for q in qs)
    assert all(q.endswith("?") for q in qs)