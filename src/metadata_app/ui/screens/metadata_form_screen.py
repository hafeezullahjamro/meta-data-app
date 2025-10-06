"""Metadata form screen for creating and editing media metadata records."""

from __future__ import annotations

from metadata_app.models.metadata_record import MetadataRecord
from metadata_app.services.xml_service import XmlService


class MetadataFormScreen:
    """Controller for the form that captures metadata across all sections."""

    def __init__(self, xml_service: XmlService) -> None:
        self._xml_service = xml_service

    def load_from_file(self, path: str) -> MetadataRecord:
        """Load an XML file and return its metadata record."""
        return self._xml_service.load_record(path)

    def save_to_file(self, record: MetadataRecord, path: str | None = None) -> str:
        """Persist the provided record and return the path written to."""
        return self._xml_service.save_record(record, path_hint=path)

    def clear_form(self) -> None:
        """Clear all bound fields in the UI."""
        raise NotImplementedError("Attach to UI widget bindings.")

    def show(self) -> None:
        """Display the form screen."""
        raise NotImplementedError("Integrate with the chosen UI framework.")

