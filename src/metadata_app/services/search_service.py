"""Search across metadata XML files using filters."""

from __future__ import annotations

from pathlib import Path

from metadata_app.models.filter_criteria import FilterCriteria
from metadata_app.services.xml_service import XmlService


class SearchService:
    """Provides filtering capabilities for metadata records stored as XML."""

    def __init__(self, xml_service: XmlService) -> None:
        self._xml_service = xml_service

    def search(
        self,
        folder: Path,
        filters: list[FilterCriteria],
        match_all: bool,
    ) -> list[Path]:
        """Return XML files that match provided filters."""
        # TODO: Implement search logic (parse XML, evaluate filters).
        raise NotImplementedError(
            f"Search is not implemented yet. Folder: {folder}, Filters: {filters}, match_all={match_all}"
        )

