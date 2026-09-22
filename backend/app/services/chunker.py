"""
Intelligent Section and Paragraph Chunker Service for DocuPilot.
Splits parsed documents by semantic sections and paragraphs while preserving page and section metadata.

Chunking strategy:
- Recognizes numbered, ALL CAPS, and Title Case headings so each section becomes a compact,
  self-contained chunk (prevents answer dilution inside oversized page-level chunks).
- Long sections are split by paragraphs, then by sentence windows with a real overlap
  so direct-answer sentences are never orphaned or glued into unrelated context.
"""

import re
from typing import Optional
from app.core.config import settings
from app.core.logging import logger
from app.models.schemas import DocumentChunk
from app.services.document_parser import ParsedDocument
from app.utils.text import approximate_tokens


# Words that typically begin prose sentences, never section headings.
_PROSE_STARTERS = {
    "the", "a", "an", "this", "these", "those", "that", "there", "here",
    "we", "you", "your", "ours", "our", "they", "them", "their", "he",
    "she", "it", "its", "in", "on", "at", "to", "for", "with", "from",
    "by", "as", "of", "and", "or", "if", "when", "while", "because",
    "although", "since", "until", "so", "not", "no", "all", "any", "each",
    "every", "some", "such", "however", "therefore", "during", "after",
    "before", "within", "between", "employees", "employers", "employee",
    "employer", "managers", "supervisors", "please", "must", "may", "will",
    "shall", "are", "is", "be", "was", "were", "have", "has", "had", "do",
    "does", "did", "can", "could", "would", "should", "one", "two", "three",
}

_ALL_CAPS_HEADING = re.compile(r"^[A-Z][A-Z0-9 &\-\/\'\.]{2,60}$")
_NUMBERED_HEADING = re.compile(
    r"^(?:\d+(?:\.\d+)*[.):\s-]+[A-Za-z]|Section\s+\d+[.:\s]+|Article\s+\d+[.:\s]+)"
)
_PAGE_MARKER = re.compile(r"^[-–\s]*\d+\s*[-–\s]*$")


def _is_heading_line(line: str) -> bool:
    """Detects section heading lines: numbered, ALL CAPS, or short Title Case."""
    s = line.strip()
    if not s or len(s) > 64:
        return False
    if re.search(r"page\s+\d+", s, re.IGNORECASE):
        return False
    if _PAGE_MARKER.match(s):
        return False
    # Numbered headings and Section/Article/Part headings
    if _NUMBERED_HEADING.match(s):
        return True
    words = re.findall(r"[A-Za-z]+", s)
    if not words:
        return False
    # ALL CAPS titles (e.g. "HOURS OF WORK")
    if s.isupper():
        alpha_chars = sum(1 for c in s if c.isalpha())
        return alpha_chars >= 3
    # Short Title Case lines (e.g. "Hours of Work", "Flex Time and Telecommuting")
    if re.search(r"[.!?]\s*$", s):
        return False
    if s[0].islower():
        return False
    if not (1 <= len(words) <= 8):
        return False
    capitalized = sum(1 for w in words if w and w[0].isupper())
    if capitalized * 10 < len(words) * 6:
        return False
    first_word = words[0].lower()
    if first_word in _PROSE_STARTERS:
        return False
    return True


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
        based on detected headings (numbered, ALL CAPS, Title Case).
        """
        if not text or not text.strip():
            return []

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

            if _is_heading_line(line_str):
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

    def _split_oversized_text(self, sec_title: str, sec_text: str) -> list[str]:
        """
        Splits a section that exceeds chunk_size into overlapping sentence windows.
        Returns a list of chunk text strings. The section heading is prepended to
        the first window so the section stays identifiable.
        """
        body = sec_text
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n\s*\n", body) if s.strip()]
        if not sentences:
            return [sec_text]

        windows: list[str] = []
        start = 0
        overlap = max(0, self.chunk_overlap)

        while start < len(sentences):
            take: list[str] = []
            length = 0
            for i in range(start, len(sentences)):
                s_len = len(sentences[i])
                if take and length + s_len > self.chunk_size:
                    break
                take.append(sentences[i])
                length += s_len

            if not take:
                break

            text = " ".join(take)
            if start == 0:
                text = f"{sec_title}\n{text}"
            windows.append(text)

            if len(take) == 1:
                start += 1
                continue

            # Carry trailing sentences back into the next window up to overlap chars
            carry: list[str] = []
            carry_len = 0
            for s_ in reversed(take):
                if carry_len + len(s_) > overlap:
                    break
                carry.insert(0, s_)
                carry_len += len(s_)

            if len(carry) >= len(take):
                start += 1
            else:
                start = start + len(take) - len(carry)

        return windows

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
                # Long sections: split into paragraphs first
                if len(sec_text) > self.chunk_size:
                    paras = [p.strip() for p in sec_text.split("\n\n") if p.strip()]
                    grouped: list[tuple[int, str]] = []
                    for p in paras:
                        if len(p) > self.chunk_size:
                            for sub_text in self._split_oversized_text(sec_title, p):
                                grouped.append((page_chunk_idx, sub_text))
                        else:
                            grouped.append((page_chunk_idx, f"{sec_title}\n{p}" if not grouped else p))
                else:
                    grouped = [(page_chunk_idx, sec_text)]

                for sub_idx, (sec_idx, chunk_text) in enumerate(grouped, start=1):
                    if sub_idx == 1:
                        chunk_id = f"{document_id}-p{page.page_number}-c{sec_idx}"
                    else:
                        chunk_id = f"{document_id}-p{page.page_number}-c{sec_idx}_{sub_idx}"
                    all_chunks.append(
                        DocumentChunk(
                            chunk_id=chunk_id,
                            document_id=document_id,
                            filename=parsed.filename,
                            page=page.page_number,
                            section=sec_title,
                            text=chunk_text,
                            token_count=approximate_tokens(chunk_text)
                        )
                    )

        logger.info(
            f"Chunked '{parsed.filename}' (Doc ID: {document_id}): "
            f"{len(all_chunks)} semantic chunks created across {parsed.total_pages} page(s)."
        )
        return all_chunks