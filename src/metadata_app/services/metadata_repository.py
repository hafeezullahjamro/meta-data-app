"""Manage the storage location for metadata XML files."""

from __future__ import annotations

from pathlib import Path

from metadata_app.utils.path_utils import ensure_directory


class MetadataRepository:
    """Resolves directories for metadata files and handles naming."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = ensure_directory(base_dir)

    @property
    def base_dir(self) -> Path:
        """Return the root directory used for metadata storage."""
        return self._base_dir

    def get_record_path(self, title: str, media_type: str) -> Path:
        """Build a file path for a record based on title and media type."""
        safe_title = "".join(ch for ch in title if ch.isalnum() or ch in (" ", "-", "_")).strip()
        safe_title = safe_title.replace(" ", "_") or "untitled"
        base_filename = f"{media_type.lower()}_{safe_title}".lower()

        candidate = self._base_dir / f"{base_filename}.xml"
        suffix = 1
        while candidate.exists():
            candidate = self._base_dir / f"{base_filename}_{suffix}.xml"
            suffix += 1
        return candidate
