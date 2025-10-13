"""Streamlit-based user interface for the metadata management application."""

from __future__ import annotations

import datetime
import tempfile
from pathlib import Path
from typing import Iterable, List, Tuple

import pandas as pd
import streamlit as st

from metadata_app.config import DEFAULT_SECTIONS
from metadata_app.models import FilterCriteria, MetadataRecord, MetadataSection, create_empty_record
from metadata_app.services import ExportService, SearchService, XmlService

MEDIA_TYPES = ["Video", "Audio", "Image"]
MEDIA_EXTENSIONS = {
    "Video": ["mp4", "mov", "avi", "mkv", "m4v"],
    "Audio": ["mp3", "wav", "aac", "flac", "m4a"],
    "Image": ["jpg", "jpeg", "png", "tif", "tiff", "bmp"],
}
SCREEN_ORDER = ["home", "form", "search", "export", "exit"]
TITLE_FIELD_KEY = "field::Administrative::Title"
LONG_TEXT_FIELDS = {"Description", "Production Notes", "Usage Notes"}
MEDIA_PATH_KEY = "current_media_path"
MEDIA_PATH_INPUT_KEY = "media_path_input"
MEDIA_PATH_INPUT_PENDING_KEY = "media_path_input_pending"
MEDIA_UPLOAD_TOKEN_KEY = "media_upload_token"
FLASH_MESSAGE_KEY = "flash_message"
FORM_SEED_TOKEN_KEY = "form_seed_token"
FORM_RENDER_TOKEN_KEY = "form_render_token"


def field_key(section_name: str, field_name: str) -> str:
    """Return a stable key name for binding Streamlit inputs."""
    return f"field::{section_name}::{field_name}"


def default_upload_directory(media_type: str) -> Path:
    """Return the default upload directory for a media type."""
    return Path("data/media_uploads") / media_type.lower()


def is_date_field(field_name: str) -> bool:
    """Return True if the field likely represents a date."""
    return "date" in field_name.lower()


def parse_iso_date(value: str) -> datetime.date | None:
    """Attempt to parse an ISO date string."""
    value = value.strip()
    if not value:
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def ensure_default_fields(record: MetadataRecord) -> MetadataRecord:
    """Populate missing sections/fields based on the default schema."""
    section_map = {section.name: section for section in record.sections}
    normalized_sections: List[MetadataSection] = []

    for definition in DEFAULT_SECTIONS:
        existing = section_map.get(definition.name)
        if existing:
            for field in definition.fields:
                existing.fields.setdefault(field, "")
            if not existing.color:
                existing.color = definition.color
            normalized_sections.append(existing)
        else:
            normalized_sections.append(
                MetadataSection(
                    name=definition.name,
                    color=definition.color,
                    fields={field: "" for field in definition.fields},
                )
            )

    record.sections = normalized_sections
    return record


def set_record_title(record: MetadataRecord, title: str) -> None:
    """Set the record title and mirror it into the Administrative section."""
    record.title = title
    admin_section = record.get_section("Administrative")
    if admin_section:
        admin_section.set_field("Title", title)


def media_upload_extensions(media_type: str) -> List[str]:
    """Return allowed upload extensions for a media type."""
    return MEDIA_EXTENSIONS.get(media_type, [])


def push_flash(message: str, level: str = "info") -> None:
    """Store a flash message for display on the next UI run."""
    st.session_state[FLASH_MESSAGE_KEY] = (level, message)


def pop_flash() -> None:
    """Display and clear any queued flash message."""
    flash = st.session_state.get(FLASH_MESSAGE_KEY)
    if not flash:
        return

    level, message = flash
    notifier = getattr(st, level, st.info)
    notifier(message)
    st.session_state[FLASH_MESSAGE_KEY] = None


def load_media_from_disk(media_path: Path, xml_service: XmlService) -> None:
    """Load metadata for a given media file, creating a blank record if needed."""
    if not media_path.exists():
        st.error(f"Media file not found at `{media_path}`.")
        return

    record: MetadataRecord
    metadata_path: Path | None = None

    try:
        existing = xml_service.find_metadata_for_media(media_path)
    except Exception as exc:
        st.error(f"Unable to load metadata for `{media_path.name}`: {exc}")
        return

    if existing:
        metadata_path, record = existing
        if not record.media_path:
            record.media_path = str(media_path)
        message = f"Loaded metadata for `{media_path.name}`."
    else:
        record = create_empty_record(st.session_state["media_type"])
        record.media_type = st.session_state["media_type"]
        set_record_title(record, media_path.stem)
        record.media_path = str(media_path)
        message = f"Prepared new metadata for `{media_path.name}`."

    record.media_path = str(media_path)
    record = ensure_default_fields(record)
    push_flash(message, "success")
    load_record_into_session(record, metadata_path)


def save_uploaded_media_file(uploaded_file, media_type: str) -> Path:
    """Persist an uploaded media file to the default upload directory."""
    target_dir = default_upload_directory(media_type)
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = Path(uploaded_file.name).name
    dest_path = target_dir / filename
    dest_path.write_bytes(uploaded_file.getbuffer())
    return dest_path


def handle_media_path_entry(path_str: str, xml_service: XmlService) -> None:
    """Parse user-supplied media path and load metadata."""
    path_str = path_str.strip()
    if not path_str:
        st.warning("Please enter a media file path before loading.")
        return
    path = Path(path_str).expanduser()
    st.session_state[MEDIA_UPLOAD_TOKEN_KEY] = None
    load_media_from_disk(path, xml_service)


def trigger_rerun() -> None:
    """Trigger a Streamlit rerun compatible with current and legacy releases."""
    rerun_fn = getattr(st, "experimental_rerun", None)
    if callable(rerun_fn):
        rerun_fn()
    else:
        st.rerun()


@st.cache_resource
def get_services() -> Tuple[XmlService, SearchService, ExportService]:
    """Instantiate and memoize core services."""
    xml_service = XmlService()
    search_service = SearchService(xml_service=xml_service)
    export_service = ExportService(xml_service=xml_service)
    return xml_service, search_service, export_service


def initialize_session_state(xml_service: XmlService) -> None:
    """Prime Streamlit session state with defaults."""
    if "current_screen" not in st.session_state:
        st.session_state["current_screen"] = "home"
    if "media_type" not in st.session_state:
        st.session_state["media_type"] = MEDIA_TYPES[0]
    st.session_state["current_xml_path"] = None
    if MEDIA_PATH_KEY not in st.session_state:
        st.session_state[MEDIA_PATH_KEY] = ""
    if MEDIA_PATH_INPUT_KEY not in st.session_state:
        st.session_state[MEDIA_PATH_INPUT_KEY] = st.session_state[MEDIA_PATH_KEY]
    if MEDIA_PATH_INPUT_PENDING_KEY not in st.session_state:
        st.session_state[MEDIA_PATH_INPUT_PENDING_KEY] = None
    if MEDIA_UPLOAD_TOKEN_KEY not in st.session_state:
        st.session_state[MEDIA_UPLOAD_TOKEN_KEY] = None
    if FLASH_MESSAGE_KEY not in st.session_state:
        st.session_state[FLASH_MESSAGE_KEY] = None
    if FORM_SEED_TOKEN_KEY not in st.session_state:
        st.session_state[FORM_SEED_TOKEN_KEY] = 0
    if FORM_RENDER_TOKEN_KEY not in st.session_state:
        st.session_state[FORM_RENDER_TOKEN_KEY] = -1
    if "current_record" not in st.session_state:
        record = create_empty_record(st.session_state["media_type"])
        st.session_state["current_record"] = record
        initialize_field_values(record, overwrite=True)
    if "current_xml_path" not in st.session_state:
        st.session_state["current_xml_path"] = None
    if "search_results" not in st.session_state:
        st.session_state["search_results"] = []
    if "filter_count" not in st.session_state:
        st.session_state["filter_count"] = 1
    if "search_folder" not in st.session_state:
        st.session_state["search_folder"] = str(xml_service.repository.base_dir)
    if "export_destination" not in st.session_state:
        st.session_state["export_destination"] = str(Path("exports/metadata_export.xlsx"))


def initialize_field_values(record: MetadataRecord, overwrite: bool = False) -> None:
    """Seed Streamlit keys for section/field pairs."""
    for section in record.sections:
        for field_name, value in section.fields.items():
            key = field_key(section.name, field_name)
            if overwrite or key not in st.session_state:
                st.session_state[key] = value
            if overwrite and is_date_field(field_name):
                date_key = f"{key}__date_picker"
                no_date_key = f"{key}__no_date"
                value_str = (value or "").strip()
                st.session_state[no_date_key] = value_str == ""
                st.session_state.pop(date_key, None)
                parsed = parse_iso_date(value_str)
                if parsed:
                    st.session_state[date_key] = parsed
    if overwrite or TITLE_FIELD_KEY not in st.session_state:
        st.session_state[TITLE_FIELD_KEY] = record.title
    media_path_value = (record.media_path or "").strip()
    if overwrite or MEDIA_PATH_KEY not in st.session_state:
        st.session_state[MEDIA_PATH_KEY] = media_path_value
    if overwrite or MEDIA_PATH_INPUT_KEY not in st.session_state:
        st.session_state[MEDIA_PATH_INPUT_KEY] = media_path_value


def load_record_into_session(record: MetadataRecord, path: Path | None = None) -> None:
    """Persist a record and associated metadata into session state."""
    record = ensure_default_fields(record)
    st.session_state["current_record"] = record
    st.session_state["media_type"] = record.media_type
    st.session_state["current_xml_path"] = str(path) if path else None
    st.session_state["current_screen"] = "form"
    media_path_value = (record.media_path or "").strip()
    st.session_state[MEDIA_PATH_KEY] = media_path_value
    st.session_state[MEDIA_PATH_INPUT_PENDING_KEY] = media_path_value

    st.session_state[FORM_SEED_TOKEN_KEY] += 1

    trigger_rerun()


def build_record_from_session(base_record: MetadataRecord) -> MetadataRecord:
    """Construct a MetadataRecord populated with current session values."""
    sections: List[MetadataSection] = []
    for section in base_record.sections:
        fields = {}
        for field_name in section.fields:
            key = field_key(section.name, field_name)
            fields[field_name] = st.session_state.get(key, "")
        sections.append(
            MetadataSection(
                name=section.name,
                fields=fields,
                color=section.color,
            )
        )

    title_value = st.session_state.get(TITLE_FIELD_KEY, "").strip()
    if not title_value and sections:
        admin_section = next((section for section in sections if section.name == "Administrative"), None)
        if admin_section:
            title_value = admin_section.fields.get("Title", "")

    record = MetadataRecord(
        title=title_value,
        media_type=st.session_state["media_type"],
        sections=sections,
        media_path=st.session_state.get(MEDIA_PATH_INPUT_KEY, st.session_state.get(MEDIA_PATH_KEY, "")).strip(),
    )
    if title_value:
        admin_section = record.get_section("Administrative")
        if admin_section:
            admin_section.set_field("Title", title_value)
    return record


def render_sidebar() -> None:
    """Render the persistent navigation menu."""
    labels = {
        "home": "Home",
        "form": "Metadata Form",
        "search": "Search",
        "export": "Export",
        "exit": "Exit",
    }
    current_screen = st.session_state.get("current_screen", "home")
    current_index = SCREEN_ORDER.index(current_screen)

    with st.sidebar:
        st.title("Navigation")
        selection = st.radio(
            "Go to",
            options=[labels[key] for key in SCREEN_ORDER[:-1]],
            index=current_index if current_screen != "exit" else 0,
        )
        selected_key = next(key for key, label in labels.items() if label == selection)
        if selected_key != current_screen:
            st.session_state["current_screen"] = selected_key
            trigger_rerun()

        if st.button("Exit App"):
            st.session_state["current_screen"] = "exit"
            trigger_rerun()


def render_home_screen() -> None:
    """Display the home screen for choosing a media type."""
    st.title("Select Media Type")
    st.write("Choose the type of media for which you would like to create metadata.")

    columns = st.columns(len(MEDIA_TYPES))
    for idx, media_type in enumerate(MEDIA_TYPES):
        if columns[idx].button(media_type, use_container_width=True):
            st.session_state["current_screen"] = "form"
            load_record_into_session(create_empty_record(media_type))


def render_metadata_form(xml_service: XmlService) -> None:
    """Render the metadata form screen."""
    record = ensure_default_fields(st.session_state["current_record"])
    st.session_state["current_record"] = record
    seed_token = st.session_state.get(FORM_SEED_TOKEN_KEY, 0)
    last_render_seed = st.session_state.get(FORM_RENDER_TOKEN_KEY, -1)
    overwrite = seed_token != last_render_seed
    initialize_field_values(record, overwrite=overwrite)
    st.session_state[FORM_RENDER_TOKEN_KEY] = seed_token

    st.title("Metadata Form")
    st.subheader(f"Media Type: {st.session_state['media_type']}")

    current_path = st.session_state.get("current_xml_path")
    if current_path:
        st.info(f"Editing existing file: `{Path(current_path).name}`")
    else:
        st.info("Creating a new metadata record.")

    pop_flash()

    st.markdown("### Media File")
    pending_media_input = st.session_state.get(MEDIA_PATH_INPUT_PENDING_KEY)
    if pending_media_input is not None:
        st.session_state[MEDIA_PATH_INPUT_KEY] = pending_media_input
        st.session_state[MEDIA_PATH_KEY] = pending_media_input
        st.session_state[MEDIA_PATH_INPUT_PENDING_KEY] = None

    media_cols = st.columns([3, 1])
    with media_cols[0]:
        media_path_input = st.text_input(
            "Media File Path",
            key=MEDIA_PATH_INPUT_KEY,
            placeholder=f"Enter or paste a {st.session_state['media_type'].lower()} file path",
        )
    with media_cols[1]:
        load_clicked = st.button("Load Media", use_container_width=True)
    if load_clicked:
        handle_media_path_entry(media_path_input, xml_service)

    uploaded_file = st.file_uploader(
        f"Upload {st.session_state['media_type']} File",
        type=media_upload_extensions(st.session_state["media_type"]),
        key="media_uploader",
    )
    if uploaded_file is not None:
        upload_token = (uploaded_file.name, uploaded_file.size)
        if st.session_state.get(MEDIA_UPLOAD_TOKEN_KEY) != upload_token:
            dest_path = save_uploaded_media_file(uploaded_file, st.session_state["media_type"])
            st.session_state[MEDIA_UPLOAD_TOKEN_KEY] = upload_token
            load_media_from_disk(dest_path, xml_service)


    st.markdown("### Metadata Fields")
    with st.form("metadata_form"):
        st.text_input("Title", key=TITLE_FIELD_KEY, help="Used as the filename when exporting to XML.")

        for section in record.sections:
            with st.expander(f"{section.name}", expanded=section.name in {"Administrative", "Technical"}):
                for field_name in section.fields:
                    if section.name == "Administrative" and field_name == "Title":
                        continue
                    key = field_key(section.name, field_name)
                    label = f"{field_name}"
                    if is_date_field(field_name):
                        no_date_key = f"{key}__no_date"
                        date_key = f"{key}__date_picker"
                        current_value = st.session_state.get(key, "").strip()
                        if no_date_key not in st.session_state:
                            st.session_state[no_date_key] = current_value == ""
                        no_date = st.checkbox(f"No {label}", key=no_date_key)
                        if no_date:
                            st.session_state[key] = ""
                            st.session_state.pop(date_key, None)
                            st.caption("No date stored for this field.")
                        else:
                            default_date = parse_iso_date(current_value) or datetime.date.today()
                            if date_key not in st.session_state:
                                st.session_state[date_key] = default_date
                            selected_date = st.date_input(label, key=date_key)
                            if isinstance(selected_date, datetime.date):
                                st.session_state[key] = selected_date.isoformat()
                    elif field_name in LONG_TEXT_FIELDS:
                        st.text_area(label, key=key, height=120)
                    else:
                        st.text_input(label, key=key)

        form_save_col, form_clear_col = st.columns(2)
        save_clicked = form_save_col.form_submit_button("Save Metadata", type="primary")
        clear_clicked = form_clear_col.form_submit_button("Reset Form")

    if save_clicked:
        handle_create_xml(xml_service)
    if clear_clicked:
        handle_clear_form()

    action_cols = st.columns(3)
    if action_cols[0].button("Back to Home", use_container_width=True):
        st.session_state["current_screen"] = "home"
        trigger_rerun()

    current_xml_path = st.session_state.get("current_xml_path")
    if current_xml_path:
        xml_path = Path(current_xml_path)
        if xml_path.exists():
            with open(xml_path, "rb") as xml_handle:
                action_cols[1].download_button(
                    "Download Metadata XML",
                    data=xml_handle.read(),
                    file_name=xml_path.name,
                    mime="application/xml",
                    use_container_width=True,
                )
    media_path_value = st.session_state.get(MEDIA_PATH_KEY, "")
    if media_path_value:
        media_path = Path(media_path_value)
        if media_path.exists():
            with open(media_path, "rb") as media_handle:
                action_cols[2].download_button(
                    "Download Media",
                    data=media_handle.read(),
                    file_name=media_path.name,
                    use_container_width=True,
                )

    with st.expander("Load Existing XML"):
        xml_files = sorted(xml_service.repository.base_dir.glob("*.xml"))
        options = ["-- Select --"] + [path.name for path in xml_files]
        selected_name = st.selectbox(
            "Available XML files",
            options,
            index=0,
            key="metadata_load_select",
        )
        load_cols = st.columns([1, 1])
        if load_cols[0].button("Load Selected", use_container_width=True):
            if selected_name != "-- Select --":
                selected_path = xml_service.repository.base_dir / selected_name
                try:
                    record = xml_service.load_record(selected_path)
                except Exception as exc:
                    st.error(f"Failed to load XML: {exc}")
                else:
                    push_flash(f"Loaded `{selected_name}`.", "success")
                    load_record_into_session(record, selected_path)
            else:
                st.warning("Please select a file to load.")

        uploaded_file = st.file_uploader("Upload XML", type="xml")
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                temp_path = Path(tmp_file.name)
            try:
                record = xml_service.load_record(temp_path)
            except Exception as exc:
                st.error(f"Unable to parse uploaded XML: {exc}")
            else:
                push_flash("XML loaded from upload. Save to store it locally.", "success")
                load_record_into_session(record)
            finally:
                temp_path.unlink(missing_ok=True)


def handle_create_xml(xml_service: XmlService) -> None:
    """Persist the current form to XML."""
    base_record = st.session_state["current_record"]
    record = build_record_from_session(base_record)

    media_path = st.session_state.get(MEDIA_PATH_INPUT_KEY, st.session_state.get(MEDIA_PATH_KEY, "")).strip()
    if not media_path:
        st.error("Please select or upload a media file before saving metadata.")
        return

    if not record.title:
        st.error("Please provide a Title before creating XML.")
        return

    record.media_path = media_path

    path_hint = st.session_state.get("current_xml_path")
    try:
        output_path = xml_service.save_record(record, path_hint=path_hint)
    except Exception as exc:
        st.error(f"Failed to save XML: {exc}")
        return

    push_flash(f"Metadata saved to `{Path(output_path).name}`.", "success")
    load_record_into_session(record, Path(output_path))
def handle_clear_form() -> None:
    """Reset the metadata form to blank values."""
    media_type = st.session_state["media_type"]
    push_flash("Form cleared. Start fresh!", "info")
    st.session_state[MEDIA_UPLOAD_TOKEN_KEY] = None
    load_record_into_session(create_empty_record(media_type))


def render_search_screen(search_service: SearchService, xml_service: XmlService) -> None:
    """Render the search screen."""
    st.title("Search Metadata")

    folder = st.text_input("Choose Folder", value=st.session_state["search_folder"])
    st.session_state["search_folder"] = folder

    text_query = st.text_input(
        "Keyword (matches any field)",
        value=st.session_state.get("search_text_query", ""),
        key="search_text_query",
    )

    filter_count = st.number_input(
        "Number of filters",
        min_value=1,
        max_value=5,
        value=st.session_state["filter_count"],
        step=1,
    )
    st.session_state["filter_count"] = filter_count

    field_options = [(section.name, field) for section in DEFAULT_SECTIONS for field in section.fields]

    filters: List[FilterCriteria] = []
    for idx in range(int(filter_count)):
        with st.container():
            field_selection = st.selectbox(
                f"Filter {idx + 1} Field",
                options=field_options,
                format_func=lambda option: f"{option[0]} • {option[1]}",
                key=f"search_field_{idx}",
            )
            keyword = st.text_input(f"Filter {idx + 1} Keyword", key=f"search_keyword_{idx}")
            if keyword.strip():
                filters.append(
                    FilterCriteria(
                        section=field_selection[0],
                        field=field_selection[1],
                        keyword=keyword,
                    )
                )

    match_choice = st.radio(
        "Condition",
        options=["Match Any", "Match All"],
        index=0,
        horizontal=True,
        key="search_match_choice",
    )
    match_all = match_choice == "Match All"

    col1, col2, col3 = st.columns(3)
    if col1.button("Search", type="primary", use_container_width=True):
        execute_search(search_service, folder, filters, match_all, text_query)
    if col2.button("Clear Search", use_container_width=True):
        st.session_state["search_results"] = []
        st.success("Search cleared.")
    if col3.button("Back to Home", use_container_width=True):
        st.session_state["current_screen"] = "home"
        trigger_rerun()

    results = st.session_state.get("search_results", [])
    if results:
        render_search_results(results, xml_service)
    else:
        st.info("No results to display yet. Run a search to see matches.")


def execute_search(
    search_service: SearchService,
    folder: str,
    filters: Iterable[FilterCriteria],
    match_all: bool,
    text_query: str,
) -> None:
    """Execute a search and cache the results."""
    path = Path(folder).expanduser()
    try:
        results = search_service.search(path, list(filters), match_all, text_query)
    except Exception as exc:
        st.error(f"Search failed: {exc}")
        return
    st.session_state["search_results"] = results
    if results:
        st.success(f"Found {len(results)} matching record(s).")
    else:
        st.warning("No matches found.")


def render_search_results(results: List[Tuple[Path, MetadataRecord]], xml_service: XmlService) -> None:
    """Display search results with an option to open a record."""
    table_rows = [
        {
            "Title": record.title or path.stem,
            "Media Type": record.media_type,
            "File": str(path),
        }
        for path, record in results
    ]
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

    for idx, (path, record) in enumerate(results):
        if st.button(f"Open {record.title or path.stem}", key=f"open_result_{idx}"):
            st.session_state["current_screen"] = "form"
            push_flash(f"Loaded metadata from `{path.name}`.", "success")
            load_record_into_session(record, path)


def render_export_screen(export_service: ExportService, xml_service: XmlService) -> None:
    """Render the Excel export screen."""
    st.title("Export to Excel")

    folder = st.text_input(
        "Source Folder",
        value=st.session_state["search_folder"],
        help="Select the folder containing XML files.",
    )
    destination = st.text_input(
        "Destination File",
        value=st.session_state["export_destination"],
        help="Provide the Excel file path to generate.",
    )

    st.session_state["search_folder"] = folder
    st.session_state["export_destination"] = destination

    col1, col2 = st.columns(2)
    if col1.button("Export to Excel", type="primary", use_container_width=True):
        try:
            output_path = export_service.export_folder(Path(folder), Path(destination))
        except Exception as exc:
            st.error(f"Export failed: {exc}")
        else:
            st.success(f"Exported metadata to `{output_path}`.")
    if col2.button("Back to Home", use_container_width=True):
        st.session_state["current_screen"] = "home"
        trigger_rerun()


def render_exit_screen() -> None:
    """Render a polite exit message."""
    st.title("Metadata Management App")
    st.success("You can close this browser tab to exit the application.")
    st.stop()


def main() -> None:
    """Entry point for Streamlit."""
    st.set_page_config(page_title="Metadata Management App", layout="wide")
    xml_service, search_service, export_service = get_services()
    initialize_session_state(xml_service)
    render_sidebar()

    screen = st.session_state.get("current_screen", "home")
    if screen == "home":
        render_home_screen()
    elif screen == "form":
        render_metadata_form(xml_service)
    elif screen == "search":
        render_search_screen(search_service, xml_service)
    elif screen == "export":
        render_export_screen(export_service, xml_service)
    elif screen == "exit":
        render_exit_screen()
    else:
        st.warning("Unknown screen. Returning home.")
        st.session_state["current_screen"] = "home"
        trigger_rerun()


if __name__ == "__main__":
    main()
