# Metadata Management App

This repository scaffolds a Streamlit-based desktop/web application that helps archivists capture, search, and export media metadata (audio, video, image).

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

## Getting Started

1. Create a virtual environment and install dependencies.
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
2. Launch the Streamlit UI.
   ```bash
   streamlit run src/main.py
   ```
3. Use the sidebar to navigate between Home, Metadata Form, Search, and Export.

All XML files are stored by default under `data/metadata_store`.

## Next Steps

- Extend the metadata schema in `metadata_app/config/schema.py` with additional sections/fields.
- Implement validation rules (required fields, controlled vocabularies).
- Add automated tests covering XML serialization, search filters, and Excel export formatting.
