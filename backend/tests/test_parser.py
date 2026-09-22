"""
Unit tests for DocumentParser service.
Validates PDF extraction, page tracking, TXT decoding, and error cases.
"""

from pathlib import Path
import pytest
from app.services.document_parser import DocumentParser, DocumentParserError

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "sample_documents"


def test_pdf_parsing_preserves_pages_and_sections():
    pdf_path = SAMPLES_DIR / "NovaTech_Leave_Policy.pdf"
    assert pdf_path.exists(), "Sample PDF not found."

    with open(pdf_path, "rb") as f:
        content = f.read()

    parsed = DocumentParser.parse("NovaTech_Leave_Policy.pdf", content)
    assert parsed.filename == "NovaTech_Leave_Policy.pdf"
    assert parsed.file_type == "pdf"
    assert parsed.total_pages == 2
    assert len(parsed.pages) == 2

    # Check page 1 text
    page1 = parsed.pages[0]
    assert page1.page_number == 1
    assert "24 annual leave days" in page1.text
    assert "carry forward a maximum of up to 8" in page1.text

    # Check page 2 text
    page2 = parsed.pages[1]
    assert page2.page_number == 2
    assert "10 paid sick leave days" in page2.text
    assert "16 weeks of fully paid maternity leave" in page2.text


def test_txt_parsing():
    txt_path = SAMPLES_DIR / "NovaTech_Remote_Work_FAQ.txt"
    assert txt_path.exists(), "Sample TXT not found."

    with open(txt_path, "rb") as f:
        content = f.read()

    parsed = DocumentParser.parse("NovaTech_Remote_Work_FAQ.txt", content)
    assert parsed.file_type == "txt"
    assert parsed.total_pages == 1
    assert "HOME OFFICE SETUP ALLOWANCE" in parsed.full_text
    assert "$500" in parsed.full_text


def test_empty_file_rejected():
    with pytest.raises(DocumentParserError, match="Uploaded file is empty"):
        DocumentParser.parse("empty.pdf", b"")


def test_unsupported_file_extension_rejected():
    with pytest.raises(DocumentParserError, match="Unsupported file type"):
        DocumentParser.parse("data.exe", b"binary content")


def test_corrupt_pdf_rejected():
    with pytest.raises(DocumentParserError):
        DocumentParser.parse("broken.pdf", b"%PDF-corrupted-bytes-data")
