"""Data structures representing metadata for media items."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class MetadataSection:
    """Logical grouping of related metadata fields."""

    name: str
    fields: Dict[str, str] = field(default_factory=dict)
    color: str | None = None


@dataclass(slots=True)
class MetadataRecord:
    """In-memory representation of a single media item's metadata."""

    title: str
    media_type: str
    sections: List[MetadataSection] = field(default_factory=list)

    def get_section(self, name: str) -> MetadataSection | None:
        """Return a section by name if it exists."""
        name = name.lower()
        return next((section for section in self.sections if section.name.lower() == name), None)

