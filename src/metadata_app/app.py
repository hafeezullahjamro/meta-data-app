"""Application entry points."""

from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from metadata_app.ui.streamlit_app import main as streamlit_main


def run_app() -> None:
    """Launch the Streamlit interface."""
    streamlit_main()


if __name__ == "__main__":
    run_app()
