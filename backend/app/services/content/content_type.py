"""Resolve upload content types from filename when browsers send generic MIME types."""

from __future__ import annotations

import mimetypes
from pathlib import Path

TEXT_EXTENSIONS = frozenset(
    {
        ".txt",
        ".md",
        ".markdown",
        ".csv",
        ".json",
        ".xml",
        ".html",
        ".htm",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".py",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".cs",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".sql",
        ".yaml",
        ".yml",
        ".log",
        ".rtf",
    },
)

GENERIC_MIME = frozenset(
    {
        "",
        "application/octet-stream",
        "binary/octet-stream",
        "application/x-download",
    },
)


def resolve_content_type(filename: str, declared: str | None) -> str:
    """Pick the best MIME type for ingestion and validation."""
    declared = (declared or "").strip().lower()
    if declared and declared not in GENERIC_MIME:
        return declared

    guessed, _ = mimetypes.guess_type(filename)
    if guessed:
        return guessed

    ext = Path(filename or "").suffix.lower()
    if ext in TEXT_EXTENSIONS:
        return "text/plain"

    return declared or "application/octet-stream"


def is_allowed_material_type(content_type: str, filename: str) -> bool:
    ct = resolve_content_type(filename, content_type)
    allowed = frozenset(
        {
            "application/pdf",
            "text/plain",
            "text/markdown",
            "text/csv",
            "text/html",
            "application/json",
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/gif",
        },
    )
    if ct in allowed:
        return True
    if ct.startswith("text/"):
        return True
    return False
