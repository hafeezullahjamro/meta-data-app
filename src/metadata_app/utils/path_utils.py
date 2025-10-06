"""Path helper utilities."""

from __future__ import annotations

from pathlib import Path

DEFAULT_STORAGE_DIR = Path("data/metadata_store")


def ensure_directory(path: Path | None) -> Path:
    """Ensure the directory exists and return it."""
    resolved = path or DEFAULT_STORAGE_DIR
    resolved = resolved if resolved.is_absolute() else Path.cwd() / resolved
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved

