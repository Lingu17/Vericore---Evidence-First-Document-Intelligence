"""
Smart Suggested Questions Generator.
Generates 3-5 useful, high-impact business questions from document structure, headings,
and topics with zero mandatory LLM token overhead.

Generated questions are aggressively filtered so that template/OCR artifacts, document
titles, headings with no answerable content, and duplicate/near-duplicate questions never
reach the UI.

Filters applied:
1. OCR/template artifacts            - spaced single letters like 'S A M P L E'
2. Document/template titles          - headings matching the file's title or generic labels
   (e.g. 'Employee Handbook', 'Sample')
3. Title-policy questions            - 'What is the policy on <document title>?'
4. Non-answerable headings           - pure numbers, greetings, filler-only labels, or
   headings whose words never appear in the document text
5. Duplicates / near-duplicates      - exact duplicates and high-overlap rewordings
"""

import re
from typing import Optional
from app.core.logging import logger
from app.utils.text import extract_query_keywords


HEADING_TO_QUESTION_PATTERNS = [
    (r"annual leave|leave entitlement|vacation", "How many annual leave days are provided per year?"),
    (r"carry forward|rollover|unused leave", "Can unused leave days be carried forward to the next year?"),
    (r"sick leave|medical leave", "What is the policy and allowance for sick and medical leave?"),
    (r"parental leave|maternity|paternity", "What are the parental and maternity leave provisions?"),
    (r"probation|probationary period", "What is the probation period for new employees?"),
    (r"working hours|work schedule|hours of work", "What are the official working hours and core schedule?"),
    (r"code of conduct|conduct|workplace ethics", "What are the key employee code of conduct guidelines?"),
    (r"health insurance|medical insurance|coverage", "What health and medical insurance coverage is provided?"),
    (r"wellness|gym|fitness", "What wellness and fitness benefits or reimbursements are available?"),
    (r"learning|stipend|education|development", "What learning and professional development stipends are offered?"),
    (r"performance review|appraisal|evaluation", "How and when are employee performance reviews conducted?"),
    (r"termination|notice period|resignation", "What is the required notice period for resignation or termination?"),
    (r"remote work|work from home|hybrid", "What is the company's remote and hybrid work policy?"),
    (r"travel|expense|reimbursement", "What business travel expenses are eligible for reimbursement?")
]

# Headings that are structural labels, not factual content (pages, dividers, boilerplate).
_JUNK_SECTIONS = {
    "overview", "introduction", "table of contents", "contents", "summary", "general",
    "index", "glossary", "disclaimer", "legal disclaimer", "notice", "acknowledgement",
    "acknowledgements", "acknowledgment", "acknowledgments", "preface", "foreword",
    "about", "about this document", "help", "contact", "contact information",
    "confidential", "draft", "for employers only", "employer note", "employer notes"
}

# Words that mark a heading as a greeting/intro line rather than a policy topic.
_GREETING_WORDS = {"welcome", "welcomes", "greeting", "greetings", "hello", "introduction",
                   "intro", "congratulations", "dear"}

# Words that only describe the document itself. A heading built solely from these words
# has no answerable factual content (e.g. 'Employee Handbook', 'Sample', 'Company Policy').
_DOC_TITLE_WORDS = {
    "employee", "employees", "employer", "employers", "employment", "staff", "company",
    "companies", "corporate", "corporation", "enterprise", "enterprises", "incorporated",
    "inc", "llc", "corp", "human", "resources", "personnel", "handbook", "manual", "guide",
    "guidelines", "policy", "policies", "document", "documents", "sample", "templates",
    "template", "forms", "form", "records", "record", "confidential", "confidentiality",
    "draft", "final", "version", "revisions", "revision", "updated", "issued", "effective",
    "legal", "summary", "contents", "index", "glossary", "appendix"
}

# Filler words that signal a label instead of a concrete, answerable topic.
_FILLER_TOPICS = {
    "summary", "overview", "general", "information", "informational", "details", "detail",
    "note", "notes", "page", "pages", "section", "part", "chapter", "appendix", "index",
    "glossary", "introduction", "purpose", "scope", "policy", "policies", "statement",
    "regulations", "provision", "provisions", "entitlement", "entitlements", "procedure",
    "procedures", "process", "guideline", "guidelines", "handbook", "manual", "guide",
    "document", "contents", "disclaimer", "notice", "acknowledgement", "welcome", "sample",
    "template", "form", "record", "legal", "employment", "employee", "employees",
    "employer", "employers", "company", "corporate", "personnel", "human", "resources",
    "health", "safety"
}

_QUESTION_STARTERS = {
    "what", "how", "when", "where", "which", "who", "why", "can", "could", "does", "do",
    "is", "are", "will", "would", "should", "may", "must"
}

# Bolt/label markers like '(Ref: HR-POL-2025-04)' never belong in a question.
_PAREN_LABEL_RE = re.compile(r"\s*\([^)]*\)")
_LEADING_NUMBER_RE = re.compile(r"^\s*\d+(?:\.|\)|:)?\s*")
_SPACED_LETTER_RUN_RE = re.compile(r"(?:^|\s)(?:[A-Za-z][\s.\-]+){2,}[A-Za-z](?=$|[^A-Za-z])")


def _filename_stem_tokens(filename: str) -> set[str]:
    """Extracts alphabetical word tokens from the filename (without extension)."""
    stem = (filename or "").rsplit(".", 1)[0].lower()
    stem = re.sub(r"[^a-z0-9]+", " ", stem)
    return {t for t in stem.split() if re.fullmatch(r"[a-z]{2,}", t)}


def _is_spaced_ocr_text(text: str) -> bool:
    """
    Detects template/OCR artifacts written as spaced single letters ('S A M P L E',
    'D R A F T', 'C O N F I D E N T I A L'). These are watermarks, not headings.
    """
    return bool(_SPACED_LETTER_RUN_RE.search(" " + text.strip()))


def _is_document_title(heading: str, filename: str) -> bool:
    """
    True when a heading is really the document/template title rather than a content
    section: it equals the filename stem, is contained in / contains it, or is composed
    entirely of document-describing words.
    """
    h = re.sub(r"[^a-z0-9]+", " ", heading.lower()).strip()
    h_toks = {t for t in h.split() if re.fullmatch(r"[a-z]{2,}", t)}
    if not h_toks:
        return False

    stem_toks = _filename_stem_tokens(filename)
    if stem_toks and (h_toks <= stem_toks or stem_toks <= h_toks):
        return True
    if h_toks <= _DOC_TITLE_WORDS:
        return True
    return False


def _is_meaningful_heading(heading: str, filename: str, full_text: Optional[str]) -> bool:
    """Filters candidate headings down to actual, answerable policy sections."""
    h = (heading or "").strip()
    if len(h) < 3:
        return False
    if _is_spaced_ocr_text(h):
        return False
    if re.fullmatch(r"[\d\s.\-–—/]+", h):
        return False
    if h.lower().strip() in _JUNK_SECTIONS:
        return False

    words = re.findall(r"[a-z]+", h.lower())
    if any(w in _GREETING_WORDS for w in words):
        return False

    toks = extract_query_keywords(h)
    if not toks:
        return False
    if set(toks) <= _FILLER_TOPICS:
        return False
    if _is_document_title(h, filename):
        return False

    # The heading must be grounded in the document body, not an orphaned template line.
    if full_text:
        text_l = full_text.lower()
        if not any(t in text_l for t in toks):
            return False
    return True


def _clean_heading_text(heading: str) -> str:
    """Normalizes a heading for question generation (drops numbering/paren codes, titles)."""
    cleaned = _PAREN_LABEL_RE.sub("", heading)
    cleaned = _LEADING_NUMBER_RE.sub("", cleaned)
    cleaned = " ".join(cleaned.split())
    return cleaned.title()


def _is_valid_question(question: str, filename: str) -> bool:
    """Final quality gate applied to every candidate question."""
    q = (question or "").strip()
    if len(q) < 10 or not q.endswith("?"):
        return False
    if _is_spaced_ocr_text(q):
        return False

    first = q.split()[0].lower()
    if first not in _QUESTION_STARTERS:
        return False

    # Questions referencing the raw file (extension or the whole title) are not useful.
    if re.search(r"\.(?:pdf|txt|docx?|pptx?|xlsx?)\b", q.lower()):
        return False
    stem = " ".join(_filename_stem_tokens(filename))
    if stem and stem in re.sub(r"[^a-z0-9]+", " ", q.lower()):
        return False

    # 'What is the policy on <document title>?' is question-shaped but content-free.
    title_match = re.search(r"policy on\s+(.+?)\?$", q, re.I)
    if title_match and _is_document_title(title_match.group(1), filename):
        return False

    toks = extract_query_keywords(q)
    if len(toks) < 2:
        return False
    if set(toks) <= _FILLER_TOPICS:
        return False
    return True


def _is_near_duplicate(question: str, kept_token_sets: list[set]) -> bool:
    """Rejects questions that are near-paraphrases of already-kept questions."""
    a = set(extract_query_keywords(question))
    if not a:
        return True
    for b in kept_token_sets:
        if not b:
            continue
        inter = len(a & b)
        if inter == 0:
            continue
        # Strong overlap with the smaller question = reworded duplicate.
        if inter / min(len(a), len(b)) >= 0.66:
            return True
        # High Jaccard = essentially the same content words.
        if inter / len(a | b) >= 0.6:
            return True
    return False


def generate_suggested_questions(
    filename: str,
    headings: list[str],
    full_text: Optional[str] = None
) -> list[str]:
    """
    Generates 3 to 5 natural language suggested questions based on:
    1. Pattern matching against extracted headings and section titles
    2. Heading-to-question transformations
    3. Fallback business questions when the document is sparse

    Every candidate passes the filtering gates in `_is_valid_question`,
    `_is_meaningful_heading` and `_is_near_duplicate` before being kept.
    """
    questions: list[str] = []
    seen_lower: set[str] = set()
    kept_token_sets: list[set] = []

    def add_q(q: str) -> None:
        if len(questions) >= 5:
            return
        q = (q or "").strip()
        normalized = q.lower()
        if normalized in seen_lower:
            return
        if not _is_valid_question(q, filename):
            return
        if _is_near_duplicate(q, kept_token_sets):
            return
        questions.append(q)
        seen_lower.add(normalized)
        kept_token_sets.append(set(extract_query_keywords(q)))

    # Candidate headings: real content sections only (no titles, OCR, or filler).
    valid_headings = [
        h for h in (headings or [])
        if _is_meaningful_heading(h, filename, full_text)
    ]
    combined_headings = " ".join(valid_headings).lower()

    # 1. Curated pattern questions derived from content sections.
    for pattern, question in HEADING_TO_QUESTION_PATTERNS:
        if re.search(pattern, combined_headings):
            add_q(question)

    # 2. Pattern questions hinted at by the filename (e.g. a 'Leave Policy' file).
    filename_lower = filename.lower()
    for pattern, question in HEADING_TO_QUESTION_PATTERNS:
        if re.search(pattern, filename_lower):
            add_q(question)

    # 3. Transform filtered headings into natural questions.
    for heading in valid_headings:
        if len(questions) >= 5:
            break
        cleaned = _clean_heading_text(heading)
        if not cleaned or cleaned.lower() in _JUNK_SECTIONS:
            continue
        if cleaned.endswith("?"):
            add_q(cleaned)
        elif len(cleaned.split()) <= 6:
            add_q(f"What is the policy on {cleaned}?")

    # 4. Fallback business questions when few questions could be extracted.
    if len(questions) < 3:
        fallbacks = [
            "What are the key policies, leave entitlements, and employee responsibilities in this document?",
            "What benefits and eligibility rules are described for employees?",
            "What workplace conduct and safety rules are covered?"
        ]
        for f in fallbacks:
            add_q(f)

    logger.info(f"Generated {len(questions)} suggested questions for '{filename}'.")
    return questions[:5]