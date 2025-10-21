"""Metadata schema definition used by the application."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


@dataclass(frozen=True, slots=True)
class SectionDefinition:
    """Immutable definition of a metadata section."""

    name: str
    color: str
    fields: List[str]


SECTION_COLORS: Dict[str, str] = {
    "Administrative": "#FFA500",  # Orange
    "Descriptive": "#9370DB",  # Medium purple
    "Technical Original": "#BEBEBE",  # Gray
    "Technical Master": "#708090",  # Slate gray
    "Access Copy": "#4682B4",  # Steel blue
    "Technical Access Copy": "#4682B4",
    "Capture Chain": "#6A5ACD",  # Slate blue
    "Preservation": "#3CB371",  # Sea green
}


def _make_sections(definitions: Iterable[Tuple[str, str, Iterable[str]]]) -> List[SectionDefinition]:
    sections: List[SectionDefinition] = []
    for name, color_key, fields in definitions:
        sections.append(
            SectionDefinition(
                name=name,
                color=SECTION_COLORS[color_key],
                fields=list(fields),
            )
        )
    return sections


VIDEO_AUDIO_SECTIONS: List[SectionDefinition] = _make_sections(
    [
        (
            "Administrative",
            "Administrative",
            [
                "Title",
                "Identifier",
                "CollectionName",
                "AcquisitionMethod",
                "DonorSourceContact",
                "Contributors",
                "DateOfCreation",
                "RightsHolder",
                "AccessConditions",
                "HoldingInstitution",
                "CopyRightStatus",
                "UserRestrictions",
                "QCStatus",
                "QCReport",
                "QCOperator",
            ],
        ),
        (
            "Descriptive",
            "Descriptive",
            [
                "Identifier",
                "Title",
                "Subject",
                "Summary",
                "KeyWords",
                "Genre",
                "Creator",
                "Languages",
                "GeographicLocation",
                "EventDate",
                "PeopleInVideo",
            ],
        ),
        (
            "Technical Original",
            "Technical Original",
            [
                "SignalType",
                "FormatLevel",
                "Format",
                "SignalStandard",
                "RecordingMode",
                "TapeLengthMinutes",
                "AudioChannels",
                "ConditionNotes",
                "OriginalLabel",
                "FormatNotes",
            ],
        ),
        (
            "Technical Master",
            "Technical Master",
            [
                "FileFormat",
                "BitDepth",
                "Resolution",
                "FrameRate",
                "AspectRatio",
                "WidthHeight",
                "ScanType",
                "ColorSubSampling",
                "ColorSpace",
                "AudioFormat",
                "AudioSampleRateKHz",
                "AudioBitDepth",
                "AudioChannelsCount",
                "DataRate",
                "Duration",
                "FileSizeGB",
                "Checksums",
                "EmbeddedMetadataSchema",
            ],
        ),
        (
            "Access Copy",
            "Access Copy",
            [
                "Container",
                "BitDepth",
                "Resolution",
                "AudioChannel",
                "Duration",
                "DataRate",
                "FileSizeGB",
            ],
        ),
        (
            "Capture Chain",
            "Capture Chain",
            [
                "DigitizationDate",
                "OperatorName",
                "PlaybackDevice",
                "TBCModel",
                "FrameSynchronizer",
                "CaptureHardware",
                "CaptureSoftware",
                "SignalPathNotes",
                "AudioDelayApplied",
                "IssuesDuringCapture",
            ],
        ),
        (
            "Preservation",
            "Preservation",
            [
                "SourceProvenance",
                "PreservationActions",
                "MigrationHistory",
                "ErrorReports",
                "StorageLocation",
                "BackupDetails",
            ],
        ),
    ]
)

IMAGE_SECTIONS: List[SectionDefinition] = _make_sections(
    [
        (
            "Administrative",
            "Administrative",
            [
                "Title",
                "Identifier",
                "CollectionName",
                "AcquisitionMethod",
                "DonorSourceContact",
                "Contributors",
                "DateOfCreation",
                "RightsHolder",
                "AccessConditions",
                "HoldingInstitution",
                "CopyRightStatus",
                "UserRestrictions",
            ],
        ),
        (
            "Descriptive",
            "Descriptive",
            [
                "Identifier",
                "Title",
                "Keywords",
                "Genre",
                "Creator",
                "Languages",
                "GeographicLocation",
                "EventDate",
                "PeopleInPhoto",
                "Description",
            ],
        ),
        (
            "Technical Original",
            "Technical Original",
            [
                "Format",
                "ConditionNotes",
            ],
        ),
        (
            "Technical Master",
            "Technical Master",
            [
                "FileFormat",
                "BitDepth",
                "WidthHeight",
                "ColorSpace",
                "DPI",
                "FileSizeGB",
                "Checksum",
            ],
        ),
        (
            "Technical Access Copy",
            "Technical Access Copy",
            [
                "FileFormat",
                "BitDepth",
                "WidthHeight",
                "DPI",
                "FileSizeGB",
            ],
        ),
        (
            "Capture Chain",
            "Capture Chain",
            [
                "DigitizationDate",
                "OperatorName",
                "ScannerModel",
            ],
        ),
        (
            "Preservation",
            "Preservation",
            [
                "ErrorReports",
                "StorageLocation",
                "BackupDetails",
            ],
        ),
    ]
)

SCHEMA_BY_MEDIA_TYPE: Dict[str, List[SectionDefinition]] = {
    "video": VIDEO_AUDIO_SECTIONS,
    "audio": VIDEO_AUDIO_SECTIONS,
    "image": IMAGE_SECTIONS,
}


def get_default_sections(media_type: str) -> List[SectionDefinition]:
    """Return a deep copy of the section definitions for the given media type."""
    sections = SCHEMA_BY_MEDIA_TYPE.get(media_type.lower(), VIDEO_AUDIO_SECTIONS)
    return [SectionDefinition(section.name, section.color, list(section.fields)) for section in sections]


def get_all_section_field_pairs() -> List[Tuple[str, str]]:
    """Return unique (section, field) pairs across every media type."""
    seen = set()
    pairs: List[Tuple[str, str]] = []
    for sections in SCHEMA_BY_MEDIA_TYPE.values():
        for section in sections:
            for field in section.fields:
                key = (section.name, field)
                if key not in seen:
                    seen.add(key)
                    pairs.append(key)
    return pairs
