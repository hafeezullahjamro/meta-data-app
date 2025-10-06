# Architecture Notes

## Screens

1. **HomeScreen** – Lets the user choose the media type and routes to metadata forms.
2. **MetadataFormScreen** – Shows 50+ metadata fields grouped by section; handles XML load/save.
3. **SearchScreen** – Searches across stored XML files with AND/OR filters.
4. **ExportScreen** – Exports one or more records into an Excel workbook with color-coded sections.

## Services

- `XmlService` – Serialize and deserialize PbCore-style XML documents.
- `SearchService` – Load XML files, apply field filters, and return matches.
- `ExportService` – Flatten metadata and generate Excel spreadsheets.
- `MetadataRepository` – Coordinates where XML files are stored on disk.

## Models

- `MetadataRecord` – In-memory representation of a media item, grouped by section.
- `SectionField` – Describes individual fields, labels, and validation rules.
- `FilterCriteria` – Captures search field, keyword, and condition (AND/OR).

## Utilities

- `path_utils` – Resolve data directories, default storage, and user paths.
- `xml_helpers` – Shared XML parsing helpers used by services and UI bindings.

