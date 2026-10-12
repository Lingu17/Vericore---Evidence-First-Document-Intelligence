"""Conservative, deterministic verification: only exact source statements pass.

This checks textual attribution, not the truth of a policy. Paraphrases fail closed.
"""
import re
from app.models.schemas import ChatResponse, ChatStatus, ConfidenceLevel, VerifiedClaim

UNKNOWN = "Information not available in the uploaded documents."


def normalize(text):
    return " ".join(text.lower().split())


def verify_response(response: ChatResponse) -> ChatResponse:
    if response.status == ChatStatus.NOT_FOUND:
        return response.model_copy(update={"answer": UNKNOWN, "sources": [], "claims": [],
                                           "verification_method": "exact_passage"})
    claims = []
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", response.answer.strip()):
        if not sentence.strip():
            continue
        matches = [s.chunk_id for s in response.sources
                   if s.document_id and s.chunk_id and s.filename and s.page > 0
                   and normalize(sentence) in normalize(s.evidence)]
        status = "supported" if matches else "unsupported"
        explanation = "Exact statement found in cited passage." if matches else "No exact passage supports this statement; withheld."
        if not matches:
            # Report partial textual support without promoting it to a factual answer.
            parts = [p.strip().rstrip(".;") for p in re.split(r";|\s+and\s+", sentence)]
            partial = [s.chunk_id for s in response.sources if s.document_id and s.chunk_id
                       and any(len(p.split()) >= 5 and normalize(p) in normalize(s.evidence) for p in parts)]
            if partial:
                status, matches = "partially_supported", partial
                explanation = "Only part of this statement matches a passage; the entire statement was withheld."
            # Numeric alternatives with otherwise identical wording are explicit textual contradictions.
            shape = re.sub(r"\b\d+(?:\.\d+)?\b", "#", normalize(sentence))
            if "#" in shape:
                contradicting = [s.chunk_id for s in response.sources if s.document_id and s.chunk_id
                                 and shape in re.sub(r"\b\d+(?:\.\d+)?\b", "#", normalize(s.evidence))]
                if contradicting:
                    status, matches = "contradicted", contradicting
                    explanation = "The passage specifies a different numeric value; statement withheld."
        claims.append(VerifiedClaim(text=sentence, status=status, source_ids=matches, explanation=explanation))
    supported = [c for c in claims if c.status == "supported"]
    ids = {sid for c in supported for sid in c.source_ids}
    conflicts = []
    for i, first in enumerate(supported):
        for second in supported[i + 1:]:
            shape1 = re.sub(r"\b\d+(?:\.\d+)?\b", "#", normalize(first.text))
            shape2 = re.sub(r"\b\d+(?:\.\d+)?\b", "#", normalize(second.text))
            if shape1 == shape2 and normalize(first.text) != normalize(second.text):
                conflicts.append({"left_chunk_id": first.source_ids[0], "right_chunk_id": second.source_ids[0],
                                  "explanation": "These source statements specify different values. Inspect policy dates and scope before deciding which applies."})
    return response.model_copy(update={
        "answer": "\n".join(c.text for c in supported) if supported else UNKNOWN,
        "status": ChatStatus.ANSWERED if supported else ChatStatus.NOT_FOUND,
        "confidence": response.confidence if supported else ConfidenceLevel.LOW,
        "sources": [s for s in response.sources if s.chunk_id in ids],
        "claims": claims, "verification_method": "exact_passage", "potential_conflicts": conflicts})
