"""Data structures representing metadata for media items."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from metadata_app.config.schema import get_default_sections


@dataclass(slots=True)
class MetadataSection:
    """Logical grouping of related metadata fields."""

    name: str
    fields: Dict[str, str] = field(default_factory=dict)
    color: str | None = None

    def get_field(self, field_name: str) -> str:
        """Return the value for a named field."""
        return self.fields.get(field_name, "")

    def set_field(self, field_name: str, value: str) -> None:
        """Update a field's value."""
        self.fields[field_name] = value


@dataclass(slots=True)
class MetadataRecord:
    """In-memory representation of a single media item's metadata."""

    title: str
    media_type: str
    sections: List[MetadataSection] = field(default_factory=list)
    media_path: str = ""

    def get_section(self, name: str) -> MetadataSection | None:
        """Return a section by name if it exists."""
        name = name.lower()
        return next((section for section in self.sections if section.name.lower() == name), None)

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        """Return a nested dictionary of sections and their fields."""
        return {section.name: dict(section.fields) for section in self.sections}

    def flatten(self) -> Dict[str, str]:
        """Return a flattened dictionary keyed by 'Section:Field'."""
        flattened: Dict[str, str] = {}
        for section in self.sections:
            for field_name, value in section.fields.items():
                flattened[f"{section.name}:{field_name}"] = value
        return flattened

    @classmethod
    def from_sections(
        cls,
        media_type: str,
        sections: Iterable[MetadataSection],
        title: Optional[str] = None,
    ) -> "MetadataRecord":
        """Create a record from pre-constructed sections."""
        title_value = title or ""
        return cls(title=title_value, media_type=media_type, sections=list(sections))


def create_empty_record(media_type: str) -> MetadataRecord:
    """Return a new metadata record with empty fields based on the default schema."""
    sections = []
    for definition in get_default_sections():
        fields = {field_name: "" for field_name in definition.fields}
        sections.append(
            MetadataSection(
                name=definition.name,
                fields=fields,
                color=definition.color,
            )
        )
    return MetadataRecord(title="", media_type=media_type, sections=sections, media_path="")
