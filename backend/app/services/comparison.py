"""Compare original indexed passages; changes are potential conflicts, not legal conclusions."""
from difflib import SequenceMatcher
import re
from app.models.schemas import SourceEvidence


def changed_words(before, after):
    # Preserve complete dates, amounts and policy values in the change indicators.
    left = re.findall(r"\S+|\s+", before)
    right = re.findall(r"\S+|\s+", after)
    return [{"before": "".join(left[a:b]), "after": "".join(right[c:d])}
            for tag, a, b, c, d in SequenceMatcher(None, left, right, autojunk=False).get_opcodes()
            if tag != "equal"]


def compare_passages(left: list[SourceEvidence], right: list[SourceEvidence]):
    remaining = list(right)
    changes = []
    for before in left:
        if not remaining:
            changes.append({"kind": "removed", "before": before, "after": None,
                            "explanation": "Passage absent from the second document."})
            continue
        after = max(remaining, key=lambda s: SequenceMatcher(None, before.evidence, s.evidence).ratio())
        similarity = SequenceMatcher(None, before.evidence, after.evidence).ratio()
        if before.evidence.strip() == after.evidence.strip():
            remaining.remove(after)
            continue
        if similarity < 0.45:
            changes.append({"kind": "removed", "before": before, "after": None,
                            "explanation": "No sufficiently similar passage found."})
            continue
        remaining.remove(after)
        important = bool(re.search(r"\b(?:employees?|must|shall|may|required|days?|hours?|payments?|allowed)\b", before.evidence + " " + after.evidence, re.I)) and bool(re.search(r"[.!?]", before.evidence + after.evidence))
        changes.append({"kind": "modified", "before": before, "after": after,
                        "potential_conflict": important,
                        "changes": changed_words(before.evidence, after.evidence),
                        "explanation": "Wording changed. Inspect dates, scope, amounts and obligations in both sources; version changes do not establish a contradiction."})
    for after in remaining:
        changes.append({"kind": "added", "before": None, "after": after,
                        "explanation": "New passage in the second document."})
    return changes
