# ============================================================
# Image Text Extractor / OCR
# ============================================================
#
# Was macht dieses Programm?
#
# Dieses Programm liest Text aus Bildern.
#
# Unterstützte Sprachen:
# - Persisch / Farsi
# - Deutsch
# - Englisch
# - Gemischt: Persisch + Deutsch + Englisch
#
# Funktionen:
# - Ein oder mehrere Bilder auswählen
# - Reihenfolge der Bilder ändern
# - Bildqualität vor OCR automatisch verbessern
# - OCR mit Tesseract
# - Ergebnis im Programm anzeigen und bearbeiten
# - Export als:
#       TXT
#       Word (.docx)
#       PowerPoint (.pptx)
#       oder mehrere Formate gleichzeitig
#
# Unterstützte Bilder:
# - JPG / JPEG
# - PNG
# - BMP
# - TIFF
# - WebP
#
# ============================================================
# PYTHON-BIBLIOTHEKEN INSTALLIEREN
# ============================================================
#
# Einmal im Terminal:
#
# py -m pip install pytesseract pillow opencv-python python-docx python-pptx
#
# ============================================================
# ZUSÄTZLICH:
# ============================================================
#
# Tesseract OCR muss unter Windows installiert sein.
#
# Danach testen:
#
# tesseract --version
#
# und:
#
# tesseract --list-langs
#
# Benötigte Sprachen:
#
# eng
# deu
# fas
#
# ============================================================


# ============================================================
# Standard-Bibliotheken
# ============================================================

import tkinter as tk

from tkinter import (
    ttk,
    filedialog,
    messagebox,
    simpledialog
)

from pathlib import Path

import threading

import shutil

import os


# ============================================================
# Bilder
# ============================================================

from PIL import (
    Image,
    ImageTk,
    ImageOps
)


# ============================================================
# Bildverbesserung
# ============================================================

import cv2

import numpy as np


# ============================================================
# OCR
# ============================================================

import pytesseract


# ============================================================
# Word Export
# ============================================================

from docx import Document

from docx.enum.text import WD_ALIGN_PARAGRAPH

from docx.shared import Pt

from docx.oxml import OxmlElement


# ============================================================
# PowerPoint Export
# ============================================================

from pptx import Presentation

from pptx.util import Inches, Pt as PPTPt

from pptx.enum.text import PP_ALIGN


# ============================================================
# Globale Variablen
# ============================================================

selected_images = []

ocr_results = []

ocr_running = False

current_preview_image = None


# ============================================================
# Sprachzuordnung
# ============================================================

LANGUAGES = {

    "Persisch / Farsi":
        "fas",

    "Deutsch":
        "deu",

    "Englisch":
        "eng",

    "Persisch + Deutsch + Englisch":
        "fas+deu+eng"

}


# ============================================================
# Tesseract suchen
# ============================================================
#
# Das Programm versucht Tesseract automatisch zu finden.
#
# Zuerst:
# - Windows PATH
#
# Danach bekannte Installationsorte.
# ============================================================

def find_tesseract():

    # --------------------------------------------------------
    # Im Windows PATH suchen
    # --------------------------------------------------------

    found = shutil.which(
        "tesseract"
    )


    if found:

        pytesseract.pytesseract.tesseract_cmd = found

        return True


    # --------------------------------------------------------
    # Typische Windows-Pfade
    # --------------------------------------------------------
    
    possible_paths = [

        r"C:\Users\Amir\AppData\Local\Tesseract-OCR\tesseract.exe",

        r"C:\Program Files\Tesseract-OCR\tesseract.exe",

        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"

    ]


    for path in possible_paths:

        if os.path.exists(
            path
        ):

            pytesseract.pytesseract.tesseract_cmd = path

            return True


    return False


# ============================================================
# Tesseract und Sprachen prüfen
# ============================================================

def check_tesseract():

    if not find_tesseract():

        messagebox.showerror(

            "Tesseract nicht gefunden",

            "Tesseract OCR wurde nicht gefunden.\n\n"
            "Bitte installiere Tesseract und starte "
            "das Programm danach erneut."

        )

        return False


    try:

        languages = pytesseract.get_languages(
            config=""
        )


    except Exception as error:

        messagebox.showerror(

            "Tesseract Fehler",

            f"Tesseract konnte nicht gestartet werden:\n\n"
            f"{error}"

        )

        return False


    required_languages = [

        "eng",
        "deu",
        "fas"

    ]


    missing = [

        language

        for language in required_languages

        if language not in languages

    ]


    if missing:

        messagebox.showwarning(

            "Sprachdateien fehlen",

            "Folgende Tesseract-Sprachen fehlen:\n\n"
            + "\n".join(missing)
            + "\n\n"
            "Für alle Funktionen werden benötigt:\n"
            "eng = Englisch\n"
            "deu = Deutsch\n"
            "fas = Persisch"

        )


    return True


# ============================================================
# Bilder hinzufügen
# ============================================================

def add_images():

    files = filedialog.askopenfilenames(

        title="Bilder auswählen",

        filetypes=[

            (
                "Bilddateien",
                "*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.webp"
            ),

            (
                "JPEG",
                "*.jpg *.jpeg"
            ),

            (
                "PNG",
                "*.png"
            ),

            (
                "Alle Dateien",
                "*.*"
            )

        ]

    )


    if not files:

        return


    for file_path in files:

        if file_path not in selected_images:

            selected_images.append(
                file_path
            )


    refresh_image_list()


    if selected_images:

        image_listbox.selection_clear(
            0,
            tk.END
        )

        image_listbox.selection_set(
            len(selected_images) - 1
        )

        image_selected()


    status_label.config(

        text=f"{len(selected_images)} Bild(er) ausgewählt."

    )


# ============================================================
# Bilderliste aktualisieren
# ============================================================

def refresh_image_list():

    image_listbox.delete(
        0,
        tk.END
    )


    for index, image_path in enumerate(

        selected_images,

        start=1

    ):

        image_listbox.insert(

            tk.END,

            f"{index}. {Path(image_path).name}"

        )


    image_count_label.config(

        text=f"{len(selected_images)} Bild(er)"

    )


# ============================================================
# Ausgewähltes Bild entfernen
# ============================================================

def remove_image():

    selection = image_listbox.curselection()


    if not selection:

        return


    index = selection[0]


    selected_images.pop(
        index
    )


    refresh_image_list()


    preview_label.config(

        image="",

        text="Keine Vorschau"

    )


    preview_label.image = None


# ============================================================
# Alle Bilder entfernen
# ============================================================

def clear_images():

    if not selected_images:

        return


    answer = messagebox.askyesno(

        "Liste leeren",

        "Alle ausgewählten Bilder entfernen?"

    )


    if not answer:

        return


    selected_images.clear()


    refresh_image_list()


    preview_label.config(

        image="",

        text="Keine Vorschau"

    )


    preview_label.image = None


# ============================================================
# Bild nach oben
# ============================================================

def move_up():

    selection = image_listbox.curselection()


    if not selection:

        return


    index = selection[0]


    if index == 0:

        return


    selected_images[index - 1], selected_images[index] = (

        selected_images[index],

        selected_images[index - 1]

    )


    refresh_image_list()


    image_listbox.selection_set(
        index - 1
    )


# ============================================================
# Bild nach unten
# ============================================================

def move_down():

    selection = image_listbox.curselection()


    if not selection:

        return


    index = selection[0]


    if index >= len(selected_images) - 1:

        return


    selected_images[index + 1], selected_images[index] = (

        selected_images[index],

        selected_images[index + 1]

    )


    refresh_image_list()


    image_listbox.selection_set(
        index + 1
    )


# ============================================================
# Bildvorschau
# ============================================================

def image_selected(event=None):

    global current_preview_image


    selection = image_listbox.curselection()


    if not selection:

        return


    image_path = selected_images[
        selection[0]
    ]


    try:

        image = Image.open(
            image_path
        )


        # EXIF-Drehung berücksichtigen
        image = ImageOps.exif_transpose(
            image
        )


        image.thumbnail(

            (
                380,
                300
            ),

            Image.Resampling.LANCZOS

        )


        photo = ImageTk.PhotoImage(
            image
        )


        preview_label.config(

            image=photo,

            text=""

        )


        preview_label.image = photo

        current_preview_image = photo


    except Exception as error:

        preview_label.config(

            image="",

            text=f"Vorschau nicht möglich:\n{error}"

        )


# ============================================================
# Bild verbessern
# ============================================================
#
# OCR funktioniert deutlich besser, wenn:
#
# - Text groß genug ist
# - Hintergrund gleichmäßig ist
# - guter Kontrast vorhanden ist
# - Bildrauschen reduziert wird
#
# Deshalb:
#
# 1. EXIF-Drehung korrigieren
# 2. Graustufen
# 3. Bild ggf. vergrößern
# 4. lokalen Kontrast verbessern
# 5. leichte Rauschreduzierung
# 6. adaptive Schwarz/Weiß-Umwandlung
#
# ============================================================

def preprocess_image(
    image_path,
    mode
):

    # --------------------------------------------------------
    # Bild mit Pillow laden
    # --------------------------------------------------------

    pil_image = Image.open(
        image_path
    )


    pil_image = ImageOps.exif_transpose(
        pil_image
    )


    pil_image = pil_image.convert(
        "RGB"
    )


    # --------------------------------------------------------
    # Original verwenden
    # --------------------------------------------------------

    if mode == "Original":

        return pil_image


    # --------------------------------------------------------
    # In OpenCV umwandeln
    # --------------------------------------------------------

    image = np.array(
        pil_image
    )


    # RGB -> Grau
    gray = cv2.cvtColor(

        image,

        cv2.COLOR_RGB2GRAY

    )


    # ========================================================
    # Bild vergrößern
    # ========================================================

    height, width = gray.shape


    largest_side = max(
        width,
        height
    )


    # Kleine Bilder stärker vergrößern
    if largest_side < 1500:

        scale = 2.0


    elif largest_side < 2500:

        scale = 1.5


    else:

        scale = 1.0


    if scale != 1.0:

        gray = cv2.resize(

            gray,

            None,

            fx=scale,

            fy=scale,

            interpolation=cv2.INTER_CUBIC

        )


    # ========================================================
    # Lokalen Kontrast verbessern
    # ========================================================

    clahe = cv2.createCLAHE(

        clipLimit=2.0,

        tileGridSize=(8, 8)

    )


    gray = clahe.apply(
        gray
    )


    # ========================================================
    # Leichte Rauschreduzierung
    # ========================================================

    gray = cv2.fastNlMeansDenoising(

        gray,

        None,

        h=8,

        templateWindowSize=7,

        searchWindowSize=21

    )


    # ========================================================
    # Modus: Automatisch
    # ========================================================
    #
    # Adaptive Threshold funktioniert besonders gut bei
    # Papierfotos mit Schatten oder ungleichmäßiger Beleuchtung.
    # ========================================================

    if mode == "Automatisch":

        processed = cv2.adaptiveThreshold(

            gray,

            255,

            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,

            cv2.THRESH_BINARY,

            31,

            11

        )


    # ========================================================
    # Modus: Sanft
    # ========================================================
    #
    # Behält mehr Graustufen.
    # Gut bei sehr feinen persischen Schriftzeichen.
    # ========================================================

    elif mode == "Sanft":

        processed = gray


    # ========================================================
    # Modus: Stark
    # ========================================================

    else:

        _, processed = cv2.threshold(

            gray,

            0,

            255,

            cv2.THRESH_BINARY
            + cv2.THRESH_OTSU

        )


    # ========================================================
    # Weißer Rand
    # ========================================================
    #
    # Etwas Rand kann Tesseract bei der Seitenerkennung helfen.
    # ========================================================

    processed = cv2.copyMakeBorder(

        processed,

        20,
        20,
        20,
        20,

        cv2.BORDER_CONSTANT,

        value=255

    )


    return Image.fromarray(
        processed
    )


# ============================================================
# OCR starten
# ============================================================

def start_ocr():

    global ocr_running


    if ocr_running:

        return


    if not selected_images:

        messagebox.showwarning(

            "Keine Bilder",

            "Bitte zuerst mindestens ein Bild auswählen."

        )

        return


    if not check_tesseract():

        return


    ocr_running = True


    start_button.config(
        state="disabled"
    )


    progress_bar["maximum"] = len(
        selected_images
    )


    progress_bar["value"] = 0


    status_label.config(
        text="Texterkennung wird gestartet..."
    )


    threading.Thread(

        target=run_ocr,

        daemon=True

    ).start()


# ============================================================
# OCR durchführen
# ============================================================

def run_ocr():

    global ocr_results
    global ocr_running


    try:

        ocr_results = []


        language_name = language_box.get()


        language_code = LANGUAGES[
            language_name
        ]


        processing_mode = processing_box.get()


        # ----------------------------------------------------
        # Tesseract Konfiguration
        # ----------------------------------------------------
        #
        # OEM 3:
        # Standard OCR Engine
        #
        # PSM 3:
        # Automatische Seitensegmentierung.
        #
        # Für Dokumentseiten ist das ein guter Ausgangspunkt.
        # ----------------------------------------------------

        tesseract_config = (
            "--oem 3 --psm 3"
        )


        for index, image_path in enumerate(
            selected_images
        ):


            # ------------------------------------------------
            # Status aktualisieren
            # ------------------------------------------------

            window.after(

                0,

                update_ocr_status,

                index,

                image_path

            )


            # ------------------------------------------------
            # Bild verbessern
            # ------------------------------------------------

            processed_image = preprocess_image(

                image_path,

                processing_mode

            )


            # ------------------------------------------------
            # OCR
            # ------------------------------------------------

            text = pytesseract.image_to_string(

                processed_image,

                lang=language_code,

                config=tesseract_config,

                timeout=120

            )


            text = text.strip()


            ocr_results.append(

                {

                    "image":
                        image_path,

                    "text":
                        text

                }

            )


            window.after(

                0,

                update_progress,

                index + 1

            )


        window.after(

            0,

            ocr_finished

        )


    except RuntimeError as error:

        window.after(

            0,

            ocr_failed,

            "OCR-Zeitüberschreitung:\n\n"
            + str(error)

        )


    except Exception as error:

        window.after(

            0,

            ocr_failed,

            str(error)

        )


    finally:

        ocr_running = False


# ============================================================
# OCR Status
# ============================================================

def update_ocr_status(
    index,
    image_path
):

    status_label.config(

        text=(
            f"Verarbeite Bild "
            f"{index + 1} von {len(selected_images)}:\n"
            f"{Path(image_path).name}"
        )

    )


# ============================================================
# Fortschritt
# ============================================================

def update_progress(value):

    progress_bar["value"] = value


# ============================================================
# OCR fertig
# ============================================================

def ocr_finished():

    start_button.config(
        state="normal"
    )


    # Ergebnisfeld leeren
    result_text.delete(

        "1.0",

        tk.END

    )


    # ========================================================
    # Ergebnisse anzeigen
    # ========================================================

    for index, result in enumerate(

        ocr_results,

        start=1

    ):

        file_name = Path(
            result["image"]
        ).name


        # Bei mehreren Bildern einen Seitentitel anzeigen.
        if len(ocr_results) > 1:

            result_text.insert(

                tk.END,

                f"\n========== Seite {index}: "
                f"{file_name} ==========\n\n"

            )


        if result["text"]:

            result_text.insert(

                tk.END,

                result["text"]

            )


        else:

            result_text.insert(

                tk.END,

                "[Kein Text erkannt]"

            )


        result_text.insert(

            tk.END,

            "\n\n"

        )


    status_label.config(

        text=(
            f"Fertig. {len(ocr_results)} "
            f"Bild(er) verarbeitet."
        )

    )


    save_button.config(
        state="normal"
    )


    # ========================================================
    # Benutzer direkt fragen, ob gespeichert werden soll
    # ========================================================

    answer = messagebox.askyesno(

        "OCR abgeschlossen",

        "Die Texterkennung ist abgeschlossen.\n\n"
        "Möchtest du das Ergebnis jetzt speichern?"

    )


    if answer:

        show_export_dialog()


# ============================================================
# OCR Fehler
# ============================================================

def ocr_failed(error):

    start_button.config(
        state="normal"
    )


    status_label.config(
        text="OCR fehlgeschlagen."
    )


    messagebox.showerror(

        "OCR Fehler",

        f"Der Text konnte nicht erkannt werden:\n\n"
        f"{error}"

    )


# ============================================================
# Aktuell bearbeiteten Text holen
# ============================================================
#
# Wichtig:
#
# Der Benutzer kann das OCR-Ergebnis im Textfeld korrigieren.
# Beim Export verwenden wir deshalb den Text aus dem Textfeld,
# nicht einfach das unveränderte OCR-Ergebnis.
# ============================================================

def get_edited_text():

    return result_text.get(

        "1.0",

        tk.END

    ).strip()


# ============================================================
# Speicherdialog
# ============================================================

def show_export_dialog():

    if not get_edited_text():

        messagebox.showwarning(

            "Kein Text",

            "Es ist kein Text zum Speichern vorhanden."

        )

        return


    dialog = tk.Toplevel(
        window
    )


    dialog.title(
        "Ergebnis speichern"
    )


    dialog.geometry(
        "430x390"
    )


    dialog.resizable(
        False,
        False
    )


    # Fenster über Hauptfenster anzeigen
    dialog.transient(
        window
    )


    dialog.grab_set()


    # ========================================================
    # Titel
    # ========================================================

    tk.Label(

        dialog,

        text="Exportformat auswählen",

        font=(
            "Segoe UI",
            16,
            "bold"
        )

    ).pack(
        pady=(25, 5)
    )


    tk.Label(

        dialog,

        text=(
            "Du kannst ein oder mehrere Formate "
            "gleichzeitig auswählen."
        ),

        wraplength=380

    ).pack(
        pady=(0, 20)
    )


    # ========================================================
    # Checkboxen
    # ========================================================

    txt_var = tk.BooleanVar(
        value=True
    )


    word_var = tk.BooleanVar(
        value=False
    )


    ppt_var = tk.BooleanVar(
        value=False
    )


    tk.Checkbutton(

        dialog,

        text="Textdatei (.txt)",

        variable=txt_var,

        font=(
            "Segoe UI",
            11
        )

    ).pack(
        anchor="w",
        padx=80,
        pady=7
    )


    tk.Checkbutton(

        dialog,

        text="Word-Datei (.docx)",

        variable=word_var,

        font=(
            "Segoe UI",
            11
        )

    ).pack(
        anchor="w",
        padx=80,
        pady=7
    )


    tk.Checkbutton(

        dialog,

        text="PowerPoint (.pptx)",

        variable=ppt_var,

        font=(
            "Segoe UI",
            11
        )

    ).pack(
        anchor="w",
        padx=80,
        pady=7
    )


    # ========================================================
    # Speichern
    # ========================================================

    def save_selected():

        formats = []


        if txt_var.get():

            formats.append(
                "txt"
            )


        if word_var.get():

            formats.append(
                "docx"
            )


        if ppt_var.get():

            formats.append(
                "pptx"
            )


        if not formats:

            messagebox.showwarning(

                "Kein Format",

                "Bitte mindestens ein Format auswählen.",

                parent=dialog

            )

            return


        dialog.destroy()


        export_results(
            formats
        )


    # ========================================================
    # Buttons
    # ========================================================

    button_frame = tk.Frame(
        dialog
    )


    button_frame.pack(
        pady=25
    )


    tk.Button(

        button_frame,

        text="Speichern",

        command=save_selected,

        width=15,

        height=2

    ).grid(

        row=0,
        column=0,
        padx=7

    )


    tk.Button(

        button_frame,

        text="Abbrechen",

        command=dialog.destroy,

        width=15,

        height=2

    ).grid(

        row=0,
        column=1,
        padx=7

    )


# ============================================================
# Ergebnisse exportieren
# ============================================================

def export_results(formats):

    # --------------------------------------------------------
    # Zielordner auswählen
    # --------------------------------------------------------

    output_folder = filedialog.askdirectory(

        title="Speicherordner auswählen"

    )


    if not output_folder:

        return


    # --------------------------------------------------------
    # Basis-Dateiname
    # --------------------------------------------------------

    base_name = simpledialog.askstring(

        "Dateiname",

        "Wie sollen die Dateien heißen?",

        initialvalue="OCR_Ergebnis"

    )


    if not base_name:

        return


    # Ungültige Windows-Zeichen ersetzen.
    invalid_chars = (
        '<>:"/\\|?*'
    )


    for character in invalid_chars:

        base_name = base_name.replace(

            character,

            "_"

        )


    output_folder = Path(
        output_folder
    )


    saved_files = []


    try:

        # ====================================================
        # TXT
        # ====================================================

        if "txt" in formats:

            txt_path = (

                output_folder

                / f"{base_name}.txt"

            )


            save_as_txt(
                txt_path
            )


            saved_files.append(
                txt_path.name
            )


        # ====================================================
        # WORD
        # ====================================================

        if "docx" in formats:

            word_path = (

                output_folder

                / f"{base_name}.docx"

            )


            save_as_word(
                word_path
            )


            saved_files.append(
                word_path.name
            )


        # ====================================================
        # POWERPOINT
        # ====================================================

        if "pptx" in formats:

            ppt_path = (

                output_folder

                / f"{base_name}.pptx"

            )


            save_as_powerpoint(
                ppt_path
            )


            saved_files.append(
                ppt_path.name
            )


        messagebox.showinfo(

            "Gespeichert",

            "Folgende Dateien wurden erstellt:\n\n"
            + "\n".join(saved_files)

        )


        status_label.config(

            text="Export erfolgreich."

        )


    except Exception as error:

        messagebox.showerror(

            "Export Fehler",

            f"Die Dateien konnten nicht gespeichert werden:\n\n"
            f"{error}"

        )


# ============================================================
# TXT Export
# ============================================================

def save_as_txt(file_path):

    text = get_edited_text()


    with open(

        file_path,

        "w",

        encoding="utf-8"

    ) as file:

        file.write(
            text
        )


# ============================================================
# Prüfen, ob Persisch verwendet wird
# ============================================================

def is_persian_mode():

    return "fas" in LANGUAGES[
        language_box.get()
    ]


# ============================================================
# Word Absatz RTL einstellen
# ============================================================

def set_word_rtl(paragraph):

    paragraph.alignment = (
        WD_ALIGN_PARAGRAPH.RIGHT
    )


    paragraph_format = (
        paragraph._p.get_or_add_pPr()
    )


    bidi = OxmlElement(
        "w:bidi"
    )


    paragraph_format.append(
        bidi
    )


# ============================================================
# Word Export
# ============================================================

def save_as_word(file_path):

    document = Document()


    # --------------------------------------------------------
    # Titel
    # --------------------------------------------------------

    title = document.add_heading(

        "OCR Ergebnis",

        level=0

    )


    if is_persian_mode():

        set_word_rtl(
            title
        )


    # ========================================================
    # Falls wir einzelne OCR-Ergebnisse haben
    # ========================================================

    if ocr_results:

        for index, result in enumerate(

            ocr_results,

            start=1

        ):

            file_name = Path(
                result["image"]
            ).name


            heading = document.add_heading(

                f"Seite {index} – {file_name}",

                level=1

            )


            if is_persian_mode():

                set_word_rtl(
                    heading
                )


            # ------------------------------------------------
            # Text in einzelne Absätze aufteilen
            # ------------------------------------------------

            for text_line in result["text"].splitlines():

                paragraph = document.add_paragraph()


                if is_persian_mode():

                    set_word_rtl(
                        paragraph
                    )


                run = paragraph.add_run(
                    text_line
                )


                run.font.name = "Arial"

                run.font.size = Pt(
                    12
                )


    # ========================================================
    # Falls Benutzer Text manuell verändert hat:
    #
    # Ganz unten die bearbeitete Gesamtfassung hinzufügen.
    # ========================================================

    document.add_page_break()


    edited_heading = document.add_heading(

        "Bearbeitete Gesamtfassung",

        level=1

    )


    if is_persian_mode():

        set_word_rtl(
            edited_heading
        )


    for text_line in get_edited_text().splitlines():

        paragraph = document.add_paragraph()


        if is_persian_mode():

            set_word_rtl(
                paragraph
            )


        run = paragraph.add_run(
            text_line
        )


        run.font.name = "Arial"

        run.font.size = Pt(
            12
        )


    document.save(
        file_path
    )


# ============================================================
# Text in Stücke teilen
# ============================================================
#
# PowerPoint kann keine beliebig langen Texte schön auf
# einer einzigen Folie darstellen.
#
# Deshalb erstellen wir bei langem Text mehrere Folien.
# ============================================================

def split_text_for_slides(
    text,
    max_characters=1200
):

    paragraphs = text.splitlines()


    chunks = []

    current = ""


    for paragraph in paragraphs:

        paragraph = paragraph.strip()


        if not paragraph:

            continue


        proposed = (

            current
            + "\n"
            + paragraph

        ).strip()


        if len(proposed) > max_characters:

            if current:

                chunks.append(
                    current.strip()
                )


            current = paragraph


        else:

            current = proposed


    if current:

        chunks.append(
            current.strip()
        )


    if not chunks:

        chunks.append(
            "[Kein Text erkannt]"
        )


    return chunks


# ============================================================
# PowerPoint Export
# ============================================================

def save_as_powerpoint(file_path):

    presentation = Presentation()


    # Breitbildformat 16:9
    presentation.slide_width = Inches(
        13.333
    )


    presentation.slide_height = Inches(
        7.5
    )


    # ========================================================
    # Titelfolie
    # ========================================================

    title_slide = presentation.slides.add_slide(

        presentation.slide_layouts[0]

    )


    title_slide.shapes.title.text = (
        "OCR Ergebnis"
    )


    title_slide.placeholders[1].text = (

        f"{len(selected_images)} Bild(er) verarbeitet"

    )


    # ========================================================
    # Eine oder mehrere Folien pro Bild
    # ========================================================

    for index, result in enumerate(

        ocr_results,

        start=1

    ):

        file_name = Path(
            result["image"]
        ).name


        chunks = split_text_for_slides(

            result["text"]

        )


        for chunk_index, chunk in enumerate(

            chunks,

            start=1

        ):

            slide = presentation.slides.add_slide(

                presentation.slide_layouts[5]

            )


            # ------------------------------------------------
            # Titel
            # ------------------------------------------------

            title = slide.shapes.title


            if len(chunks) == 1:

                title.text = (
                    f"Seite {index} – {file_name}"
                )

            else:

                title.text = (

                    f"Seite {index} – "
                    f"{file_name} "
                    f"({chunk_index}/{len(chunks)})"

                )


            # ------------------------------------------------
            # Textbox
            # ------------------------------------------------

            text_box = slide.shapes.add_textbox(

                Inches(0.7),

                Inches(1.5),

                Inches(11.9),

                Inches(5.3)

            )


            text_frame = text_box.text_frame


            text_frame.word_wrap = True


            text_frame.clear()


            paragraph = text_frame.paragraphs[0]


            paragraph.text = chunk


            if is_persian_mode():

                paragraph.alignment = (
                    PP_ALIGN.RIGHT
                )


            else:

                paragraph.alignment = (
                    PP_ALIGN.LEFT
                )


            for run in paragraph.runs:

                run.font.name = "Arial"

                run.font.size = PPTPt(
                    18
                )


    presentation.save(
        file_path
    )


# ============================================================
# Ergebnis löschen
# ============================================================

def clear_result():

    answer = messagebox.askyesno(

        "Text löschen",

        "Den erkannten Text wirklich löschen?"

    )


    if not answer:

        return


    result_text.delete(

        "1.0",

        tk.END

    )


    save_button.config(
        state="disabled"
    )


# ============================================================
# HAUPTFENSTER
# ============================================================

window = tk.Tk()


window.title(
    "Image Text Extractor"
)


window.geometry(
    "1100x780"
)


window.minsize(
    950,
    700
)


# ============================================================
# Titel
# ============================================================

title_label = tk.Label(

    window,

    text="Image Text Extractor",

    font=(
        "Segoe UI",
        20,
        "bold"
    )

)


title_label.pack(
    pady=(15, 3)
)


description_label = tk.Label(

    window,

    text=(
        "Text aus Bildern erkennen – "
        "Persisch, Deutsch und Englisch"
    )

)


description_label.pack(
    pady=(0, 12)
)


# ============================================================
# Hauptbereich
# ============================================================

main_frame = tk.Frame(
    window
)


main_frame.pack(

    fill="both",

    expand=True,

    padx=15,

    pady=5

)


# ============================================================
# Linke Seite
# ============================================================

left_frame = tk.Frame(

    main_frame,

    width=420

)


left_frame.pack(

    side="left",

    fill="y",

    padx=(0, 10)

)


# ============================================================
# Bilder hinzufügen
# ============================================================

add_button = tk.Button(

    left_frame,

    text="Bilder auswählen",

    command=add_images,

    width=25,

    height=2

)


add_button.pack(
    pady=5
)


image_count_label = tk.Label(

    left_frame,

    text="0 Bilder"

)


image_count_label.pack(
    pady=3
)


# ============================================================
# Bilderliste
# ============================================================

list_frame = tk.Frame(
    left_frame
)


list_frame.pack(
    pady=5
)


image_listbox = tk.Listbox(

    list_frame,

    width=45,

    height=9,

    font=(
        "Segoe UI",
        9
    )

)


image_listbox.pack(

    side="left",

    fill="y"

)


image_scrollbar = tk.Scrollbar(

    list_frame,

    command=image_listbox.yview

)


image_scrollbar.pack(

    side="right",

    fill="y"

)


image_listbox.config(

    yscrollcommand=image_scrollbar.set

)


image_listbox.bind(

    "<<ListboxSelect>>",

    image_selected

)


# ============================================================
# Bildlisten-Buttons
# ============================================================

image_buttons = tk.Frame(
    left_frame
)


image_buttons.pack(
    pady=5
)


tk.Button(

    image_buttons,

    text="↑",

    command=move_up,

    width=5

).grid(

    row=0,
    column=0,
    padx=3

)


tk.Button(

    image_buttons,

    text="↓",

    command=move_down,

    width=5

).grid(

    row=0,
    column=1,
    padx=3

)


tk.Button(

    image_buttons,

    text="Entfernen",

    command=remove_image,

    width=10

).grid(

    row=0,
    column=2,
    padx=3

)


tk.Button(

    image_buttons,

    text="Alles löschen",

    command=clear_images,

    width=12

).grid(

    row=0,
    column=3,
    padx=3

)


# ============================================================
# Vorschau
# ============================================================

preview_frame = tk.Frame(

    left_frame,

    width=390,

    height=300,

    relief="groove",

    borderwidth=2

)


preview_frame.pack(
    pady=10
)


preview_frame.pack_propagate(
    False
)


preview_label = tk.Label(

    preview_frame,

    text="Keine Vorschau"

)


preview_label.pack(

    fill="both",

    expand=True

)


# ============================================================
# Sprache
# ============================================================

settings_frame = tk.LabelFrame(

    left_frame,

    text="OCR Einstellungen",

    padx=10,

    pady=10

)


settings_frame.pack(

    fill="x",

    pady=10

)


tk.Label(

    settings_frame,

    text="Sprache:"

).grid(

    row=0,
    column=0,

    sticky="w",

    padx=5,
    pady=5

)


language_box = ttk.Combobox(

    settings_frame,

    values=list(
        LANGUAGES.keys()
    ),

    state="readonly",

    width=28

)


language_box.grid(

    row=0,
    column=1,

    padx=5,
    pady=5

)


# Schwerpunkt Persisch
language_box.set(
    "Persisch / Farsi"
)


# ============================================================
# Bildverbesserung
# ============================================================

tk.Label(

    settings_frame,

    text="Bildverbesserung:"

).grid(

    row=1,
    column=0,

    sticky="w",

    padx=5,
    pady=5

)


processing_box = ttk.Combobox(

    settings_frame,

    values=[

        "Automatisch",

        "Sanft",

        "Stark",

        "Original"

    ],

    state="readonly",

    width=28

)


processing_box.grid(

    row=1,
    column=1,

    padx=5,
    pady=5

)


processing_box.set(
    "Automatisch"
)


# ============================================================
# OCR Start
# ============================================================

start_button = tk.Button(

    left_frame,

    text="Text erkennen",

    command=start_ocr,

    width=25,

    height=2

)


start_button.pack(
    pady=10
)


progress_bar = ttk.Progressbar(

    left_frame,

    length=350,

    mode="determinate"

)


progress_bar.pack(
    pady=5
)


# ============================================================
# Rechte Seite
# ============================================================

right_frame = tk.Frame(
    main_frame
)


right_frame.pack(

    side="right",

    fill="both",

    expand=True

)


result_title = tk.Label(

    right_frame,

    text="Erkannter Text",

    font=(
        "Segoe UI",
        12,
        "bold"
    )

)


result_title.pack(
    pady=(5, 5)
)


# ============================================================
# Textbox
# ============================================================

text_frame = tk.Frame(
    right_frame
)


text_frame.pack(

    fill="both",

    expand=True

)


result_text = tk.Text(

    text_frame,

    wrap="word",

    font=(
        "Arial",
        12
    ),

    undo=True

)


result_text.pack(

    side="left",

    fill="both",

    expand=True

)


text_scrollbar = tk.Scrollbar(

    text_frame,

    command=result_text.yview

)


text_scrollbar.pack(

    side="right",

    fill="y"

)


result_text.config(

    yscrollcommand=text_scrollbar.set

)


# ============================================================
# Ergebnis Buttons
# ============================================================

result_buttons = tk.Frame(
    right_frame
)


result_buttons.pack(
    pady=10
)


save_button = tk.Button(

    result_buttons,

    text="Ergebnis speichern",

    command=show_export_dialog,

    width=20,

    height=2,

    state="disabled"

)


save_button.grid(

    row=0,
    column=0,

    padx=5

)


clear_result_button = tk.Button(

    result_buttons,

    text="Text löschen",

    command=clear_result,

    width=15,

    height=2

)


clear_result_button.grid(

    row=0,
    column=1,

    padx=5

)


# ============================================================
# Status
# ============================================================

status_label = tk.Label(

    window,

    text="Bilder auswählen, um zu beginnen.",

    wraplength=1000

)


status_label.pack(
    pady=(5, 15)
)


# ============================================================
# Programm starten
# ============================================================

window.mainloop()