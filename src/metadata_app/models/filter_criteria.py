"""Filter structures for searching metadata records."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FilterCriteria:
    """Represents a single metadata field filter."""

    section: str
    field: str
    keyword: str

    @property
    def key(self) -> str:
        """Return a composite key used for flattened field lookup."""
        return f"{self.section}:{self.field}"
