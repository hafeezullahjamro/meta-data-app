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
        text_query: str | None = None,
    ) -> List[Tuple[Path, MetadataRecord]]:
        """Return metadata records that match provided filters."""
        folder = Path(folder)
        if not folder.exists():
            return []

        matched: List[Tuple[Path, MetadataRecord]] = []

        candidates = sorted(folder.glob("*.xml"))
        text_query_normalized = (text_query or "").strip().lower()

        for xml_file in candidates:
            try:
                record = self._xml_service.load_record(xml_file)
            except Exception:
                continue

            flattened = record.flatten()

            # Evaluate field-specific filters first (if any were supplied).
            filters_match = True
            if filters:
                evaluations = []
                for criteria in filters:
                    value = flattened.get(criteria.key, "")
                    keyword = criteria.keyword.strip().lower()
                    evaluations.append(keyword in value.lower())

                filters_match = (match_all and all(evaluations)) or (not match_all and any(evaluations))

            if not filters_match:
                continue

            # When a free-text query is provided, match it against every value in the record.
            if text_query_normalized:
                aggregated_values = [
                    record.title or "",
                    record.media_type or "",
                    xml_file.stem,
                    xml_file.name,
                ]
                aggregated_values.extend(flattened.values())
                if not any(text_query_normalized in (value or "").lower() for value in aggregated_values):
                    continue

            matched.append((xml_file, record))

        return matched
