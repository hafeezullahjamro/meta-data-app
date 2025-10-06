"""Search screen for browsing existing metadata XML files."""

from __future__ import annotations

from pathlib import Path

from metadata_app.models.filter_criteria import FilterCriteria
from metadata_app.services.search_service import SearchService


class SearchScreen:
    """Controller handling search inputs and presenting results."""

    def __init__(self, search_service: SearchService) -> None:
        self._search_service = search_service

    def perform_search(
        self,
        folder: Path,
        filters: list[FilterCriteria],
        match_all: bool,
    ) -> list[Path]:
        """Return matching XML file paths."""
        return self._search_service.search(folder=folder, filters=filters, match_all=match_all)

    def clear(self) -> None:
        """Reset form fields and results in the UI."""
        raise NotImplementedError("Bind to UI controls when implementing the view.")

    def show(self) -> None:
        """Display the search screen."""
        raise NotImplementedError("Integrate with the selected UI framework.")

