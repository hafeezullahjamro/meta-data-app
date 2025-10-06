"""Home screen for selecting the media type workflow."""

from __future__ import annotations

from metadata_app.services.xml_service import XmlService
from metadata_app.services.search_service import SearchService
from metadata_app.services.export_service import ExportService


class HomeScreen:
    """Simple controller for the opening screen."""

    def __init__(
        self,
        xml_service: XmlService,
        search_service: SearchService,
        export_service: ExportService,
    ) -> None:
        self._xml_service = xml_service
        self._search_service = search_service
        self._export_service = export_service

    def show(self) -> None:
        """Display the screen (placeholder for GUI integration)."""
        raise NotImplementedError(
            "Integrate with the UI framework (e.g., PySide6) before showing the screen."
        )

    def open_metadata_form(self, media_type: str) -> None:
        """Navigate to the metadata form for the selected media type."""
        raise NotImplementedError("Route to MetadataFormScreen once the UI is wired.")

    def open_search(self) -> None:
        """Navigate to the search screen."""
        raise NotImplementedError("Route to SearchScreen once the UI is wired.")

    def open_export(self) -> None:
        """Navigate to the export screen."""
        raise NotImplementedError("Route to ExportScreen once the UI is wired.")

