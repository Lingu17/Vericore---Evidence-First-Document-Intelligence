"""
Intelligent Section and Paragraph Chunker Service for DocuPilot.
Splits parsed documents by semantic sections and paragraphs while preserving page and section metadata.
"""

import re
from typing import Optional
from app.core.config import settings
from app.core.logging import logger
from app.models.schemas import DocumentChunk
from app.services.document_parser import ParsedDocument
from app.utils.text import approximate_tokens, extract_potential_headings


class DocumentChunker:
    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def _split_into_sections(self, text: str) -> list[tuple[str, str]]:
        """
        Splits page text into (section_title, section_text) tuples
        based on numbered headings or paragraph breaks.
        """
        if not text or not text.strip():
            return []

        # Split text by numbered headers e.g. "1. WELCOME", "4. PROBATIONARY PERIOD"
        # or double newlines
        lines = text.split("\n")
        sections: list[tuple[str, list[str]]] = []
        current_header = "General"
        current_lines: list[str] = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                if current_lines:
                    current_lines.append("")
                continue

            # Check if this line is a numbered header
            header_match = re.match(r"^(\d+\.|\d+\.\d+|Section\s+\d+|Article\s+\d+)[\s:]+(.+)$", line_str, re.IGNORECASE)
            if header_match:
                if current_lines:
                    sections.append((current_header, current_lines))
                    current_lines = []
                current_header = line_str
                current_lines.append(line_str)
            else:
                current_lines.append(line_str)

        if current_lines:
            sections.append((current_header, current_lines))

        result: list[tuple[str, str]] = []
        for sec_title, sec_lines in sections:
            sec_text = "\n".join(sec_lines).strip()
            if sec_text:
                result.append((sec_title, sec_text))

        return result

    def chunk_document(self, document_id: str, parsed: ParsedDocument) -> list[DocumentChunk]:
        """
        Creates metadata-enriched chunks from a parsed document.
        Maintains document_id, filename, page, section, and unique chunk_id.
        """
        all_chunks: list[DocumentChunk] = []

        for page in parsed.pages:
            if not page.text.strip():
                continue

            sections = self._split_into_sections(page.text)
            if not sections:
                sections = [("General", page.text.strip())]

            for page_chunk_idx, (sec_title, sec_text) in enumerate(sections, start=1):
                # If section text is unusually long (> chunk_size), split into paragraphs
                if len(sec_text) > self.chunk_size:
                    paras = [p.strip() for p in sec_text.split("\n\n") if p.strip()]
                    for sub_idx, p in enumerate(paras, start=1):
                        chunk_id = f"{document_id}-p{page.page_number}-c{page_chunk_idx}_{sub_idx}"
                        all_chunks.append(
                            DocumentChunk(
                                chunk_id=chunk_id,
                                document_id=document_id,
                                filename=parsed.filename,
                                page=page.page_number,
                                section=sec_title,
                                text=p,
                                token_count=approximate_tokens(p)
                            )
                        )
                else:
                    chunk_id = f"{document_id}-p{page.page_number}-c{page_chunk_idx}"
                    all_chunks.append(
                        DocumentChunk(
                            chunk_id=chunk_id,
                            document_id=document_id,
                            filename=parsed.filename,
                            page=page.page_number,
                            section=sec_title,
                            text=sec_text,
                            token_count=approximate_tokens(sec_text)
                        )
                    )

        logger.info(
            f"Chunked '{parsed.filename}' (Doc ID: {document_id}): "
            f"{len(all_chunks)} semantic chunks created across {parsed.total_pages} page(s)."
        )
        return all_chunks
