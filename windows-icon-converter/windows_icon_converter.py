# ============================================================
# Windows Icon Converter
# ============================================================
#
# Was macht dieses Programm?
#
# Dieses Programm wandelt normale Bilder in eine richtige
# Windows ICO-Datei um.
#
# Geeignet für:
# - Windows 10
# - Windows 11
# - Ordner-Symbole im Windows Explorer
# - Verknüpfungen
# - Programme
#
# Unterstützte Eingabeformate:
# - PNG
# - JPG / JPEG
# - WebP
# - BMP
# - TIFF
#
# Die ICO-Datei enthält mehrere Größen:
#
# 16x16
# 24x24
# 32x32
# 48x48
# 64x64
# 128x128
# 256x256
#
# Dadurch kann Windows automatisch die passende Größe
# auswählen.
#
# Benötigte Bibliothek:
#
# py -m pip install pillow
#
# Start:
#
# py windows-icon-converter\windows_icon_converter.py
# ============================================================


import tkinter as tk

from tkinter import filedialog, messagebox

from pathlib import Path

# Pillow bearbeitet und speichert Bilder.
from PIL import Image, ImageTk


# ============================================================
# Variablen
# ============================================================

selected_image_path = None

original_image = None

prepared_icon = None


# ============================================================
# ICO-Größen
# ============================================================

ICON_SIZES = [

    (16, 16),

    (24, 24),

    (32, 32),

    (48, 48),

    (64, 64),

    (128, 128),

    (256, 256)

]


# ============================================================
# Bild auswählen
# ============================================================

def choose_image():

    global selected_image_path
    global original_image
    global prepared_icon


    file_path = filedialog.askopenfilename(

        title="Bild auswählen",

        filetypes=[

            (
                "Bilddateien",
                "*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff"
            ),

            (
                "PNG",
                "*.png"
            ),

            (
                "JPEG",
                "*.jpg *.jpeg"
            ),

            (
                "WebP",
                "*.webp"
            ),

            (
                "Alle Dateien",
                "*.*"
            )

        ]

    )


    if not file_path:
        return


    try:

        selected_image_path = file_path


        # Bild laden und als RGBA öffnen.
        #
        # RGBA unterstützt Transparenz.
        original_image = Image.open(
            file_path
        ).convert(
            "RGBA"
        )


        # Icon vorbereiten.
        prepared_icon = prepare_icon_image(
            original_image
        )


        # Vorschau anzeigen.
        show_preview(
            prepared_icon
        )


        file_name_label.config(

            text=Path(file_path).name

        )


        save_button.config(
            state="normal"
        )


        status_label.config(

            text="Bild geladen. Das Icon kann gespeichert werden."

        )


    except Exception as error:

        messagebox.showerror(

            "Fehler",

            f"Das Bild konnte nicht geöffnet werden:\n\n{error}"

        )


# ============================================================
# Bild für Windows Icon vorbereiten
# ============================================================
#
# Windows Icons sollten quadratisch sein.
#
# Wenn das Original zum Beispiel 1920x1080 groß ist,
# verzerren wir es NICHT.
#
# Stattdessen:
#
# 1. Bild proportional verkleinern
# 2. Transparenten quadratischen Hintergrund erstellen
# 3. Bild mittig einsetzen
#
# ============================================================

def prepare_icon_image(image):

    # Wir benutzen 256x256 als größte Icon-Version.
    canvas_size = 256


    # Kopie erstellen, damit das Original nicht verändert wird.
    image_copy = image.copy()


    # Etwas Abstand zum Rand lassen.
    #
    # Dadurch sieht das Symbol in Windows oft besser aus.
    max_image_size = 230


    # Bild proportional verkleinern.
    image_copy.thumbnail(

        (
            max_image_size,
            max_image_size
        ),

        Image.Resampling.LANCZOS

    )


    # Transparenten 256x256 Hintergrund erstellen.
    icon_canvas = Image.new(

        "RGBA",

        (
            canvas_size,
            canvas_size
        ),

        (
            0,
            0,
            0,
            0
        )

    )


    # Position berechnen, damit das Bild genau mittig sitzt.
    x = (
        canvas_size
        - image_copy.width
    ) // 2


    y = (
        canvas_size
        - image_copy.height
    ) // 2


    # Bild auf den transparenten Hintergrund setzen.
    icon_canvas.alpha_composite(

        image_copy,

        (
            x,
            y
        )

    )


    return icon_canvas


# ============================================================
# Vorschau anzeigen
# ============================================================

def show_preview(image):

    preview = image.copy()


    preview.thumbnail(

        (
            256,
            256
        ),

        Image.Resampling.LANCZOS

    )


    photo = ImageTk.PhotoImage(
        preview
    )


    preview_label.config(

        image=photo,

        text=""

    )


    # Referenz behalten.
    #
    # Sonst kann tkinter das Bild aus dem Speicher entfernen.
    preview_label.image = photo


# ============================================================
# Icon speichern
# ============================================================

def save_icon():

    if prepared_icon is None:

        messagebox.showwarning(

            "Kein Bild",

            "Bitte zuerst ein Bild auswählen."

        )

        return


    # Namen des Originals übernehmen.
    #
    # Beispiel:
    #
    # folder-logo.png
    #
    # wird vorgeschlagen als:
    #
    # folder-logo.ico

    original_name = Path(
        selected_image_path
    ).stem


    save_path = filedialog.asksaveasfilename(

        title="Windows Icon speichern",

        initialfile=f"{original_name}.ico",

        defaultextension=".ico",

        filetypes=[

            (
                "Windows Icon",
                "*.ico"
            )

        ]

    )


    if not save_path:
        return


    try:

        # ====================================================
        # Als echtes Windows ICO speichern
        # ====================================================
        #
        # Pillow speichert mehrere Icon-Größen innerhalb
        # derselben ICO-Datei.
        #
        # Windows kann dann selbst entscheiden, welche
        # Auflösung gerade benötigt wird.
        # ====================================================

        prepared_icon.save(

            save_path,

            format="ICO",

            sizes=ICON_SIZES

        )


        status_label.config(

            text="Windows Icon erfolgreich erstellt."

        )


        messagebox.showinfo(

            "Fertig",

            "Das Windows Icon wurde erfolgreich erstellt!\n\n"
            "Du kannst die ICO-Datei jetzt als Ordner-Symbol "
            "in Windows verwenden."

        )


    except Exception as error:

        messagebox.showerror(

            "Fehler",

            f"Das Icon konnte nicht gespeichert werden:\n\n{error}"

        )


# ============================================================
# Hauptfenster
# ============================================================

window = tk.Tk()


window.title(
    "Windows Icon Converter"
)


window.geometry(
    "600x600"
)


window.minsize(
    560,
    560
)


# ============================================================
# Titel
# ============================================================

title_label = tk.Label(

    window,

    text="Windows Icon Converter",

    font=(

        "Segoe UI",

        20,

        "bold"

    )

)


title_label.pack(

    pady=(25, 5)

)


# ============================================================
# Beschreibung
# ============================================================

description_label = tk.Label(

    window,

    text=(

        "PNG, JPG, WebP, BMP oder TIFF in ein\n"
        "Windows 10 / Windows 11 ICO-Symbol umwandeln."

    ),

    justify="center"

)


description_label.pack(

    pady=(0, 20)

)


# ============================================================
# Bild auswählen
# ============================================================

choose_button = tk.Button(

    window,

    text="Bild auswählen",

    command=choose_image,

    width=22,

    height=2

)


choose_button.pack(

    pady=5

)


# ============================================================
# Dateiname
# ============================================================

file_name_label = tk.Label(

    window,

    text="Kein Bild ausgewählt",

    wraplength=500

)


file_name_label.pack(

    pady=10

)


# ============================================================
# Vorschau
# ============================================================

preview_frame = tk.Frame(

    window,

    width=280,

    height=280,

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

    text="Vorschau",

    font=(

        "Segoe UI",

        12

    )

)


preview_label.pack(

    fill="both",

    expand=True

)


# ============================================================
# Icon speichern
# ============================================================

save_button = tk.Button(

    window,

    text="ICO speichern",

    command=save_icon,

    width=22,

    height=2,

    state="disabled"

)


save_button.pack(

    pady=15

)


# ============================================================
# Information
# ============================================================

info_label = tk.Label(

    window,

    text=(

        "Erstellt automatisch mehrere Größen:\n"
        "16, 24, 32, 48, 64, 128 und 256 Pixel"

    ),

    justify="center"

)


info_label.pack(

    pady=5

)


# ============================================================
# Status
# ============================================================

status_label = tk.Label(

    window,

    text="Bitte ein Bild auswählen."

)


status_label.pack(

    pady=(10, 20)

)


# ============================================================
# Fenster offen halten
# ============================================================

window.mainloop()