"""Export screen for generating Excel reports from metadata records."""

from __future__ import annotations

from pathlib import Path

from metadata_app.services.export_service import ExportService


class ExportScreen:
    """Controller for configuring and running Excel exports."""

    def __init__(self, export_service: ExportService) -> None:
        self._export_service = export_service

    def export_folder(self, folder: Path, destination: Path) -> Path:
        """Export all XML files in the provided folder."""
        return self._export_service.export_folder(folder=folder, destination=destination)

    def show(self) -> None:
        """Display the export screen."""
        raise NotImplementedError("Integrate with the chosen UI framework.")

