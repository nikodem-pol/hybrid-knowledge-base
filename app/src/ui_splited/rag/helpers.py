"""
Small utility functions used across the app.
"""

import hashlib


def file_id(name: str, size: int) -> str:
    """Deterministic short hash for deduplication."""
    return hashlib.md5(f"{name}{size}".encode()).hexdigest()[:10]


def format_size(b: int) -> str:
    """Human-readable byte size."""
    for u in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} TB"
