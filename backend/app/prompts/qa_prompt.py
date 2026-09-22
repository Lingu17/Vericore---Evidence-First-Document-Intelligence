"""
Grounded QA Prompts for DocuPilot.
Extremely minimal and token-optimized: zero instruction bloat, zero CoT overhead, strict JSON schema.
"""

from app.models.schemas import SourceEvidence


SYSTEM_PROMPT = """You answer only from the provided evidence.
If the evidence does not support the answer, return not_found.
Return valid structured JSON.
Cite only provided source IDs in source_ids.
Be concise (1-3 sentences).

Schema:
{"status": "answered" | "not_found", "answer": "...", "source_ids": ["..."]}"""


def build_context_block(sources: list[SourceEvidence]) -> str:
    """Formats selected evidence chunks with minimal overhead."""
    blocks: list[str] = []
    for s in sources:
        section_part = f", Section: {s.section}" if s.section and s.section != "General" else ""
        blocks.append(
            f"[SOURCE_ID={s.chunk_id}]\n"
            f"Document: {s.filename} (Page {s.page}{section_part})\n"
            f"Evidence: {s.evidence.strip()}"
        )
    return "\n\n".join(blocks)


def build_user_prompt(
    question: str,
    sources: list[SourceEvidence],
    conversation_summary: str = ""
) -> str:
    """Builds a compact user prompt containing only question and trimmed evidence."""
    context_str = build_context_block(sources)

    if conversation_summary.strip():
        return f"""PREVIOUS CONTEXT:
{conversation_summary.strip()}

QUESTION:
{question.strip()}

EVIDENCE:
{context_str}"""

    return f"""QUESTION:
{question.strip()}

EVIDENCE:
{context_str}"""
