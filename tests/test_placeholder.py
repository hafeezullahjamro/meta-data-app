"""Placeholder test to verify the package imports correctly."""

from pathlib import Path
import sys


def test_import_package() -> None:
    project_root = Path(__file__).resolve().parents[1]
    src_dir = project_root / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    import metadata_app  # noqa: F401
