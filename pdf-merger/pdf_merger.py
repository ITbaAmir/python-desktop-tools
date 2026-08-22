# ============================================================
# PDF Merger
# ============================================================
#
# Was macht dieses Programm?
#
# Dieses Programm führt mehrere PDF-Dateien zu einer einzigen
# PDF-Datei zusammen.
#
# Du kannst:
# - Mehrere PDFs einzeln auswählen
# - Einen ganzen Ordner mit PDFs auswählen
# - Die Reihenfolge verändern
# - Einzelne PDFs entfernen
# - Alle PDFs zu einer Datei zusammenführen
#
# Benötigte Bibliothek:
#
# py -m pip install pypdf
#
# Diese Bibliothek muss nur einmal installiert werden.
#
# Start:
#
# py pdf-merger\pdf_merger.py
# ============================================================


import tkinter as tk
from tkinter import filedialog, messagebox

from pathlib import Path

# pypdf führt die PDF-Dateien zusammen
from pypdf import PdfReader, PdfWriter


# ============================================================
# Liste der ausgewählten PDF-Dateien
# ============================================================

selected_pdfs = []


# ============================================================
# Liste aktualisieren
# ============================================================

def refresh_list():

    pdf_listbox.delete(
        0,
        tk.END
    )

    for index, pdf_path in enumerate(
        selected_pdfs,
        start=1
    ):

        file_name = Path(
            pdf_path
        ).name

        pdf_listbox.insert(
            tk.END,
            f"{index}. {file_name}"
        )

    count_label.config(
        text=f"{len(selected_pdfs)} PDF-Datei(en) ausgewählt"
    )


# ============================================================
# Mehrere PDFs auswählen
# ============================================================

def add_pdfs():

    files = filedialog.askopenfilenames(

        title="PDF-Dateien auswählen",

        filetypes=[
            ("PDF Files", "*.pdf")
        ]

    )

    if not files:
        return

    for file_path in files:

        # Gleiche Datei nicht doppelt hinzufügen
        if file_path not in selected_pdfs:

            selected_pdfs.append(
                file_path
            )

    refresh_list()

    status_label.config(
        text="PDF-Dateien hinzugefügt."
    )


# ============================================================
# Ordner mit PDFs auswählen
# ============================================================

def add_folder():

    folder = filedialog.askdirectory(
        title="Ordner mit PDF-Dateien auswählen"
    )

    if not folder:
        return

    folder_path = Path(
        folder
    )

    # Alle PDFs direkt in diesem Ordner suchen
    #
    # Die Unterordner werden absichtlich nicht durchsucht.
    pdf_files = sorted(

        folder_path.glob("*.pdf"),

        key=lambda path: path.name.lower()

    )

    if not pdf_files:

        messagebox.showwarning(

            "Keine PDFs",

            "In diesem Ordner wurden keine PDF-Dateien gefunden."

        )

        return

    added = 0

    for pdf_path in pdf_files:

        file_path = str(
            pdf_path
        )

        if file_path not in selected_pdfs:

            selected_pdfs.append(
                file_path
            )

            added += 1

    refresh_list()

    status_label.config(

        text=f"{added} PDF-Datei(en) aus dem Ordner hinzugefügt."

    )


# ============================================================
# Ausgewählte PDF entfernen
# ============================================================

def remove_pdf():

    selection = pdf_listbox.curselection()

    if not selection:

        messagebox.showwarning(

            "Keine Auswahl",

            "Bitte zuerst eine PDF aus der Liste auswählen."

        )

        return

    index = selection[0]

    selected_pdfs.pop(
        index
    )

    refresh_list()

    status_label.config(
        text="PDF entfernt."
    )


# ============================================================
# PDF nach oben verschieben
# ============================================================

def move_up():

    selection = pdf_listbox.curselection()

    if not selection:
        return

    index = selection[0]

    # Erste Datei kann nicht weiter nach oben
    if index == 0:
        return

    selected_pdfs[index - 1], selected_pdfs[index] = (

        selected_pdfs[index],
        selected_pdfs[index - 1]

    )

    refresh_list()

    pdf_listbox.selection_set(
        index - 1
    )


# ============================================================
# PDF nach unten verschieben
# ============================================================

def move_down():

    selection = pdf_listbox.curselection()

    if not selection:
        return

    index = selection[0]

    # Letzte Datei kann nicht weiter nach unten
    if index >= len(selected_pdfs) - 1:
        return

    selected_pdfs[index + 1], selected_pdfs[index] = (

        selected_pdfs[index],
        selected_pdfs[index + 1]

    )

    refresh_list()

    pdf_listbox.selection_set(
        index + 1
    )


# ============================================================
# Ganze Liste löschen
# ============================================================

def clear_list():

    if not selected_pdfs:
        return

    answer = messagebox.askyesno(

        "Liste löschen",

        "Alle ausgewählten PDF-Dateien aus der Liste entfernen?"

    )

    if not answer:
        return

    selected_pdfs.clear()

    refresh_list()

    status_label.config(
        text="Liste geleert."
    )


# ============================================================
# PDFs zusammenführen
# ============================================================

def merge_pdfs():

    # Mindestens zwei PDFs sind sinnvoll
    if len(selected_pdfs) < 2:

        messagebox.showwarning(

            "Zu wenige PDFs",

            "Bitte mindestens zwei PDF-Dateien auswählen."

        )

        return

    save_path = filedialog.asksaveasfilename(

        title="Zusammengeführte PDF speichern",

        defaultextension=".pdf",

        initialfile="merged.pdf",

        filetypes=[
            ("PDF Files", "*.pdf")
        ]

    )

    if not save_path:
        return

    try:

        status_label.config(
            text="PDF-Dateien werden zusammengeführt..."
        )

        window.update_idletasks()

        # Neue PDF erstellen
        writer = PdfWriter()

        # ====================================================
        # Jede PDF lesen
        # ====================================================

        for pdf_path in selected_pdfs:

            reader = PdfReader(
                pdf_path
            )

            # ------------------------------------------------
            # Falls die PDF passwortgeschützt ist
            # ------------------------------------------------

            if reader.is_encrypted:

                messagebox.showerror(

                    "Passwortgeschützte PDF",

                    f"Diese PDF ist passwortgeschützt:\n\n"
                    f"{Path(pdf_path).name}\n\n"
                    "Bitte zuerst entsperren oder eine andere Datei wählen."

                )

                status_label.config(
                    text="Zusammenführen abgebrochen."
                )

                return

            # ------------------------------------------------
            # Alle Seiten kopieren
            # ------------------------------------------------

            for page in reader.pages:

                writer.add_page(
                    page
                )

        # ====================================================
        # Fertige PDF speichern
        # ====================================================

        with open(
            save_path,
            "wb"
        ) as output_file:

            writer.write(
                output_file
            )

        status_label.config(
            text="PDF erfolgreich erstellt."
        )

        messagebox.showinfo(

            "Fertig",

            "Alle PDF-Dateien wurden erfolgreich zusammengeführt!"

        )

    except Exception as error:

        status_label.config(
            text="Fehler beim Zusammenführen."
        )

        messagebox.showerror(

            "Fehler",

            f"Die PDF-Dateien konnten nicht zusammengeführt werden:\n\n"
            f"{error}"

        )


# ============================================================
# Hauptfenster
# ============================================================

window = tk.Tk()


window.title(
    "PDF Merger"
)


window.geometry(
    "720x620"
)


window.minsize(
    650,
    560
)


# ============================================================
# Titel
# ============================================================

title_label = tk.Label(

    window,

    text="PDF Merger",

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

    text=(
        "Mehrere PDF-Dateien auswählen und "
        "zu einer PDF zusammenführen."
    )

)


description_label.pack(
    pady=(0, 20)
)


# ============================================================
# Dateien hinzufügen
# ============================================================

add_frame = tk.Frame(
    window
)


add_frame.pack(
    pady=5
)


add_pdfs_button = tk.Button(

    add_frame,

    text="PDFs auswählen",

    command=add_pdfs,

    width=20,

    height=2

)


add_pdfs_button.grid(

    row=0,
    column=0,

    padx=10

)


add_folder_button = tk.Button(

    add_frame,

    text="Ordner auswählen",

    command=add_folder,

    width=20,

    height=2

)


add_folder_button.grid(

    row=0,
    column=1,

    padx=10

)


# ============================================================
# Anzahl
# ============================================================

count_label = tk.Label(

    window,

    text="0 PDF-Datei(en) ausgewählt"

)


count_label.pack(
    pady=10
)


# ============================================================
# PDF-Liste
# ============================================================

list_frame = tk.Frame(
    window
)


list_frame.pack(
    padx=20,
    pady=5,
    fill="both",
    expand=True
)


pdf_listbox = tk.Listbox(

    list_frame,

    font=(
        "Segoe UI",
        10
    ),

    height=16

)


pdf_listbox.pack(

    side="left",

    fill="both",

    expand=True

)


scrollbar = tk.Scrollbar(

    list_frame,

    command=pdf_listbox.yview

)


scrollbar.pack(

    side="right",

    fill="y"

)


pdf_listbox.config(

    yscrollcommand=scrollbar.set

)


# ============================================================
# Reihenfolge und Entfernen
# ============================================================

control_frame = tk.Frame(
    window
)


control_frame.pack(
    pady=10
)


up_button = tk.Button(

    control_frame,

    text="Nach oben",

    command=move_up,

    width=13

)


up_button.grid(
    row=0,
    column=0,
    padx=5
)


down_button = tk.Button(

    control_frame,

    text="Nach unten",

    command=move_down,

    width=13

)


down_button.grid(
    row=0,
    column=1,
    padx=5
)


remove_button = tk.Button(

    control_frame,

    text="Entfernen",

    command=remove_pdf,

    width=13

)


remove_button.grid(
    row=0,
    column=2,
    padx=5
)


clear_button = tk.Button(

    control_frame,

    text="Alles löschen",

    command=clear_list,

    width=13

)


clear_button.grid(
    row=0,
    column=3,
    padx=5
)


# ============================================================
# Zusammenführen
# ============================================================

merge_button = tk.Button(

    window,

    text="PDFs zusammenführen",

    command=merge_pdfs,

    width=25,

    height=2

)


merge_button.pack(
    pady=15
)


# ============================================================
# Status
# ============================================================

status_label = tk.Label(

    window,

    text="PDF-Dateien auswählen oder einen Ordner öffnen."

)


status_label.pack(
    pady=(0, 20)
)


# ============================================================
# Fenster offen halten
# ============================================================

window.mainloop()
