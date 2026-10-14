# ============================================================
# Video & Audio Transcriber
# ============================================================
#
# Dieses Programm kann:
# - lokale Video-Dateien transkribieren
# - lokale Audio-Dateien transkribieren
# - YouTube-Videos transkribieren
# - Deutsch, Englisch und Persisch verarbeiten
# - Sprache automatisch erkennen
# - TXT-Dateien erstellen
# - Word-Dateien erstellen
# - SRT-Untertitel erstellen
# - VTT-Untertitel erstellen
#
# Installation:
#
# py -m pip install -U openai-whisper yt-dlp python-docx
#
# Zusätzlich benötigt:
# FFmpeg
#
# ============================================================

import os
import re
import shutil
import tempfile
import threading
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


# ------------------------------------------------------------
# Unterstützte lokale Datei-Endungen
# ------------------------------------------------------------

SUPPORTED_LOCAL_EXTENSIONS = {
    # Audio
    ".mp3",
    ".wav",
    ".m4a",
    ".flac",
    ".aac",
    ".ogg",
    ".opus",
    ".wma",

    # Video
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".webm",
    ".wmv",
    ".mpeg",
    ".mpg",
    ".m4v",
    ".ts",
}


# ------------------------------------------------------------
# Sprachen
# ------------------------------------------------------------

LANGUAGES = {
    "Automatisch erkennen": None,
    "Deutsch": "de",
    "English": "en",
    "Persisch / Farsi": "fa",
}


# ------------------------------------------------------------
# Whisper Modelle
# ------------------------------------------------------------

MODELS = (
    "tiny",
    "base",
    "small",
    "medium",
    "turbo",
)


# ------------------------------------------------------------
# Dateinamen sicher machen
# ------------------------------------------------------------

def safe_filename(name):
    """
    Entfernt Zeichen, die unter Windows
    nicht in Dateinamen erlaubt sind.
    """

    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = re.sub(r"\s+", " ", name).strip()

    if not name:
        name = "transcript"

    return name[:150]


# ------------------------------------------------------------
# SRT Zeitformat
# ------------------------------------------------------------

def srt_timestamp(seconds):
    """
    Wandelt Sekunden in das SRT-Zeitformat um.

    Beispiel:
    65.5 -> 00:01:05,500
    """

    milliseconds = int(round(float(seconds) * 1000))

    hours, remainder = divmod(
        milliseconds,
        3_600_000
    )

    minutes, remainder = divmod(
        remainder,
        60_000
    )

    seconds, milliseconds = divmod(
        remainder,
        1_000
    )

    return (
        f"{hours:02}:"
        f"{minutes:02}:"
        f"{seconds:02},"
        f"{milliseconds:03}"
    )


# ------------------------------------------------------------
# VTT Zeitformat
# ------------------------------------------------------------

def vtt_timestamp(seconds):
    """
    Wandelt Sekunden in das VTT-Zeitformat um.
    """

    milliseconds = int(round(float(seconds) * 1000))

    hours, remainder = divmod(
        milliseconds,
        3_600_000
    )

    minutes, remainder = divmod(
        remainder,
        60_000
    )

    seconds, milliseconds = divmod(
        remainder,
        1_000
    )

    return (
        f"{hours:02}:"
        f"{minutes:02}:"
        f"{seconds:02}."
        f"{milliseconds:03}"
    )


# ------------------------------------------------------------
# SRT erstellen
# ------------------------------------------------------------

def make_srt(segments):
    """
    Erstellt aus Whisper-Segmenten eine SRT-Datei.
    """

    blocks = []

    subtitle_number = 1

    for segment in segments:

        text = segment.get(
            "text",
            ""
        ).strip()

        if not text:
            continue

        start = segment.get(
            "start",
            0
        )

        end = segment.get(
            "end",
            0
        )

        block = (
            f"{subtitle_number}\n"
            f"{srt_timestamp(start)} --> "
            f"{srt_timestamp(end)}\n"
            f"{text}\n"
        )

        blocks.append(block)

        subtitle_number += 1

    return "\n".join(blocks)


# ------------------------------------------------------------
# VTT erstellen
# ------------------------------------------------------------

def make_vtt(segments):
    """
    Erstellt aus Whisper-Segmenten eine VTT-Datei.
    """

    lines = [
        "WEBVTT",
        "",
    ]

    for segment in segments:

        text = segment.get(
            "text",
            ""
        ).strip()

        if not text:
            continue

        start = segment.get(
            "start",
            0
        )

        end = segment.get(
            "end",
            0
        )

        lines.append(
            f"{vtt_timestamp(start)} --> "
            f"{vtt_timestamp(end)}"
        )

        lines.append(text)

        lines.append("")

    return "\n".join(lines)


# ------------------------------------------------------------
# FFmpeg finden
# ------------------------------------------------------------

def ensure_ffmpeg():
    """
    Prüft, ob FFmpeg verfügbar ist.
    """

    ffmpeg = shutil.which("ffmpeg")

    if ffmpeg:
        return ffmpeg

    # Einige typische Windows-Installationsorte
    common_paths = [
        Path(r"C:\ffmpeg\bin\ffmpeg.exe"),
        Path(r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"),
        Path(r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe"),
    ]

    for path in common_paths:

        if path.exists():

            # FFmpeg zum aktuellen PATH hinzufügen
            os.environ["PATH"] = (
                str(path.parent)
                + os.pathsep
                + os.environ.get("PATH", "")
            )

            return str(path)

    return None


# ============================================================
# Hauptprogramm
# ============================================================

class TranscriberApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Video & Audio Transcriber"
        )

        self.root.geometry(
            "1050x780"
        )

        self.root.minsize(
            900,
            680
        )

        # Lokale Dateien
        self.local_files = []

        # Geladenes Whisper-Modell
        self.model = None
        self.loaded_model_name = None

        # Abbrechen
        self.stop_event = threading.Event()

        # GUI Variablen
        self.language_var = tk.StringVar(
            value="Automatisch erkennen"
        )

        self.model_var = tk.StringVar(
            value="small"
        )

        self.output_dir_var = tk.StringVar(
            value=str(
                Path.home()
                / "Documents"
                / "Transcripts"
            )
        )

        self.youtube_var = tk.StringVar()

        self.status_var = tk.StringVar(
            value="Bereit."
        )

        self.detected_language_var = tk.StringVar(
            value="-"
        )

        # Ausgabeformate
        self.txt_var = tk.BooleanVar(
            value=True
        )

        self.docx_var = tk.BooleanVar(
            value=True
        )

        self.srt_var = tk.BooleanVar(
            value=True
        )

        self.vtt_var = tk.BooleanVar(
            value=False
        )

        self.build_ui()

    # ========================================================
    # GUI
    # ========================================================

    def build_ui(self):

        style = ttk.Style()

        try:
            style.configure(
                "Title.TLabel",
                font=(
                    "Segoe UI",
                    18,
                    "bold"
                )
            )

            style.configure(
                "Section.TLabel",
                font=(
                    "Segoe UI",
                    11,
                    "bold"
                )
            )

        except tk.TclError:
            pass

        main = ttk.Frame(
            self.root,
            padding=18
        )

        main.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # Titel
        # ----------------------------------------------------

        ttk.Label(
            main,
            text="🎙 Video & Audio Transcriber",
            style="Title.TLabel"
        ).pack(
            anchor="w"
        )

        ttk.Label(
            main,
            text=(
                "Lokale Videos, Audiodateien und "
                "YouTube-Videos mit Whisper transkribieren."
            )
        ).pack(
            anchor="w",
            pady=(2, 15)
        )

        # ----------------------------------------------------
        # Quelle
        # ----------------------------------------------------

        source_frame = ttk.LabelFrame(
            main,
            text="1. Quelle",
            padding=12
        )

        source_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        button_row = ttk.Frame(
            source_frame
        )

        button_row.pack(
            fill="x"
        )

        ttk.Button(
            button_row,
            text="📁 Lokale Dateien auswählen",
            command=self.choose_files
        ).pack(
            side="left"
        )

        ttk.Button(
            button_row,
            text="🗑 Auswahl leeren",
            command=self.clear_files
        ).pack(
            side="left",
            padx=(8, 0)
        )

        self.file_count_label = ttk.Label(
            button_row,
            text="0 Dateien ausgewählt"
        )

        self.file_count_label.pack(
            side="left",
            padx=12
        )

        # ----------------------------------------------------
        # Dateiliste
        # ----------------------------------------------------

        self.file_list = tk.Listbox(
            source_frame,
            height=5
        )

        self.file_list.pack(
            fill="x",
            pady=(10, 8)
        )

        # ----------------------------------------------------
        # YouTube
        # ----------------------------------------------------

        youtube_row = ttk.Frame(
            source_frame
        )

        youtube_row.pack(
            fill="x"
        )

        ttk.Label(
            youtube_row,
            text="YouTube URL:"
        ).pack(
            side="left"
        )

        ttk.Entry(
            youtube_row,
            textvariable=self.youtube_var
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=8
        )

        ttk.Label(
            source_frame,
            text=(
                "Du kannst lokale Dateien und eine "
                "YouTube-URL gleichzeitig hinzufügen."
            )
        ).pack(
            anchor="w"
        )

        # ----------------------------------------------------
        # Einstellungen
        # ----------------------------------------------------

        settings_frame = ttk.LabelFrame(
            main,
            text="2. Einstellungen",
            padding=12
        )

        settings_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        grid = ttk.Frame(
            settings_frame
        )

        grid.pack(
            fill="x"
        )

        # Sprache
        ttk.Label(
            grid,
            text="Sprache:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 8)
        )

        ttk.Combobox(
            grid,
            textvariable=self.language_var,
            values=list(
                LANGUAGES.keys()
            ),
            state="readonly",
            width=23
        ).grid(
            row=0,
            column=1,
            sticky="w"
        )

        # Modell
        ttk.Label(
            grid,
            text="Whisper Modell:"
        ).grid(
            row=0,
            column=2,
            sticky="w",
            padx=(30, 8)
        )

        ttk.Combobox(
            grid,
            textvariable=self.model_var,
            values=MODELS,
            state="readonly",
            width=15
        ).grid(
            row=0,
            column=3,
            sticky="w"
        )

        ttk.Label(
            grid,
            text=(
                "Größere Modelle = meist bessere "
                "Genauigkeit, aber langsamer."
            )
        ).grid(
            row=0,
            column=4,
            sticky="w",
            padx=(15, 0)
        )

        # ----------------------------------------------------
        # Ausgabeordner
        # ----------------------------------------------------

        output_frame = ttk.Frame(
            settings_frame
        )

        output_frame.pack(
            fill="x",
            pady=(12, 0)
        )

        ttk.Label(
            output_frame,
            text="Ausgabeordner:"
        ).pack(
            side="left"
        )

        ttk.Entry(
            output_frame,
            textvariable=self.output_dir_var
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=8
        )

        ttk.Button(
            output_frame,
            text="📁",
            width=4,
            command=self.choose_output_folder
        ).pack(
            side="left"
        )

        # ----------------------------------------------------
        # Ausgabeformate
        # ----------------------------------------------------

        formats_frame = ttk.Frame(
            settings_frame
        )

        formats_frame.pack(
            fill="x",
            pady=(10, 0)
        )

        ttk.Label(
            formats_frame,
            text="Ausgabe:"
        ).pack(
            side="left"
        )

        ttk.Checkbutton(
            formats_frame,
            text="TXT",
            variable=self.txt_var
        ).pack(
            side="left",
            padx=8
        )

        ttk.Checkbutton(
            formats_frame,
            text="Word (.docx)",
            variable=self.docx_var
        ).pack(
            side="left",
            padx=8
        )

        ttk.Checkbutton(
            formats_frame,
            text="SRT",
            variable=self.srt_var
        ).pack(
            side="left",
            padx=8
        )

        ttk.Checkbutton(
            formats_frame,
            text="VTT",
            variable=self.vtt_var
        ).pack(
            side="left",
            padx=8
        )

        # ----------------------------------------------------
        # Buttons
        # ----------------------------------------------------

        action_frame = ttk.Frame(
            main
        )

        action_frame.pack(
            fill="x",
            pady=(2, 10)
        )

        self.start_button = ttk.Button(
            action_frame,
            text="🎙 TRANSKRIBIEREN",
            command=self.start_transcription
        )

        self.start_button.pack(
            side="left"
        )

        self.stop_button = ttk.Button(
            action_frame,
            text="⛔ Abbrechen",
            command=self.cancel_transcription,
            state="disabled"
        )

        self.stop_button.pack(
            side="left",
            padx=8
        )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        status_frame = ttk.LabelFrame(
            main,
            text="3. Status",
            padding=10
        )

        status_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        ttk.Label(
            status_frame,
            textvariable=self.status_var
        ).pack(
            anchor="w"
        )

        self.progress = ttk.Progressbar(
            status_frame,
            mode="indeterminate"
        )

        self.progress.pack(
            fill="x",
            pady=(8, 5)
        )

        lang_row = ttk.Frame(
            status_frame
        )

        lang_row.pack(
            fill="x"
        )

        ttk.Label(
            lang_row,
            text="Erkannte Sprache:"
        ).pack(
            side="left"
        )

        ttk.Label(
            lang_row,
            textvariable=self.detected_language_var
        ).pack(
            side="left",
            padx=6
        )

        # ----------------------------------------------------
        # Transkript
        # ----------------------------------------------------

        transcript_frame = ttk.LabelFrame(
            main,
            text="4. Transkript",
            padding=10
        )

        transcript_frame.pack(
            fill="both",
            expand=True
        )

        text_container = ttk.Frame(
            transcript_frame
        )

        text_container.pack(
            fill="both",
            expand=True
        )

        self.transcript_text = tk.Text(
            text_container,
            wrap="word",
            font=(
                "Segoe UI",
                10
            )
        )

        self.transcript_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = ttk.Scrollbar(
            text_container,
            orient="vertical",
            command=self.transcript_text.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.transcript_text.configure(
            yscrollcommand=scrollbar.set
        )

    # ========================================================
    # Dateien auswählen
    # ========================================================

    def choose_files(self):

        files = filedialog.askopenfilenames(
            title="Video- oder Audiodateien auswählen",
            filetypes=[
                (
                    "Video & Audio",
                    "*.mp4 *.mkv *.avi *.mov *.webm *.wmv "
                    "*.mpeg *.mpg *.m4v *.ts *.mp3 *.wav "
                    "*.m4a *.flac *.aac *.ogg *.opus *.wma"
                ),
                (
                    "Alle Dateien",
                    "*.*"
                ),
            ],
        )

        for file_path in files:

            path = Path(
                file_path
            )

            if path.suffix.lower() not in SUPPORTED_LOCAL_EXTENSIONS:
                continue

            if str(path) not in self.local_files:

                self.local_files.append(
                    str(path)
                )

                self.file_list.insert(
                    "end",
                    str(path)
                )

        self.update_file_count()

    # ========================================================
    # Dateien löschen
    # ========================================================

    def clear_files(self):

        self.local_files.clear()

        self.file_list.delete(
            0,
            "end"
        )

        self.update_file_count()

    # ========================================================
    # Dateianzahl aktualisieren
    # ========================================================

    def update_file_count(self):

        count = len(
            self.local_files
        )

        if count == 1:
            text = "1 Datei ausgewählt"
        else:
            text = f"{count} Dateien ausgewählt"

        self.file_count_label.config(
            text=text
        )

    # ========================================================
    # Ausgabeordner auswählen
    # ========================================================

    def choose_output_folder(self):

        folder = filedialog.askdirectory(
            title="Ausgabeordner auswählen"
        )

        if folder:
            self.output_dir_var.set(
                folder
            )

    # ========================================================
    # Status aktualisieren
    # ========================================================

    def set_status(self, text):

        self.root.after(
            0,
            lambda: self.status_var.set(text)
        )

    # ========================================================
    # Erkannte Sprache anzeigen
    # ========================================================

    def set_detected_language(self, text):

        self.root.after(
            0,
            lambda: self.detected_language_var.set(text)
        )

    # ========================================================
    # Transkript in GUI anzeigen
    # ========================================================

    def append_transcript(self, text):

        def update():

            self.transcript_text.insert(
                "end",
                text
            )

            self.transcript_text.see(
                "end"
            )

        self.root.after(
            0,
            update
        )

    # ========================================================
    # Progressbar starten
    # ========================================================

    def start_progress(self):

        self.root.after(
            0,
            self.progress.start,
            12
        )

    # ========================================================
    # Progressbar stoppen
    # ========================================================

    def stop_progress(self):

        self.root.after(
            0,
            self.progress.stop
        )

    # ========================================================
    # Transkription starten
    # ========================================================

    def start_transcription(self):

        youtube_url = (
            self.youtube_var
            .get()
            .strip()
        )

        # Keine Quelle
        if not self.local_files and not youtube_url:

            messagebox.showwarning(
                "Keine Quelle",
                (
                    "Bitte wähle lokale Dateien aus "
                    "oder gib eine YouTube-URL ein."
                )
            )

            return

        # URL prüfen
        if youtube_url:

            if not (
                youtube_url.startswith("https://")
                or youtube_url.startswith("http://")
            ):

                messagebox.showwarning(
                    "Ungültige URL",
                    "Bitte gib eine vollständige YouTube-URL ein."
                )

                return

        # Ausgabeformat prüfen
        if not any(
            [
                self.txt_var.get(),
                self.docx_var.get(),
                self.srt_var.get(),
                self.vtt_var.get(),
            ]
        ):

            messagebox.showwarning(
                "Keine Ausgabe",
                "Bitte wähle mindestens ein Ausgabeformat."
            )

            return

        # FFmpeg prüfen
        ffmpeg = ensure_ffmpeg()

        if not ffmpeg:

            messagebox.showerror(
                "FFmpeg fehlt",
                (
                    "FFmpeg wurde nicht gefunden.\n\n"
                    "Bitte installiere FFmpeg und stelle sicher, "
                    "dass ffmpeg.exe im PATH verfügbar ist."
                )
            )

            return

        # Ausgabeordner
        output_dir = Path(
            self.output_dir_var
            .get()
            .strip()
        )

        if not output_dir:

            messagebox.showwarning(
                "Ausgabeordner",
                "Bitte wähle einen Ausgabeordner."
            )

            return

        try:

            output_dir.mkdir(
                parents=True,
                exist_ok=True
            )

        except Exception as exc:

            messagebox.showerror(
                "Fehler",
                (
                    "Der Ausgabeordner konnte "
                    f"nicht erstellt werden:\n{exc}"
                )
            )

            return

        # Zustand vorbereiten
        self.stop_event.clear()

        self.start_button.config(
            state="disabled"
        )

        self.stop_button.config(
            state="normal"
        )

        self.transcript_text.delete(
            "1.0",
            "end"
        )

        self.detected_language_var.set(
            "-"
        )

        self.start_progress()

        files = list(
            self.local_files
        )

        model_name = (
            self.model_var
            .get()
        )

        language_code = LANGUAGES[
            self.language_var.get()
        ]

        # Eigener Thread
        thread = threading.Thread(
            target=self.transcription_worker,
            args=(
                files,
                youtube_url,
                model_name,
                language_code,
                output_dir,
            ),
            daemon=True
        )

        thread.start()

    # ========================================================
    # Transkription abbrechen
    # ========================================================

    def cancel_transcription(self):

        self.stop_event.set()

        self.set_status(
            (
                "Abbruch angefordert. "
                "Die aktuelle Transkription wird "
                "noch beendet."
            )
        )

    # ========================================================
    # GUI nach Ende zurücksetzen
    # ========================================================

    def finish_ui(self):

        self.stop_progress()

        self.start_button.config(
            state="normal"
        )

        self.stop_button.config(
            state="disabled"
        )

    # ========================================================
    # Whisper Modell laden
    # ========================================================

    def load_whisper_model(
        self,
        model_name
    ):

        # Bereits geladenes Modell verwenden
        if (
            self.model is not None
            and self.loaded_model_name == model_name
        ):

            return self.model

        self.set_status(
            (
                f"Whisper-Modell '{model_name}' wird geladen. "
                "Beim ersten Start kann der Download etwas dauern..."
            )
        )

        # Whisper erst hier importieren
        # Dadurch startet die GUI schneller.
        import whisper

        self.model = whisper.load_model(
            model_name
        )

        self.loaded_model_name = (
            model_name
        )

        return self.model

    # ========================================================
    # Datei transkribieren
    # ========================================================

    def transcribe_file(
        self,
        model,
        file_path,
        language_code
    ):

        options = {
            "task": "transcribe",

            # Whisper schreibt nicht selbst in die Konsole.
            "verbose": False,

            # GPU benutzt FP16.
            # CPU benutzt FP32.
            "fp16": (
                model.device.type == "cuda"
            ),
        }

        # Sprache vorgeben,
        # wenn der Benutzer sie ausgewählt hat.
        if language_code:

            options["language"] = (
                language_code
            )

        result = model.transcribe(
            str(file_path),
            **options
        )

        return result

    # ========================================================
    # Dateien speichern
    # ========================================================

    def save_outputs(
        self,
        base_name,
        result,
        output_dir
    ):

        text = result.get(
            "text",
            ""
        ).strip()

        segments = result.get(
            "segments",
            []
        )

        saved = []

        # ----------------------------------------------------
        # TXT
        # ----------------------------------------------------

        if self.txt_var.get():

            path = (
                output_dir
                / f"{base_name}.txt"
            )

            path.write_text(
                text,
                encoding="utf-8-sig"
            )

            saved.append(
                path.name
            )

        # ----------------------------------------------------
        # Word
        # ----------------------------------------------------

        if self.docx_var.get():

            from docx import Document
            from docx.enum.text import WD_ALIGN_PARAGRAPH

            path = (
                output_dir
                / f"{base_name}.docx"
            )

            document = Document()

            document.add_heading(
                base_name,
                level=1
            )

            paragraph = (
                document.add_paragraph(
                    text
                )
            )

            # Bei Persisch rechtsbündig.
            if (
                self.language_var.get()
                == "Persisch / Farsi"
            ):

                paragraph.alignment = (
                    WD_ALIGN_PARAGRAPH.RIGHT
                )

            document.save(
                path
            )

            saved.append(
                path.name
            )

        # ----------------------------------------------------
        # SRT
        # ----------------------------------------------------

        if self.srt_var.get():

            path = (
                output_dir
                / f"{base_name}.srt"
            )

            path.write_text(
                make_srt(segments),
                encoding="utf-8-sig"
            )

            saved.append(
                path.name
            )

        # ----------------------------------------------------
        # VTT
        # ----------------------------------------------------

        if self.vtt_var.get():

            path = (
                output_dir
                / f"{base_name}.vtt"
            )

            path.write_text(
                make_vtt(segments),
                encoding="utf-8"
            )

            saved.append(
                path.name
            )

        return saved

    # ========================================================
    # YouTube Audio herunterladen
    # ========================================================

    def download_youtube_audio(
        self,
        url,
        temp_dir
    ):
        """
        Lädt die Audiospur eines YouTube-Videos herunter.

        Wir versuchen mehrere YouTube-Konfigurationen,
        weil YouTube die Auslieferung regelmäßig verändert.
        """

        from yt_dlp import YoutubeDL

        self.set_status(
            "YouTube-Video wird vorbereitet..."
        )

        output_template = str(
            Path(temp_dir)
            / "youtube_audio.%(ext)s"
        )

        # ----------------------------------------------------
        # Prüfen, ob Deno vorhanden ist
        # ----------------------------------------------------

        deno = shutil.which("deno")

        # ----------------------------------------------------
        # Grundkonfiguration
        # ----------------------------------------------------

        base_options = {
            # Nur Audio
            "format": "bestaudio/best",

            "outtmpl": output_template,

            # Keine Playlists
            "noplaylist": True,

            # Weniger Konsolenausgabe
            "quiet": True,

            "no_warnings": False,

            # Netzwerkversuche
            "retries": 3,

            "fragment_retries": 3,

            # Audio mit FFmpeg in WAV umwandeln
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                }
            ],
        }

        # ----------------------------------------------------
        # Deno verwenden
        # ----------------------------------------------------

        if deno:

            base_options[
                "js_runtimes"
            ] = {
                "deno": {}
            }

        # ----------------------------------------------------
        # Verschiedene YouTube-Konfigurationen
        #
        # Erst normale Konfiguration.
        # Wenn YouTube 403 liefert, versuchen wir
        # den Android-Client.
        # ----------------------------------------------------

        configurations = [

            {
                "name": "Standard",
                "options": {}
            },

            {
                "name": "Android-Client",
                "options": {
                    "extractor_args": {
                        "youtube": {
                            "player_client": [
                                "android"
                            ]
                        }
                    }
                }
            },
        ]

        last_error = None

        # ----------------------------------------------------
        # Versuche nacheinander
        # ----------------------------------------------------

        for attempt in configurations:

            name = attempt["name"]

            self.set_status(
                f"YouTube: {name} wird versucht..."
            )

            # Neue Konfiguration erstellen
            ydl_options = dict(
                base_options
            )

            # Zusätzliche Optionen übernehmen
            ydl_options.update(
                attempt["options"]
            )

            try:

                with YoutubeDL(
                    ydl_options
                ) as ydl:

                    info = ydl.extract_info(
                        url,
                        download=True
                    )

                title = (
                    info.get("title")
                    or "youtube_transcript"
                )

                # ------------------------------------------------
                # WAV suchen
                # ------------------------------------------------

                wav_files = list(
                    Path(temp_dir).glob(
                        "*.wav"
                    )
                )

                if wav_files:

                    self.set_status(
                        f"YouTube erfolgreich geladen: {title}"
                    )

                    return (
                        wav_files[0],
                        title
                    )

                # ------------------------------------------------
                # Falls WAV nicht existiert,
                # nach anderer Mediendatei suchen
                # ------------------------------------------------

                media_files = [

                    path

                    for path in Path(
                        temp_dir
                    ).iterdir()

                    if (
                        path.is_file()
                        and path.suffix.lower()
                        in SUPPORTED_LOCAL_EXTENSIONS
                    )
                ]

                if media_files:

                    self.set_status(
                        f"YouTube erfolgreich geladen: {title}"
                    )

                    return (
                        media_files[0],
                        title
                    )

                raise RuntimeError(
                    "YouTube-Audio wurde nicht gefunden."
                )

            except Exception as exc:

                last_error = exc

                error_text = str(
                    exc
                ).lower()

                # ------------------------------------------------
                # Bei 403 nächsten Client versuchen
                # ------------------------------------------------

                if (
                    "403" in error_text
                    or "forbidden" in error_text
                ):

                    self.set_status(
                        (
                            f"YouTube: {name} wurde "
                            "von YouTube abgelehnt. "
                            "Nächster Versuch..."
                        )
                    )

                    continue

                # Bei anderen Fehlern ebenfalls
                # nächsten Versuch testen.
                continue

        # ----------------------------------------------------
        # Alle Versuche fehlgeschlagen
        # ----------------------------------------------------

        raise RuntimeError(
            "YouTube konnte nicht heruntergeladen werden.\n\n"
            "Die letzten Fehlermeldung war:\n"
            f"{last_error}\n\n"
            "Mögliche Ursachen:\n"
            "• YouTube blockiert den verwendeten Client.\n"
            "• yt-dlp/EJS ist nicht aktuell.\n"
            "• Deno fehlt oder ist nicht im PATH.\n"
            "• Das Video benötigt eine Anmeldung.\n"
            "• YouTube hat die Auslieferung erneut geändert."
        )

    # ========================================================
    # Haupt-Worker
    # ========================================================

    def transcription_worker(
        self,
        files,
        youtube_url,
        model_name,
        language_code,
        output_dir
    ):

        successful = []
        failed = []

        try:

            # Whisper laden
            model = self.load_whisper_model(
                model_name
            )

            # Lokale Quellen
            sources = list(
                files
            )

            # Temporärer Ordner für YouTube
            if youtube_url:

                temp_context = (
                    tempfile.TemporaryDirectory(
                        prefix="transcriber_"
                    )
                )

            else:

                temp_context = None

            try:

                # ------------------------------------------------
                # YouTube herunterladen
                # ------------------------------------------------

                if youtube_url:

                    youtube_file, youtube_title = (
                        self.download_youtube_audio(
                            youtube_url,
                            temp_context.name
                        )
                    )

                    sources.append(
                        (
                            str(youtube_file),
                            youtube_title
                        )
                    )

                total = len(
                    sources
                )

                # ------------------------------------------------
                # Dateien nacheinander verarbeiten
                # ------------------------------------------------

                for index, source in enumerate(
                    sources,
                    start=1
                ):

                    # Wenn Abbruch angefordert wurde
                    if self.stop_event.is_set():
                        break

                    # YouTube oder lokale Datei
                    if isinstance(
                        source,
                        tuple
                    ):

                        file_path = Path(
                            source[0]
                        )

                        original_name = (
                            source[1]
                        )

                    else:

                        file_path = Path(
                            source
                        )

                        original_name = (
                            file_path.stem
                        )

                    self.set_status(
                        (
                            f"Transkribiere "
                            f"{index}/{total}: "
                            f"{original_name}"
                        )
                    )

                    try:

                        # ------------------------------------------------
                        # Whisper
                        # ------------------------------------------------

                        result = self.transcribe_file(
                            model,
                            file_path,
                            language_code
                        )

                        # Erkannte Sprache
                        detected_code = (
                            result.get(
                                "language",
                                "-"
                            )
                        )

                        self.set_detected_language(
                            detected_code
                        )

                        # Text
                        text = (
                            result.get(
                                "text",
                                ""
                            ).strip()
                        )

                        if not text:

                            raise RuntimeError(
                                "Whisper hat keinen Text erkannt."
                            )

                        # Dateiname
                        base_name = safe_filename(
                            original_name
                        )

                        # Ausgaben speichern
                        saved = self.save_outputs(
                            base_name,
                            result,
                            output_dir
                        )

                        successful.append(
                            base_name
                        )

                        # ------------------------------------------------
                        # Ergebnis in GUI
                        # ------------------------------------------------

                        preview = (
                            "\n\n"
                            + "=" * 70
                            + "\n"
                            + base_name
                            + "\n"
                            + "=" * 70
                            + "\n"
                            + text
                            + "\n"
                        )

                        self.append_transcript(
                            preview
                        )

                        self.set_status(
                            (
                                f"Fertig: {original_name} "
                                f"— gespeichert: "
                                f"{', '.join(saved)}"
                            )
                        )

                    except Exception as exc:

                        failed.append(
                            (
                                str(original_name),
                                str(exc)
                            )
                        )

                # ------------------------------------------------
                # Abschluss
                # ------------------------------------------------

                if self.stop_event.is_set():

                    self.set_status(
                        (
                            f"Abgebrochen. "
                            f"{len(successful)} Datei(en) "
                            "wurden fertig verarbeitet."
                        )
                    )

                else:

                    self.set_status(
                        (
                            f"Fertig. "
                            f"{len(successful)} Datei(en) "
                            "erfolgreich verarbeitet."
                        )
                    )

            finally:

                # Temporäre YouTube-Datei löschen
                if temp_context:

                    temp_context.cleanup()

        except Exception as exc:

            # Fehler anzeigen
            self.root.after(
                0,
                lambda error=exc: messagebox.showerror(
                    "Transkriptionsfehler",
                    (
                        "Das Programm konnte die "
                        "Transkription nicht starten:\n\n"
                        f"{error}"
                    )
                )
            )

            self.set_status(
                "Fehler."
            )

        finally:

            # Fehler einzelner Dateien
            if failed:

                error_text = "\n\n".join(
                    (
                        f"{name}\n"
                        f"{error}"
                    )

                    for name, error in failed
                )

                self.root.after(
                    0,
                    lambda text=error_text: (
                        messagebox.showwarning(
                            "Einige Dateien konnten nicht verarbeitet werden",
                            text
                        )
                    )
                )

            # GUI wieder aktivieren
            self.root.after(
                0,
                self.finish_ui
            )


# ============================================================
# Programm starten
# ============================================================

def main():

    root = tk.Tk()

    app = TranscriberApp(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()
