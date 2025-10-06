"""Read and write PbCore-compliant metadata XML files."""

from __future__ import annotations

from pathlib import Path

from metadata_app.models.metadata_record import MetadataRecord
from metadata_app.services.metadata_repository import MetadataRepository


class XmlService:
    """Handles serialization of metadata records."""

    def __init__(self, repository: MetadataRepository | None = None) -> None:
        self._repository = repository or MetadataRepository()

    def save_record(self, record: MetadataRecord, path_hint: str | Path | None = None) -> str:
        """Persist a metadata record to XML and return the path written."""
        path = self._resolve_path(record, path_hint)
        # TODO: Implement XML serialization logic.
        raise NotImplementedError(f"Serialization not yet implemented. Target path: {path}")

    def load_record(self, path: str | Path) -> MetadataRecord:
        """Load an XML file from disk."""
        # TODO: Implement XML parsing logic.
        raise NotImplementedError(f"Loading not yet implemented. Source path: {path}")

    def _resolve_path(self, record: MetadataRecord, path_hint: str | Path | None) -> Path:
        """Determine the output path for the record."""
        if path_hint:
            return Path(path_hint)
        return self._repository.get_record_path(title=record.title, media_type=record.media_type)

