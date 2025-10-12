"""Metadata schema definition used by the application."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True, slots=True)
class SectionDefinition:
    """Immutable definition of a metadata section."""

    name: str
    color: str
    fields: List[str]


SECTION_COLORS: Dict[str, str] = {
    "Administrative": "#FFA500",  # Orange
    "Technical": "#BEBEBE",  # Gray
    "Capture": "#4682B4",  # Steel blue
    "People/Subjects": "#9370DB",  # Medium purple
    "Rights": "#3CB371",  # Medium sea green
}

DEFAULT_SECTIONS: List[SectionDefinition] = [
    SectionDefinition(
        name="Administrative",
        color=SECTION_COLORS["Administrative"],
        fields=[
            "Title",
            "Alternative Title",
            "Creator",
            "Contributor",
            "Publisher",
            "Description",
            "Language",
            "Identifier",
            "Date",
            "Type",
            "Source",
            "Coverage",
            "Relation",
            "Rights",
        ],
    ),
    SectionDefinition(
        name="Technical",
        color=SECTION_COLORS["Technical"],
        fields=[
            "Format",
            "File Size",
            "Duration",
            "Bitrate",
            "Resolution",
            "Frame Rate",
            "Aspect Ratio",
            "Color Profile",
            "Audio Channels",
            "Sample Rate",
            "File Path",
            "Checksum",
        ],
    ),
    SectionDefinition(
        name="Capture",
        color=SECTION_COLORS["Capture"],
        fields=[
            "Capture Date",
            "Capture Location",
            "Camera/Device",
            "Lens",
            "Exposure",
            "Aperture",
            "ISO",
            "White Balance",
            "Lighting Conditions",
            "Operator",
            "Production Notes",
        ],
    ),
    SectionDefinition(
        name="People/Subjects",
        color=SECTION_COLORS["People/Subjects"],
        fields=[
            "Primary Subjects",
            "Supporting Subjects",
            "Keywords",
            "Tags",
            "People Mentioned",
            "Organizations",
            "Events",
            "Locations Mentioned",
        ],
    ),
    SectionDefinition(
        name="Rights",
        color=SECTION_COLORS["Rights"],
        fields=[
            "Rights Statement",
            "Rights Holder",
            "Access Level",
            "Usage Notes",
            "Expiration Date",
        ],
    ),
]


def get_default_sections() -> List[SectionDefinition]:
    """Return a deep copy of the default section definitions."""
    return [SectionDefinition(section.name, section.color, list(section.fields)) for section in DEFAULT_SECTIONS]

