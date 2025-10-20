from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import hashlib
import re
import sys
import os

APP_TITLE = "AV Metadata Sidecar Builder"
XML_ROOT = "Asset"
VERSION = "1.0"

XML_NAME_RE = re.compile(r"[^A-Za-z0-9_.:-]")


def sanitize_tag(name: str) -> str:
    tag = XML_NAME_RE.sub("_", name.strip())
    if not tag:
        tag = "X"
    if tag[0].isdigit():
        tag = "X_" + tag
    return tag


def _indent(elem, level=0):
    i = "
" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            _indent(e, level + 1)
            if not e.tail or not e.tail.strip():
                e.tail = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def save_xml(root: ET.Element, xml_path: Path):
    _indent(root)
    ET.ElementTree(root).write(xml_path, encoding="utf-8", xml_declaration=True)


def _local_name(tag: str) -> str:
    return tag.rsplit('}', 1)[-1] if '}' in tag else tag


# --------------------- Scrolling helper ---------------------
def bind_mousewheel(widget, target=None, *, horizontal_with_shift=True, v_units=1, h_units=1, page_on_ctrl=False):
    """Enable mouse-wheel scrolling over `widget` to scroll `target`."""
    if target is None:
        target = widget

    def _scroll_y(delta):
        if page_on_ctrl and getattr(_scroll_y, "_ctrl", False):
            target.yview_scroll(-1 if delta < 0 else 1, "page")
        else:
            target.yview_scroll(delta * v_units, "units")

    def _scroll_x(delta):
        try:
            target.xview_scroll(delta * h_units, "units")
        except Exception:
            pass

    def _on_wheel_win_mac(event):
        step = 0
        if sys.platform.startswith("darwin"):
            step = -1 if event.delta > 0 else 1
        else:
            step = -int(event.delta / 120) if event.delta else 0
        _scroll_y._ctrl = bool(event.state & 0x0004)
        if horizontal_with_shift and (event.state & 0x0001):
            if step:
                _scroll_x(step)
        else:
            if step:
                _scroll_y(step)
        return "break"

    def _on_wheel_linux_up(event):
        _scroll_y._ctrl = bool(event.state & 0x0004)
        if horizontal_with_shift and (event.state & 0x0001):
            _scroll_x(-1)
        else:
            _scroll_y(-1)
        return "break"

    def _on_wheel_linux_down(event):
        _scroll_y._ctrl = bool(event.state & 0x0004)
        if horizontal_with_shift and (event.state & 0x0001):
            _scroll_x(1)
        else:
            _scroll_y(1)
        return "break"

    def _bind_all(_):
        widget.bind_all("<MouseWheel>", _on_wheel_win_mac, add="+")
        widget.bind_all("<Button-4>", _on_wheel_linux_up, add="+")
        widget.bind_all("<Button-5>", _on_wheel_linux_down, add="+")

    def _unbind_all(_):
        widget.unbind_all("<MouseWheel>")
        widget.unbind_all("<Button-4>")
        widget.unbind_all("<Button-5>")

    widget.bind("<Enter>", _bind_all, add="+")
    widget.bind("<Leave>", _unbind_all, add="+")


# --------------------- Field definitions ---------------------
VIDEO_SECTIONS = {
    "Administrative": [
        "Title",
        "Identifier",
        "CollectionName",
        "AcquisitionMethod",
        "Donor/Source Contact",
        "Contributors",
        "DateOfCreation",
        "RightsHolder",
        "AccessConditions",
        "HoldingInstitution",
        "CopyRightStatus",
        "UserRestrictions",
        "QCStatus",
        "QCOperator",
    ],
    "Descriptive": [
        "Identifier",
        "Title",
        "Subject",
        "Summary",
        "KeyWords",
        "Genre",
        "Creator",
        "Languages",
        "GeographicLocation",
        "EventDate",
        "PeopleInVideo",
    ],
    "TechnicalOriginal": [
        "Format",
        "SignalStandard",
        "RecordingMode",
        "TapeLengthMinutes",
        "AudioChannels",
        "ConditionNotes",
        "OriginalLabel",
    ],
    "TechnicalMaster": [
        "Codec",
        "Container_wrapper",
        "BitDepth",
        "Resolution",
        "FrameRate",
        "ScanType",
        "AspectRatio",
        "DataRate_BitRate",
        "ColorSubSampling",
        "ColorSpace",
        "AudioFormat",
        "AudioSampleRateKHz",
        "AudioBitDepth",
        "AudioChannelsCount",
        "Duration",
        "FileSizeGB",
        "Checksums",
        "EmbeddedMetadataSchema",
    ],
    "CaptureChain": [
        "DigitizationDate",
        "OperatorName",
        "PlaybackDevice",
        "TBCModel",
        "FrameSynchronizer",
        "CaptureHardware",
        "CaptureSoftware",
        "SignalPathNotes",
        "AudioDelayApplied",
        "IssuesDuringCapture",
    ],
    "Preservation": [
        "SourceProvenance",
        "PreservationActions",
        "MigrationHistory",
        "ErrorReports",
        "StorageLocation",
        "BackupDetails",
    ],
}

AUDIO_SECTIONS = {
    "Administrative": VIDEO_SECTIONS["Administrative"],
    "Descriptive": [
        "Identifier",
        "Title",
        "Subject",
        "Summary",
        "KeyWords",
        "Genre",
        "Creator",
        "Languages",
        "GeographicLocation",
        "EventDate",
        "PeopleInVideo",
    ],
    "TechnicalOriginal": [
        "Format",
        "SignalStandard",
        "RecordingMode",
        "TapeLengthMinutes",
        "AudioChannels",
        "ConditionNotes",
        "OriginalLabel",
        "SpeedTrack",
        "TrackCount",
        "SideCount",
        "ChannelCount",
        "DurationSideA",
        "DurationSideB",
    ],
    "TechnicalMaster": [
        "Codec",
        "Container_wrapper",
        "BitDepth",
        "DataRate_BitRate",
        "AudioFormat",
        "AudioSampleRateKHz",
        "AudioBitDepth",
        "AudioChannelsCount",
        "Duration",
        "FileSizeGB",
        "Checksums",
        "EmbeddedMetadataSchema",
    ],
    "CaptureChain": VIDEO_SECTIONS["CaptureChain"],
    "Preservation": VIDEO_SECTIONS["Preservation"],
}

LIST_FIELDS = {"KeyWords", "Languages", "PeopleInVideo"}
DEFAULTS = {"EmbeddedMetadataSchema": "PBCoreXML"}

PH = {
    ("Administrative", "CollectionName"): "Collection/Series (e.g., 'National Archive – Aviation')",
    ("Administrative", "AcquisitionMethod"): "Donation / Purchase / Transfer / In-house",
    ("Administrative", "Donor/Source Contact"): "Name, email/phone",
    ("Administrative", "Contributors"): "Names, roles (comma-separated)",
    ("Administrative", "DateOfCreation"): "YYYY or YYYY-MM-DD (content creation)",
    ("Administrative", "RightsHolder"): "Person/org owning copyright",
    ("Administrative", "AccessConditions"): "e.g., 'Reading-room only' or 'Public web'",
    ("Administrative", "HoldingInstitution"): "Institution/department",
    ("Administrative", "CopyRightStatus"): "In copyright / Public domain / Unknown",
    ("Administrative", "UserRestrictions"): "Usage restrictions, if any",
    ("Administrative", "QCStatus"): "Pass / Fail / Needs review",
    ("Administrative", "QCOperator"): "QC reviewer name/ID",
    ("Descriptive", "Identifier"): "Auto from filename; can override",
    ("Descriptive", "Title"): "e.g., 'Saudi Airlines Training Film, 1988'",
    ("Descriptive", "Subject"): "Primary topic(s); comma-separated",
    ("Descriptive", "Summary"): "1–3 sentence abstract",
    ("Descriptive", "KeyWords"): "Comma-separated keywords",
    ("Descriptive", "Genre"): "e.g., Training, News, Documentary",
    ("Descriptive", "Creator"): "Producer/Organization",
    ("Descriptive", "Languages"): "Language codes (ar, en, tr), comma-separated",
    ("Descriptive", "GeographicLocation"): "City, Country (or GPS)",
    ("Descriptive", "EventDate"): "YYYY or YYYY-MM-DD (event date)",
    ("Descriptive", "PeopleInVideo"): "Names (comma-separated)",
    ("TechnicalOriginal", "Format"): "Physical: VHS / U-matic / Betacam SP",
    ("TechnicalOriginal", "SignalStandard"): "PAL / NTSC / SECAM",
    ("TechnicalOriginal", "RecordingMode"): "SP / LP / EP (or format-specific)",
    ("TechnicalOriginal", "TapeLengthMinutes"): "e.g., 60",
    ("TechnicalOriginal", "AudioChannels"): "e.g., 2 (Ch1 Arabic, Ch2 M&E)",
    ("TechnicalOriginal", "ConditionNotes"): "Dropouts, mold, creasing",
    ("TechnicalOriginal", "OriginalLabel"): "Text on shell/box",
    ("TechnicalOriginal", "SpeedTrack"): "e.g., 7½ ips",
    ("TechnicalOriginal", "TrackCount"): "e.g., 2",
    ("TechnicalOriginal", "SideCount"): "e.g., 2 (A/B)",
    ("TechnicalOriginal", "ChannelCount"): "e.g., 2 mono",
    ("TechnicalOriginal", "DurationSideA"): "HH:MM:SS",
    ("TechnicalOriginal", "DurationSideB"): "HH:MM:SS",
    ("TechnicalMaster", "Codec"): "e.g., FFV1 / ProRes 422HQ",
    ("TechnicalMaster", "Container_wrapper"): "e.g., MKV / MOV",
    ("TechnicalMaster", "BitDepth"): "10-bit (video) / 24-bit (audio)",
    ("TechnicalMaster", "Resolution"): "e.g., 720x576 / 1920x1080",
    ("TechnicalMaster", "FrameRate"): "e.g., 25i / 29.97i / 23.976p",
    ("TechnicalMaster", "ScanType"): "Interlaced / Progressive",
    ("TechnicalMaster", "AspectRatio"): "4:3 / 16:9",
    ("TechnicalMaster", "DataRate_BitRate"): "e.g., 120 Mbps",
    ("TechnicalMaster", "ColorSubSampling"): "4:2:2",
    ("TechnicalMaster", "ColorSpace"): "Rec.601 / Rec.709",
    ("TechnicalMaster", "AudioFormat"): "WAV / PCM",
    ("TechnicalMaster", "AudioSampleRateKHz"): "48 / 96",
    ("TechnicalMaster", "AudioBitDepth"): "24",
    ("TechnicalMaster", "AudioChannelsCount"): "e.g., 2",
    ("TechnicalMaster", "Duration"): "HH:MM:SS.mmm",
    ("TechnicalMaster", "FileSizeGB"): "e.g., 45.2",
    ("TechnicalMaster", "Checksums"): "Click 'Generate MD5'",
    ("TechnicalMaster", "EmbeddedMetadataSchema"): "e.g., PBCoreXML",
    ("CaptureChain", "DigitizationDate"): "YYYY-MM-DD",
    ("CaptureChain", "OperatorName"): "Your name/ID",
    ("CaptureChain", "PlaybackDevice"): "e.g., Sony BVU-950",
    ("CaptureChain", "TBCModel"): "e.g., DPS-295 / BE75",
    ("CaptureChain", "FrameSynchronizer"): "Model or N/A",
    ("CaptureChain", "CaptureHardware"): "e.g., AJA Kona LHi",
    ("CaptureChain", "CaptureSoftware"): "e.g., vrecord 2024.x",
    ("CaptureChain", "SignalPathNotes"): "BVU-950 → BE75 → Kona LHi → vrecord",
    ("CaptureChain", "AudioDelayApplied"): "ms (+/-)",
    ("CaptureChain", "IssuesDuringCapture"): "Head clogging, tracking",
    ("Preservation", "SourceProvenance"): "Custody history",
    ("Preservation", "PreservationActions"): "Cleaning, baking, repair",
    ("Preservation", "MigrationHistory"): "Any previous conversions",
    ("Preservation", "ErrorReports"): "QC notes / logs",
    ("Preservation", "StorageLocation"): "NAS path / LTO barcode",
    ("Preservation", "BackupDetails"): "3-2-1 backups",
}

OPTIONS = {
    ("Administrative", "AcquisitionMethod"): ["Donation", "Purchase", "Transfer", "In-house"],
    ("Administrative", "CopyRightStatus"): ["In copyright", "Public domain", "Unknown"],
    ("Administrative", "QCStatus"): ["Pass", "Fail", "Needs review"],
    ("Administrative", "AccessConditions"): ["Public web", "Reading-room only", "Restricted"],
    ("Descriptive", "Genre"): [
        "Documentary", "News report", "Interview", "Oral history", "Lecture",
        "Advertisement / Commercial", "Feature film", "Educational program", "Home video",
        "Music", "Sports broadcast", "Public service announcement",
    ],
    ("Descriptive", "Languages"): ["ar", "en", "fr", "es", "de"],
    ("TechnicalOriginal", "Format"): [
        "VHS", "VHS-C", "Betacam SP", "U-matic Low", "U-matic Hi", "MiniDV",
        "MicroMV", "Betamax", "8mm", "Hi8", "DVCAM", "Digital Betacam",
    ],
    ("TechnicalOriginal", "SignalStandard"): ["PAL", "NTSC", "SECAM"],
    ("TechnicalOriginal", "RecordingMode"): ["SP", "LP", "EP"],
    ("TechnicalOriginal", "AudioChannels"): ["1", "2", "4"],
    ("TechnicalOriginal", "SpeedTrack"): ["1⅞ ips", "3¾ ips", "7½ ips", "15 ips"],
    ("TechnicalOriginal", "TrackCount"): ["1", "2", "4"],
    ("TechnicalOriginal", "SideCount"): ["1", "2"],
    ("TechnicalOriginal", "ChannelCount"): ["1", "2", "4"],
    ("TechnicalMaster", "Codec"): ["FFV1", "ProRes 422HQ", "DV25", "PCM"],
    ("TechnicalMaster", "Container_wrapper"): ["MKV", "MOV", "MXF"],
    ("TechnicalMaster", "BitDepth"): ["8-bit", "10-bit", "12-bit", "24-bit"],
    ("TechnicalMaster", "Resolution"): ["720x576", "720x480", "1280x720", "1920x1080"],
    ("TechnicalMaster", "FrameRate"): ["23.976", "24", "25", "29.97"],
    ("TechnicalMaster", "ScanType"): ["Interlaced", "Progressive"],
    ("TechnicalMaster", "AspectRatio"): ["4:3", "16:9"],
    ("TechnicalMaster", "ColorSubSampling"): ["4:2:0", "4:2:2", "4:4:4"],
    ("TechnicalMaster", "ColorSpace"): ["Rec.601", "Rec.709", "Rec.2020"],
    ("TechnicalMaster", "AudioFormat"): ["WAV", "PCM", "AAC"],
    ("TechnicalMaster", "AudioSampleRateKHz"): ["44.1", "48", "96"],
    ("TechnicalMaster", "AudioBitDepth"): ["16", "24", "32"],
    ("TechnicalMaster", "AudioChannelsCount"): ["1", "2", "6"],
}


class MediaTab(ttk.Frame):
    def __init__(self, parent, media_type: str):
        super().__init__(parent)
        self.media_type = media_type
        self.sections = VIDEO_SECTIONS if media_type == "Video" else AUDIO_SECTIONS
        self.related_node = "RelatedVideo" if media_type == "Video" else "RelatedAudio"
        self.path_key = "VideoPath" if media_type == "Video" else "AudioPath"
        self.base_key = "VideoBasename" if media_type == "Video" else "AudioBasename"

        self.entries: dict[tuple[str, str], tk.StringVar] = {}
        self.entry_widgets: dict[tuple[str, str], ttk.Entry] = {}

        self._build_ui()

    def _apply_placeholder(self, widget: ttk.Entry, text: str):
        widget.delete(0, "end")
        widget.insert(0, text)
        try:
            widget.configure(foreground="gray50")
        except tk.TclError:
            pass
        widget._placeholder = text  # type: ignore[attr-defined]

        def on_focus_in(_):
            if getattr(widget, "_placeholder", None) == text and widget.get() == text:
                widget.delete(0, "end")
                try:
                    widget.configure(foreground="black")
                except tk.TclError:
                    pass

        def on_focus_out(_):
            if not widget.get().strip():
                widget.delete(0, "end")
                widget.insert(0, text)
                try:
                    widget.configure(foreground="gray50")
                except tk.TclError:
                    pass
                widget._placeholder = text  # type: ignore[attr-defined]

        widget.bind("<FocusIn>", on_focus_in, add="+")
        widget.bind("<FocusOut>", on_focus_out, add="+")

    def _is_placeholder(self, widget: ttk.Entry, value: str) -> bool:
        return getattr(widget, "_placeholder", None) == value and widget.get() == value

    def _strip_placeholder(self, widget: ttk.Entry) -> str:
        value = widget.get()
        if self._is_placeholder(widget, value):
            return ""
        return value

    def _build_ui(self):
        outer = ttk.Frame(self, padding=10)
        outer.pack(fill=tk.BOTH, expand=True)

        pick = ttk.LabelFrame(outer, text=f"Select {self.media_type} File (XML will use the SAME name)")
        pick.pack(fill=tk.X, pady=6)
        self.media_var = tk.StringVar()
        media_entry = ttk.Entry(pick, textvariable=self.media_var)
        media_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, pady=6)
        ttk.Button(pick, text="Browse…", command=self._pick_file).pack(side=tk.LEFT, padx=6, pady=6)

        out = ttk.LabelFrame(outer, text="XML Output Folder (default: same folder as media)")
        out.pack(fill=tk.X, pady=6)
        self.outdir_var = tk.StringVar()
        out_entry = ttk.Entry(out, textvariable=self.outdir_var)
        out_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, pady=6)
        ttk.Button(out, text="Choose…", command=self._pick_outdir).pack(side=tk.LEFT, padx=6, pady=6)

        id_row = ttk.Frame(outer)
        id_row.pack(fill=tk.X, pady=4)
        ttk.Label(id_row, text="Identifier:").pack(side=tk.LEFT, padx=6)
        self.identifier_var = tk.StringVar()
        id_entry = ttk.Entry(id_row, textvariable=self.identifier_var, width=40)
        id_entry.pack(side=tk.LEFT, padx=6)
        self._apply_placeholder(id_entry, PH[("Descriptive", "Identifier")])

        fields_frame = ttk.LabelFrame(outer, text="Metadata Fields (read hints first; replace grayed text)")
        fields_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        canvas = tk.Canvas(fields_frame, borderwidth=0, height=380)
        yscroll = ttk.Scrollbar(fields_frame, orient="vertical", command=canvas.yview)
        container = ttk.Frame(canvas)
        container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=container, anchor="nw")
        canvas.configure(yscrollcommand=yscroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        bind_mousewheel(canvas, canvas, v_units=2)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        row = col = 0
        for sec_name, fields in self.sections.items():
            frame = ttk.LabelFrame(container, text=sec_name, padding=8)
            frame.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)

            for label in fields:
                row_frame = ttk.Frame(frame)
                row_frame.pack(fill=tk.X, pady=2)
                ttk.Label(row_frame, text=label, width=28).pack(side=tk.LEFT)

                var = tk.StringVar()
                options = OPTIONS.get((sec_name, label))
                if options:
                    widget = ttk.Combobox(row_frame, textvariable=var, values=options, state="normal")
                    widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
                else:
                    widget = ttk.Entry(row_frame, textvariable=var)
                    widget.pack(side=tk.LEFT, fill=tk.X, expand=True)

                self.entries[(sec_name, label)] = var
                self.entry_widgets[(sec_name, label)] = widget

                placeholder = PH.get((sec_name, label), "")
                if placeholder:
                    self._apply_placeholder(widget, placeholder)
                elif (sec_name, label) in DEFAULTS:
                    var.set(DEFAULTS[(sec_name, label)])

                if sec_name == "TechnicalMaster" and label == "Checksums":
                    ttk.Button(row_frame, text="Generate MD5", command=self._generate_md5).pack(side=tk.LEFT, padx=6)

            col = 1 - col
            if col == 0:
                row += 1

        btns = ttk.Frame(outer)
        btns.pack(fill=tk.X, pady=8)
        ttk.Button(btns, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Load XML…", command=self._load_xml).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Create XML (Same Name)", command=self._create_xml).pack(side=tk.RIGHT, padx=4)

    def _pick_file(self):
        if self.media_type == "Video":
            ftypes = [
                ("Video files", "*.mkv *.mov *.avi *.mp4 *.mxf *.m2t *.dv *.mpg *.mpeg *.vob *.wmv *.ts"),
                ("All files", "*.*"),
            ]
        else:
            ftypes = [
                ("Audio files", "*.wav *.aiff *.aif *.flac *.mp3 *.m4a *.aac *.wma *.ogg"),
                ("All files", "*.*"),
            ]
        path = filedialog.askopenfilename(title=f"Choose {self.media_type} file", filetypes=ftypes)
        if not path:
            return
        p = Path(path)
        self.media_var.set(str(p))
        if not self.outdir_var.get().strip():
            self.outdir_var.set(str(p.parent))
        if not self.identifier_var.get().strip() or self._is_placeholder(self.entry_widgets[("Descriptive", "Identifier")], self.identifier_var.get()):
            self.identifier_var.set(p.stem)

    def _pick_outdir(self):
        directory = filedialog.askdirectory(title="Choose output folder for XML")
        if directory:
            self.outdir_var.set(directory)

    def _clear(self):
        self.media_var.set("")
        self.outdir_var.set("")
        self.identifier_var.set("")
        for (section, label), widget in self.entry_widgets.items():
            widget.config(state="normal")
            widget.delete(0, "end")
            placeholder = PH.get((section, label), "")
            if placeholder:
                self._apply_placeholder(widget, placeholder)
            elif (section, label) in DEFAULTS:
                self.entries[(section, label)].set(DEFAULTS[(section, label)])

    def _generate_md5(self):
        media_path = self.media_var.get().strip()
        if not media_path:
            messagebox.showerror("Missing file", "Select a media file first.")
            return
        path = Path(media_path)
        if not path.exists():
            messagebox.showerror("Not found", f"File not found:
{path}")
            return
        h = hashlib.md5()
        try:
            with open(path, "rb") as handle:
                while True:
                    chunk = handle.read(8 * 1024 * 1024)
                    if not chunk:
                        break
                    h.update(chunk)
        except Exception as exc:
            messagebox.showerror("MD5 error", f"Failed to read file:
{exc}")
            return
        checksum = h.hexdigest()
        var = self.entries[("TechnicalMaster", "Checksums")]
        widget = self.entry_widgets[("TechnicalMaster", "Checksums")]
        widget.config(foreground="black")
        var.set(f"MD5:{checksum}")
        widget._placeholder = None  # type: ignore[attr-defined]
        widget.config(state="readonly")
        messagebox.showinfo("MD5 generated", f"MD5:
{checksum}")

    def _load_xml(self):
        path = filedialog.askopenfilename(title="Choose XML", filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
        if not path:
            return
        try:
            tree = ET.parse(path)
        except Exception as exc:
            messagebox.showerror("Parse error", f"Could not parse XML:
{exc}")
            return
        root = tree.getroot()
        related = root.find(self.related_node)
        if related is not None:
            media_el = related.find(self.path_key)
            ident_el = related.find("Identifier")
            if media_el is not None and media_el.text:
                self.media_var.set(media_el.text)
            if ident_el is not None and ident_el.text:
                self.identifier_var.set(ident_el.text)
        for (section, label), var in self.entries.items():
            widget = self.entry_widgets[(section, label)]
            node = root.find(sanitize_tag(section))
            value = ""
            if node is not None:
                tag = sanitize_tag(label)
                if label in LIST_FIELDS:
                    parent = node.find(tag)
                    if parent is not None:
                        items = [child.text.strip() for child in parent if child.text and _local_name(child.tag) == "Item"]
                        value = ", ".join(items)
                else:
                    child = node.find(tag)
                    if child is not None and child.text:
                        value = child.text.strip()
            if not value and (section, label) in DEFAULTS:
                value = DEFAULTS[(section, label)]
            widget.config(foreground="black")
            var.set(value)
            widget._placeholder = None  # type: ignore[attr-defined]
            if (section, label) == ("TechnicalMaster", "Checksums"):
                widget.config(state="readonly" if value.startswith("MD5:") and value else "normal")
        messagebox.showinfo("Loaded", f"Fields populated from:
{path}")

    def _create_xml(self):
        media_path = self.media_var.get().strip()
        if not media_path:
            messagebox.showerror("Missing file", f"Choose a {self.media_type} file first.")
            return
        media = Path(media_path)
        if not media.exists():
            messagebox.showerror("Not found", f"File does not exist:
{media}")
            return

        outdir = Path(self.outdir_var.get().strip()) if self.outdir_var.get().strip() else media.parent
        outdir.mkdir(parents=True, exist_ok=True)
        xml_path = outdir / f"{media.stem}.xml"

        root = ET.Element(XML_ROOT, attrib={"version": VERSION})
        related = ET.SubElement(root, self.related_node)
        ET.SubElement(related, self.path_key).text = str(media.resolve())
        ET.SubElement(related, self.base_key).text = media.name
        identifier = self.identifier_var.get().strip() or media.stem
        ET.SubElement(related, "Identifier").text = identifier

        for section, fields in self.sections.items():
            sec_el = ET.SubElement(root, sanitize_tag(section))
            for label in fields:
                widget = self.entry_widgets[(section, label)]
                value = self._strip_placeholder(widget)
                if label in LIST_FIELDS:
                    parent = ET.SubElement(sec_el, sanitize_tag(label))
                    if value:
                        for item in [x.strip() for x in value.split(",") if x.strip()]:
                            ET.SubElement(parent, "Item").text = item
                else:
                    if not value and (section, label) in DEFAULTS:
                        value = DEFAULTS[(section, label)]
                    ET.SubElement(sec_el, sanitize_tag(label)).text = value

        try:
            save_xml(root, xml_path)
        except Exception as exc:
            messagebox.showerror("Write error", f"Failed to write XML:
{exc}")
            return

        if messagebox.askyesno("Success", f"XML saved:
{xml_path}

Open folder?"):
            try:
                if sys.platform.startswith("darwin"):
                    os.system(f'open "{xml_path.parent}"')
                elif os.name == "nt":
                    os.startfile(str(xml_path.parent))
                else:
                    os.system(f'xdg-open "{xml_path.parent}"')
            except Exception:
                pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1200x820")

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)
        notebook.add(MediaTab(notebook, "Video"), text="Video Tape")
        notebook.add(MediaTab(notebook, "Audio"), text="Audio Tape")


if __name__ == "__main__":
    app = App()
    app.mainloop()
