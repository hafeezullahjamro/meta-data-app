"""Filter structures for searching metadata records."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FilterCriteria:
    """Represents a single metadata field filter."""

    field: str
    keyword: str

