# Metadata Management App

This repository scaffolds a desktop application that helps archivists capture, search, and export media metadata (audio, video, image).

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

1. Create a virtual environment and install dependencies once they are defined in `requirements.txt`.
2. Use `src/metadata_app/app.py` as the entry point for the UI shell.
3. Fill out services and UI screens according to the functional guide provided by the product brief.

## Next Steps

- Implement the UI using your preferred toolkit (e.g., PySide6, Tkinter, Electron).
- Flesh out XML read/write logic in `services/xml_service.py`.
- Add search indexing in `services/search_service.py`.
- Implement Excel export via `services/export_service.py` (e.g., using `openpyxl`).

