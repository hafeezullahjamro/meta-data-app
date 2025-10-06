"""Export metadata records into Excel workbooks."""

from __future__ import annotations

from pathlib import Path

from metadata_app.services.xml_service import XmlService


class ExportService:
    """Handles conversion of metadata records to Excel spreadsheets."""

    def __init__(self, xml_service: XmlService) -> None:
        self._xml_service = xml_service

    def export_folder(self, folder: Path, destination: Path) -> Path:
        """Export all XML files in the given folder to a single Excel workbook."""
        # TODO: Implement Excel export (e.g., with openpyxl).
        raise NotImplementedError(
            f"Export not implemented. Source folder: {folder}, destination workbook: {destination}"
        )

