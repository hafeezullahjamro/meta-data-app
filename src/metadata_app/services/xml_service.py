"""Read and write PbCore-compliant metadata XML files."""

from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

from metadata_app.models.metadata_record import MetadataRecord, MetadataSection
from metadata_app.services.metadata_repository import MetadataRepository


class XmlService:
    """Handles serialization of metadata records."""

    def __init__(self, repository: MetadataRepository | None = None) -> None:
        self._repository = repository or MetadataRepository()
        self._repository.base_dir.mkdir(parents=True, exist_ok=True)

    def save_record(self, record: MetadataRecord, path_hint: str | Path | None = None) -> str:
        """Persist a metadata record to XML and return the path written."""
        path = self._resolve_path(record, path_hint)

        root = ET.Element("metadata", mediaType=record.media_type)
        title_element = ET.SubElement(root, "title")
        title_element.text = record.title.strip()

        media_element = ET.SubElement(root, "media")
        media_path_element = ET.SubElement(media_element, "path")
        media_path_element.text = record.media_path

        sections_element = ET.SubElement(root, "sections")
        for section in record.sections:
            section_attrs = {"name": section.name}
            if section.color:
                section_attrs["color"] = section.color
            section_element = ET.SubElement(sections_element, "section", section_attrs)
            for field_name, value in section.fields.items():
                field_element = ET.SubElement(section_element, "field", name=field_name)
                field_element.text = value or ""

        path.parent.mkdir(parents=True, exist_ok=True)
        tree = ET.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)
        return str(path)

    def load_record(self, path: str | Path) -> MetadataRecord:
        """Load an XML file from disk."""
        xml_path = Path(path)
        tree = ET.parse(xml_path)
        root = tree.getroot()

        media_type = root.attrib.get("mediaType", "")
        title = root.findtext("title", default="")

        sections: list[MetadataSection] = []
        sections_element = root.find("sections")
        if sections_element is not None:
            for section_element in sections_element.findall("section"):
                section_name = section_element.attrib.get("name", "Unknown")
                section_color = section_element.attrib.get("color")
                fields: dict[str, str] = {}
                for field_element in section_element.findall("field"):
                    field_name = field_element.attrib.get("name", "Unnamed Field")
                    fields[field_name] = (field_element.text or "").strip()
                sections.append(
                    MetadataSection(
                        name=section_name,
                        color=section_color,
                        fields=fields,
                    )
                )

        record = MetadataRecord(title=title, media_type=media_type, sections=sections)
        media_path_element = root.find("media/path")
        if media_path_element is not None and media_path_element.text:
            record.media_path = media_path_element.text.strip()
        return record

    def find_metadata_for_media(self, media_path: Path) -> tuple[Path, MetadataRecord] | None:
        """Return the XML path and record for a given media file, if it exists."""
        target = Path(media_path).expanduser().resolve()
        for xml_file in sorted(self._repository.base_dir.glob("*.xml")):
            try:
                record = self.load_record(xml_file)
            except Exception:
                continue
            if not record.media_path:
                continue
            try:
                record_media_path = Path(record.media_path).expanduser().resolve()
            except Exception:
                record_media_path = Path(record.media_path)
            if record_media_path == target:
                return xml_file, record
        return None

    def _resolve_path(self, record: MetadataRecord, path_hint: str | Path | None) -> Path:
        """Determine the output path for the record."""
        if path_hint:
            return Path(path_hint)
        return self._repository.get_record_path(title=record.title, media_type=record.media_type)

    @property
    def repository(self) -> MetadataRepository:
        """Expose the underlying metadata repository."""
        return self._repository
