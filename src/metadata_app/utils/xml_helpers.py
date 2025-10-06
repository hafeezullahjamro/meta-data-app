"""Shared XML parsing helpers."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Iterable


def find_text(element: ET.Element, path: str) -> str | None:
    """Return the trimmed text for the first matching child path."""
    target = element.find(path)
    if target is None or target.text is None:
        return None
    return target.text.strip()


def iter_children(element: ET.Element, tag: str) -> Iterable[ET.Element]:
    """Yield children with a specific tag."""
    return (child for child in element.findall(tag))

