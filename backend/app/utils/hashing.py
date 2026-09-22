"""
File hashing utility for document deduplication.
Computes SHA-256 hash to prevent redundant re-indexing and token usage.
"""

import hashlib


def calculate_sha256(content: bytes) -> str:
    """Computes SHA-256 hash string for raw file bytes."""
    sha256_hash = hashlib.sha256()
    sha256_hash.update(content)
    return sha256_hash.hexdigest()
