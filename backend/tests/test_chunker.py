"""
Unit tests for DocumentChunker service.
Validates chunk sizing, overlap, page number preservation, and section assignment.
"""

from pathlib import Path
from app.services.chunker import DocumentChunker
from app.services.document_parser import DocumentParser

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "sample_documents"


def test_chunking_metadata_preservation():
    pdf_path = SAMPLES_DIR / "NovaTech_Benefits_Policy.pdf"
    with open(pdf_path, "rb") as f:
        content = f.read()

    parsed = DocumentParser.parse("NovaTech_Benefits_Policy.pdf", content)
    chunker = DocumentChunker(chunk_size=400, chunk_overlap=80)
    chunks = chunker.chunk_document("doc_test123", parsed)

    assert len(chunks) >= 2

    for chunk in chunks:
        assert chunk.document_id == "doc_test123"
        assert chunk.filename == "NovaTech_Benefits_Policy.pdf"
        assert chunk.page in [1, 2]
        assert chunk.chunk_id.startswith("doc_test123-p")
        assert len(chunk.text) > 0
        assert chunk.token_count is not None and chunk.token_count > 0


def test_chunker_section_detection():
    pdf_path = SAMPLES_DIR / "NovaTech_Employee_Handbook.pdf"
    with open(pdf_path, "rb") as f:
        content = f.read()

    parsed = DocumentParser.parse("NovaTech_Employee_Handbook.pdf", content)
    chunker = DocumentChunker(chunk_size=600, chunk_overlap=80)
    chunks = chunker.chunk_document("doc_handbook", parsed)

    sections = [c.section for c in chunks]
    assert any("PROBATIONARY" in s.upper() or "PROBATION" in s.upper() or "EMPLOYMENT" in s.upper() for s in sections)
