"""Search across metadata XML files using filters."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from metadata_app.models.filter_criteria import FilterCriteria
from metadata_app.models.metadata_record import MetadataRecord
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
    ) -> List[Tuple[Path, MetadataRecord]]:
        """Return metadata records that match provided filters."""
        folder = Path(folder)
        if not folder.exists():
            return []

        matched: List[Tuple[Path, MetadataRecord]] = []

        candidates = sorted(folder.glob("*.xml"))
        for xml_file in candidates:
            try:
                record = self._xml_service.load_record(xml_file)
            except Exception:
                continue

            if not filters:
                matched.append((xml_file, record))
                continue

            flattened = record.flatten()
            evaluations = []
            for criteria in filters:
                value = flattened.get(criteria.key, "")
                keyword = criteria.keyword.strip().lower()
                evaluations.append(keyword in value.lower())

            if (match_all and all(evaluations)) or (not match_all and any(evaluations)):
                matched.append((xml_file, record))

        return matched
