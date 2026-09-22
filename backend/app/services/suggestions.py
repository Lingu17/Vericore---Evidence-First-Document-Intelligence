"""
Smart Suggested Questions Generator.
Generates 3-5 useful, high-impact business questions from document structure, headings,
and topics with zero mandatory LLM token overhead.
"""

import re
from typing import Optional
from app.core.logging import logger


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


def generate_suggested_questions(
    filename: str,
    headings: list[str],
    full_text: Optional[str] = None
) -> list[str]:
    """
    Generates 3 to 5 natural language suggested questions based on:
    1. Pattern matching against extracted headings and section titles
    2. Heading-to-question transformations
    3. Document filename hints
    """
    questions: list[str] = []
    seen = set()

    def add_q(q: str):
        normalized = q.strip().lower()
        if normalized not in seen and len(questions) < 5:
            seen.add(normalized)
            questions.append(q)

    # 1. Check patterns across headings
    combined_headings = " ".join(headings).lower()
    for pattern, question in HEADING_TO_QUESTION_PATTERNS:
        if re.search(pattern, combined_headings):
            add_q(question)

    # 2. Check patterns against filename
    filename_lower = filename.lower()
    for pattern, question in HEADING_TO_QUESTION_PATTERNS:
        if re.search(pattern, filename_lower):
            add_q(question)

    # 3. Transform headings into questions
    for heading in headings:
        if len(questions) >= 5:
            break
        h_clean = heading.strip()
        # Skip generic headings
        if h_clean.lower() in {"overview", "introduction", "table of contents", "summary", "general"}:
            continue

        # Convert heading into question format
        if not h_clean.endswith("?"):
            if any(h_clean.lower().startswith(w) for w in ["how", "what", "can", "when", "is", "where"]):
                add_q(f"{h_clean}?")
            elif len(h_clean.split()) <= 6:
                add_q(f"What is the policy on {h_clean}?")
        else:
            add_q(h_clean)

    # 4. Fallback business questions if few questions could be extracted
    if len(questions) < 3:
        fallbacks = [
            f"What are the main terms and policies detailed in {filename}?",
            f"What are the key employee responsibilities in {filename}?",
            f"What eligibility criteria are specified in {filename}?"
        ]
        for f in fallbacks:
            add_q(f)

    logger.info(f"Generated {len(questions)} suggested questions for '{filename}'.")
    return questions[:5]
