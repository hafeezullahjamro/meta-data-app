# Metadata Management App

This repository contains a Streamlit-based desktop/web application that helps archivists capture, search, and export media metadata (audio, video, image). It is designed to support full-roundtrips: load or upload a media file, view or edit every metadata field, save an updated XML record, search across existing XML files (including keyword matches inside field content), and export collections to Excel.

## Project Layout

- `src/metadata_app/` – application source code.
  - `ui/screens/` – individual UI screens (home, metadata form, search, export).
  - `ui/components/` – reusable UI widgets (notifications, dialogs, etc.).
  - `services/` – XML persistence, search, and export services.
  - `models/` – domain models describing metadata records and search criteria.
  - `utils/` – helper utilities shared across modules.
- `data/samples/` – placeholder for example XML files.
- `docs/` – product notes, specs, and wireframes.
- `tests/` – automated tests.

## Requirements

- Python 3.10+
- Recommended: virtual environment (`venv`, `conda`, etc.)
- Optional (for Excel export): Microsoft Excel or a compatible viewer to open the generated `.xlsx` files

Install the app-specific dependencies with:

```bash
pip install -r requirements.txt
```

Key dependencies:

- `streamlit` – UI layer
- `pandas` – search/export presentation
- `openpyxl` – Excel writer

## Running the App

1. From the project root (`c:\Projects\meta data app`), activate your environment (optional but recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # PowerShell / CMD on Windows
   ```
2. Install requirements if you have not already:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the Streamlit UI:
   ```bash
   streamlit run src/main.py
   ```
4. Streamlit prints a local URL (default `http://localhost:8501`). Open it in your browser.
5. Use the sidebar navigation (Home, Metadata Form, Search, Export) to move between screens.

Default storage locations (created automatically when needed):

- Metadata XML: `data/metadata_store/`
- Uploaded media files: `data/media_uploads/<media_type>/`

## Features

- **Home**  
  Choose the media type (Video / Audio / Image) before entering the metadata form.
- **Metadata Form**  
  - Load metadata by pasting a path to a local media file and clicking **Load Media**.  
  - Upload a media file directly; the app saves it under `data/media_uploads/<media_type>/` and loads metadata immediately.  
  - The form pre-fills fields when metadata already exists (based on the stored XML).  
  - Edit metadata inside a single Streamlit form; press **Save Metadata** to write out an updated XML file.  
  - Download buttons appear after saving so you can grab the XML or the current media file right from the UI.
- **Search**  
  - Enter a folder (default is `data/metadata_store`).  
  - Type a keyword in **Keyword (matches any field)** to search across all sections and metadata values (including title, media type, file name, and XML contents).  
  - Optionally add structured filters by selecting section/field pairs and keywords.  
  - Choose **Match Any** (logical OR) or **Match All** (logical AND) for the filters.  
  - Results list the title, media type, and file path; click **Open** to load/edit a record directly in the form.
- **Export**  
  - Choose a folder containing XML files and a destination workbook path.  
  - Hit **Export to Excel** to produce a color-coded Excel spreadsheet with sectioned metadata and a sequence column.

## Using the Metadata Form

1. **Load or Upload Media**  
   - Paste an existing media file path and click **Load Media**, or  
   - Upload a new file (the app saves it and loads the form automatically).
2. **Review Existing Metadata**  
   - If a matching XML file exists in `data/metadata_store`, fields are pre-populated.  
   - No XML yet? The form is populated with empty defaults defined in `metadata_app/config/schema.py`.
3. **Edit and Save**  
   - Update fields inside the expandable sections.  
   - Hit **Save Metadata** (inside the form) to create/update an XML record.  
   - The XML is stored under `data/metadata_store`. The file name is derived from the title and media type.
4. **Download (Optional)**  
   - After saving, use the download buttons to download the XML and/or the media file.

## Searching Metadata

- **Global keyword**: Enter any value in the `Keyword (matches any field)` input to search across *all* metadata content (flattened fields + XML file names + titles).
- **Structured filters**: Add up to five section-specific filters for pinpoint matches.
- **Match mode**: Select “Match Any” or “Match All” to control how structured filters combine. The global keyword is applied after filters succeed.
- **Open from results**: Clicking an entry loads it into the form for immediate editing.

## Exporting Metadata

- Provide the source folder (default `data/metadata_store`) and destination Excel file path.  
- Excel export groups sections with distinct colors, adds sequence numbers, and includes every metadata field.  
- Useful for reporting, bulk review, or archival copies.

## Schema Customisation

- `metadata_app/config/schema.py` defines the default sections, colors, and fields.  
- Add/remove sections or fields by editing `DEFAULT_SECTIONS`.  
- The UI automatically adapts to the schema changes the next time it runs.

## Troubleshooting Tips

- **No metadata loads**: Confirm an XML file exists for the media under `data/metadata_store`. If not, save once to generate it.  
- **Search returns empty**: Verify the folder path and ensure XML content contains the keyword. Remember that global keyword search uses lowercase comparisons.  
- **Streamlit issues**: Restart with `Ctrl+C` and re-run `streamlit run src/main.py`. Ensure the virtual environment is active so dependencies are recognised.

## Development Notes

- Python package structure lives under `src/metadata_app`.  
- Tests (currently a placeholder) live under `tests/`.  
- Feel free to extend the test suite (e.g., add coverage for search/excel export) as you expand the app.

## Contributing

1. Fork or branch the repository.  
2. Run `pip install -r requirements.txt`.  
3. Make your changes; add tests if possible.  
4. Run `pytest`.  
5. Submit a pull request or push your branch.

## License

This project is released under the MIT License. See the `LICENSE` file for details.

## Next Steps

- Extend the metadata schema in `metadata_app/config/schema.py` with additional sections/fields.
- Implement validation rules (required fields, controlled vocabularies).
- Add automated tests covering XML serialization, search filters, and Excel export formatting.
