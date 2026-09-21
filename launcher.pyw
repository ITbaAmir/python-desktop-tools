# ============================================================
# Python Desktop Tools Launcher
# ============================================================
#
# Was macht dieses Programm?
#
# Dieses Programm durchsucht automatisch alle Unterordner
# und findet dort Python-Programme.
#
# Gefundene Programme werden automatisch als Buttons angezeigt.
#
# Neue Programme müssen NICHT manuell zum Launcher hinzugefügt
# werden. Einfach einen neuen Unterordner mit einer .py oder
# .pyw Datei hinzufügen.
#
# Beispiel:
#
# python-desktop-tools
# │
# ├── launcher.pyw
# │
# ├── qr-code-generator
# │   └── qr_code_generator.py
# │
# ├── snake-game
# │   └── snake_game.py
# │
# └── password-generator
#     └── password_generator.py
#
# Beim nächsten Start erkennt der Launcher automatisch alle drei.
#
# Benötigte Bibliotheken:
# Keine.
#
# ============================================================


import tkinter as tk
from tkinter import messagebox

import subprocess
import sys

from pathlib import Path


# ============================================================
# Hauptordner
# ============================================================

BASE_FOLDER = Path(__file__).parent


# ============================================================
# Dateien, die NICHT als Programme angezeigt werden sollen
# ============================================================

IGNORED_FILES = {

    "launcher.py",
    "launcher.pyw",

    "__init__.py",

    "setup.py",

    "conftest.py"

}


# ============================================================
# Ordner, die ignoriert werden sollen
# ============================================================

IGNORED_FOLDERS = {

    ".git",

    ".github",

    ".idea",

    ".vscode",

    "__pycache__",

    "venv",

    ".venv",

    "env",

    ".env",

    "node_modules"

}


# ============================================================
# Schönen Programmnamen erstellen
# ============================================================
#
# Beispiel:
#
# qr_code_generator.py
#
# wird:
#
# Qr Code Generator
# ============================================================

def create_program_name(file_path):

    # Dateiendung entfernen
    name = file_path.stem

    # Unterstriche und Bindestriche durch Leerzeichen ersetzen
    name = name.replace(
        "_",
        " "
    )

    name = name.replace(
        "-",
        " "
    )

    # Jedes Wort groß schreiben
    name = name.title()

    # Einige häufige Abkürzungen schöner darstellen
    replacements = {

        "Qr": "QR",

        "Pdf": "PDF",

        "Mp3": "MP3",

        "Mp4": "MP4",

        "Txt": "TXT",

        "Csv": "CSV",

        "Ico": "ICO",

        "Url": "URL"

    }

    words = name.split()

    words = [

        replacements.get(
            word,
            word
        )

        for word in words

    ]

    return " ".join(
        words
    )


# ============================================================
# Prüfen, ob ein Pfad ignoriert werden soll
# ============================================================

def should_ignore(file_path):

    # Datei selbst ignorieren
    if file_path.name.lower() in {

        name.lower()

        for name in IGNORED_FILES

    }:

        return True

    # Prüfen, ob die Datei innerhalb eines ignorierten
    # Ordners liegt.
    for part in file_path.parts:

        if part.lower() in {

            folder.lower()

            for folder in IGNORED_FOLDERS

        }:

            return True

    return False


# ============================================================
# Programme automatisch finden
# ============================================================

def find_programs():

    programs = []

    # ========================================================
    # Alle Dateien in allen Unterordnern durchsuchen
    # ========================================================

    for file_path in BASE_FOLDER.rglob("*"):

        # Nur echte Dateien
        if not file_path.is_file():

            continue

        # Nur Python-Dateien
        if file_path.suffix.lower() not in {

            ".py",
            ".pyw"

        }:

            continue

        # Ignorierte Dateien überspringen
        if should_ignore(
            file_path
        ):

            continue

        # Programmnamen erstellen
        program_name = create_program_name(
            file_path
        )

        programs.append(

            (
                program_name,
                file_path
            )

        )

    # Alphabetisch sortieren
    programs.sort(

        key=lambda item:
        item[0].lower()

    )

    return programs


# ============================================================
# Programm starten
# ============================================================

def start_program(file_path):

    try:

        # Aktuell verwendetes Python finden
        python_exe = Path(
            sys.executable
        )

        # ====================================================
        # pythonw.exe suchen
        # ====================================================
        #
        # pythonw.exe startet Python-Programme ohne Terminal.
        # ====================================================

        pythonw_exe = python_exe.with_name(
            "pythonw.exe"
        )

        # Falls pythonw.exe nicht existiert,
        # normales Python benutzen.
        if not pythonw_exe.exists():

            pythonw_exe = python_exe

        # ====================================================
        # Programm starten
        # ====================================================

        subprocess.Popen(

            [

                str(
                    pythonw_exe
                ),

                str(
                    file_path
                )

            ],

            # Arbeitsordner wird der Ordner des Programms.
            cwd=str(
                file_path.parent
            )

        )

    except Exception as error:

        messagebox.showerror(

            "Fehler",

            f"Das Programm konnte nicht gestartet werden:\n\n"
            f"{error}"

        )


# ============================================================
# Programmliste neu laden
# ============================================================

def refresh_programs():

    # Alte Buttons entfernen
    for widget in program_frame.winfo_children():

        widget.destroy()

    programs = find_programs()

    program_count_label.config(

        text=f"{len(programs)} Programme gefunden"

    )

    # ========================================================
    # Falls keine Programme gefunden wurden
    # ========================================================

    if not programs:

        empty_label = tk.Label(

            program_frame,

            text=(
                "Keine Python-Programme gefunden.\n\n"
                "Lege deine Programme in Unterordnern "
                "neben launcher.pyw ab."
            ),

            justify="center"

        )

        empty_label.pack(
            pady=30
        )

        return

    # ========================================================
    # Button für jedes gefundene Programm
    # ========================================================

    for program_name, file_path in programs:

        button = tk.Button(

            program_frame,

            text=program_name,

            width=45,

            height=2,

            command=lambda path=file_path:
            start_program(path)

        )

        button.pack(

            pady=5,

            padx=10

        )


# ============================================================
# Mausrad für Scrollen
# ============================================================

def mouse_wheel(event):

    canvas.yview_scroll(

        int(
            -1 * (event.delta / 120)
        ),

        "units"

    )


# ============================================================
# Hauptfenster
# ============================================================

window = tk.Tk()


window.title(
    "Python Desktop Tools"
)


window.geometry(
    "540x680"
)


window.minsize(
    480,
    500
)


# ============================================================
# Titel
# ============================================================

title_label = tk.Label(

    window,

    text="Python Desktop Tools",

    font=(
        "Segoe UI",
        20,
        "bold"
    )

)


title_label.pack(
    pady=(25, 5)
)


description_label = tk.Label(

    window,

    text="Wähle ein Programm aus."

)


description_label.pack(
    pady=(0, 5)
)


# ============================================================
# Anzahl gefundener Programme
# ============================================================

program_count_label = tk.Label(

    window,

    text="Programme werden gesucht..."

)


program_count_label.pack(
    pady=(0, 10)
)


# ============================================================
# Neu laden
# ============================================================
#
# Praktisch, falls du einen neuen Ordner hinzufügst,
# während der Launcher bereits geöffnet ist.
# ============================================================

refresh_button = tk.Button(

    window,

    text="Programme neu laden",

    command=refresh_programs,

    width=20

)


refresh_button.pack(
    pady=(0, 10)
)


# ============================================================
# Scrollbarer Programmbereich
# ============================================================

container = tk.Frame(
    window
)


container.pack(

    fill="both",

    expand=True,

    padx=20,

    pady=5

)


canvas = tk.Canvas(

    container,

    highlightthickness=0

)


scrollbar = tk.Scrollbar(

    container,

    orient="vertical",

    command=canvas.yview

)


program_frame = tk.Frame(
    canvas
)


program_window = canvas.create_window(

    (
        0,
        0
    ),

    window=program_frame,

    anchor="nw"

)


# ============================================================
# Scrollbereich aktualisieren
# ============================================================

def update_scroll_region(event=None):

    canvas.configure(

        scrollregion=canvas.bbox(
            "all"
        )

    )


program_frame.bind(

    "<Configure>",

    update_scroll_region

)


# ============================================================
# Inneren Bereich auf Canvas-Breite anpassen
# ============================================================

def resize_program_frame(event):

    canvas.itemconfigure(

        program_window,

        width=event.width

    )


canvas.bind(

    "<Configure>",

    resize_program_frame

)


canvas.configure(

    yscrollcommand=scrollbar.set

)


canvas.pack(

    side="left",

    fill="both",

    expand=True

)


scrollbar.pack(

    side="right",

    fill="y"

)


# ============================================================
# Mausrad aktivieren
# ============================================================

canvas.bind_all(

    "<MouseWheel>",

    mouse_wheel

)


# ============================================================
# Programme beim Start automatisch suchen
# ============================================================

refresh_programs()


# ============================================================
# Hinweis unten
# ============================================================

info_label = tk.Label(

    window,

    text=(
        "Neue Tools werden beim nächsten Start "
        "automatisch erkannt."
    ),

    font=(
        "Segoe UI",
        9
    )

)


info_label.pack(
    pady=10
)


# ============================================================
# Fenster starten
# ============================================================

window.mainloop()
