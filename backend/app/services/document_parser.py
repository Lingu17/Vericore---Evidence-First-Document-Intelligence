"""
Document Parser Service for DocuPilot.
Extracts page-aware text and section hierarchy from PDF and TXT files using PyMuPDF and native text decoders.
"""

from typing import NamedTuple
import pymupdf as fitz  # PyMuPDF
from app.core.config import settings
from app.core.logging import logger
from app.utils.text import clean_text, extract_potential_headings


class PageContent(NamedTuple):
    page_number: int
    text: str
    headings: list[str]


class ParsedDocument(NamedTuple):
    filename: str
    file_type: str
    total_pages: int
    pages: list[PageContent]
    full_text: str
    headings: list[str]


class DocumentParserError(Exception):
    """Base exception for document parsing failures."""
    pass


class DocumentParser:
    @staticmethod
    def validate_file(filename: str, file_bytes: bytes) -> None:
        """Validates file extension and size constraints."""
        if not filename or "." not in filename:
            raise DocumentParserError("Invalid filename provided.")

        extension = f".{filename.split('.')[-1].lower()}"
        if extension not in settings.ALLOWED_EXTENSIONS:
            allowed = ", ".join(settings.ALLOWED_EXTENSIONS)
            raise DocumentParserError(
                f"Unsupported file type '{extension}'. Supported formats: {allowed}"
            )

        if len(file_bytes) == 0:
            raise DocumentParserError("Uploaded file is empty (0 bytes).")

        if len(file_bytes) > settings.max_file_size_bytes:
            raise DocumentParserError(
                f"File size exceeds maximum allowed limit of {settings.MAX_FILE_SIZE_MB}MB."
            )

    @classmethod
    def parse_pdf(cls, filename: str, file_bytes: bytes) -> ParsedDocument:
        """
        Parses a PDF document using PyMuPDF (fitz).
        Extracts text page by page, tracking exact 1-indexed page numbers.
        """
        cls.validate_file(filename, file_bytes)

        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            logger.error(f"Failed to open PDF {filename}: {e}")
            raise DocumentParserError(f"Corrupted or invalid PDF file: {str(e)}")

        if doc.page_count == 0:
            doc.close()
            raise DocumentParserError("PDF document contains no pages.")

        pages_data: list[PageContent] = []
        all_headings: list[str] = []
        combined_text_parts: list[str] = []

        try:
            for page_idx in range(doc.page_count):
                page = doc.load_page(page_idx)
                raw_text = page.get_text("text") or ""
                cleaned = clean_text(raw_text)

                page_headings = extract_potential_headings(cleaned)
                all_headings.extend(page_headings)

                page_num = page_idx + 1
                pages_data.append(PageContent(
                    page_number=page_num,
                    text=cleaned,
                    headings=page_headings
                ))
                if cleaned:
                    combined_text_parts.append(cleaned)
        finally:
            doc.close()

        full_text = "\n\n".join(combined_text_parts)
        if not full_text.strip():
            raise DocumentParserError(
                "No readable text could be extracted from this PDF. "
                "The document may be scanned or image-only."
            )

        # Unique headings preserving order
        unique_headings = list(dict.fromkeys(all_headings))

        logger.info(f"Successfully parsed PDF '{filename}' ({len(pages_data)} pages, {len(unique_headings)} sections).")
        return ParsedDocument(
            filename=filename,
            file_type="pdf",
            total_pages=len(pages_data),
            pages=pages_data,
            full_text=full_text,
            headings=unique_headings
        )

    @classmethod
    def parse_txt(cls, filename: str, file_bytes: bytes) -> ParsedDocument:
        """
        Parses a plain text file.
        Attempts UTF-8 first, with Latin-1 fallback for legacy encodings.
        """
        cls.validate_file(filename, file_bytes)

        try:
            raw_text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                raw_text = file_bytes.decode("latin-1")
            except Exception as e:
                raise DocumentParserError(f"Could not decode text file encoding: {str(e)}")

        cleaned = clean_text(raw_text)
        if not cleaned:
            raise DocumentParserError("The text file is empty or contains only whitespace.")

        headings = extract_potential_headings(cleaned)
        page_content = PageContent(page_number=1, text=cleaned, headings=headings)

        logger.info(f"Successfully parsed TXT '{filename}': 1 page, {len(headings)} sections.")
        return ParsedDocument(
            filename=filename,
            file_type="txt",
            total_pages=1,
            pages=[page_content],
            full_text=cleaned,
            headings=headings
        )

    @classmethod
    def parse(cls, filename: str, file_bytes: bytes) -> ParsedDocument:
        """Entry point that auto-detects format and parses."""
        cls.validate_file(filename, file_bytes)
        ext = f".{filename.split('.')[-1].lower()}" if "." in filename else ""
        if ext == ".pdf":
            return cls.parse_pdf(filename, file_bytes)
        elif ext == ".txt":
            return cls.parse_txt(filename, file_bytes)
        else:
            raise DocumentParserError(f"Unsupported file type '{ext}'.")
