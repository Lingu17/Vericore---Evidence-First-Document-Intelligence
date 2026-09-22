"""
Text processing and cleaning utilities.
Cleans raw document text, normalizes Unicode artifacts, and extracts structured section headings.
"""

import re


_COVERAGE_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "what", "which", "who", "whom", "how", "where", "when", "why",
    "of", "to", "for", "with", "on", "at", "in", "from", "by", "as",
    "and", "or", "but", "if", "then", "than", "so",
    "it", "its", "this", "that", "these", "those", "there", "here",
    "do", "did", "does", "can", "could", "may", "might", "would", "should",
    "shall", "will", "i", "we", "you", "your", "our", "me", "my", "us",
    "they", "them", "their", "please", "tell", "explain", "about", "per",
    "many", "much", "some", "any", "all", "each", "every", "most", "more",
    "not", "no", "yes", "have", "has", "had", "hasnt", "dont", "didnt",
    "doesnt", "cant", "wont", "shouldnt", "instead", "also", "only", "just",
}


def extract_query_keywords(text: str) -> list[str]:
    """
    Extracts content keywords from a query, dropping stopwords.
    Used by the hybrid retriever to compute lexical grounding (coverage).
    """
    words = re.findall(r"[a-zA-Z]+", (text or "").lower())
    seen: set[str] = set()
    keywords: list[str] = []
    for w in words:
        if w in _COVERAGE_STOPWORDS or len(w) <= 1 or w in seen:
            continue
        seen.add(w)
        keywords.append(w)
    return keywords


def calculate_keyword_coverage(keywords: list[str], text: str) -> tuple[float, int]:
    """
    Computes lexical grounding of a chunk against the query keywords.

    Returns (coverage, matched_count) where coverage is the fraction of query
    content keywords that appear in the chunk (token-exact or stem/prefix match).
    A high coverage strongly indicates the chunk literally contains the answer.
    """
    if not keywords or not text:
        return 0.0, 0

    tokens = set(re.findall(r"[a-zA-Z]+", text.lower()))
    matched = 0
    for qw in keywords:
        if qw in tokens:
            matched += 1
            continue
        if len(qw) >= 4 and any(
            t.startswith(qw) or qw.startswith(t)
            for t in tokens
            if len(t) >= 4
        ):
            matched += 1

    coverage = matched / len(keywords)
    return coverage, matched


def clean_text(text: str) -> str:
    """
    Cleans raw extracted text from PDF/TXT:
    - Normalizes Unicode dashes, quotes, and whitespace
    - Fixes hyphenated words broken across line breaks
    - Collapses excessive blank lines
    - Strips leading/trailing whitespace
    """
    if not text:
        return ""

    # Normalize special Unicode dashes and quotation marks
    text = (
        text.replace("\u2014", " - ")
        .replace("\u2013", " - ")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2022", "*")
        .replace("\ufffd", "-")
    )

    # Replace null bytes or control characters except newlines/tabs
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # Rejoin hyphenated linebreaks (e.g. 'implemen-\ntation' -> 'implementation')
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

    # Replace windows line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Replace multiple consecutive spaces/tabs with single space (preserve single newlines)
    text = re.sub(r"[ \t]+", " ", text)

    # Remove decorative repeating underscore/dash separator lines
    text = re.sub(r"^[_\-=]{3,}$", "", text, flags=re.MULTILINE)

    # Collapse 3+ newlines to 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def approximate_tokens(text: str) -> int:
    """Estimates token count (~4 characters per token on average)."""
    return max(1, len(text) // 4)


def extract_potential_headings(text: str) -> list[str]:
    """
    Extracts high-signal section headings from text lines.
    Looks for:
    - Numbered titles ('1. Annual Leave', 'Section 2.1 Benefits')
    - Markdown headers ('# Heading', '## Section')
    - ALL CAPS titles ('LEAVE ENTITLEMENT', 'PROBATIONARY PERIOD')
    - Short Title Case lines (< 60 chars ending without punctuation)
    """
    headings: list[str] = []
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    for line in lines:
        if len(line) > 80:
            continue

        # Ignore decorative lines or page footers
        if re.search(r"page\s+\d+", line, re.IGNORECASE) or line.startswith(("_", "-", "=")):
            continue

        # Markdown header
        if line.startswith("#"):
            cleaned = line.lstrip("#").strip()
            if cleaned and len(cleaned) > 2:
                headings.append(cleaned)
            continue

        # Numbered headings (e.g. "1. Leave Entitlement", "4. PROBATIONARY PERIOD", "Section 3: Health")
        if re.match(r"^(\d+\.|\d+\.\d+|Section\s+\d+|Article\s+\d+)[\s:]+[A-Za-z]", line):
            headings.append(line)
            continue

        # ALL CAPS line with at least 4 characters
        if line.isupper() and len(line) >= 4 and not line.isdigit():
            headings.append(line.title())
            continue

        # Short Title Case line that doesn't end with a period
        words = line.split()
        if 2 <= len(words) <= 7 and not line.endswith((".", ",", ";", ":")):
            capitalized_words = sum(1 for w in words if w and w[0].isupper())
            if capitalized_words >= len(words) * 0.7:
                headings.append(line)

    # Deduplicate while preserving order
    seen = set()
    unique_headings = []
    for h in headings:
        normalized = h.lower().strip()
        if normalized not in seen and len(normalized) >= 3:
            seen.add(normalized)
            unique_headings.append(h)

    return unique_headings
