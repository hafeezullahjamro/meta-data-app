"""Application entry point and high-level wiring."""

from metadata_app.ui.screens.home_screen import HomeScreen
from metadata_app.services.xml_service import XmlService
from metadata_app.services.search_service import SearchService
from metadata_app.services.export_service import ExportService


def run_app() -> None:
    """Bootstrap services and launch the home screen."""
    xml_service = XmlService()
    search_service = SearchService(xml_service=xml_service)
    export_service = ExportService(xml_service=xml_service)

    home_screen = HomeScreen(
        xml_service=xml_service,
        search_service=search_service,
        export_service=export_service,
    )
    home_screen.show()


if __name__ == "__main__":
    run_app()

