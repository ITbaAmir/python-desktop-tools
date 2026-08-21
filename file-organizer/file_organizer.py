# ============================================================
# File Organizer
# ============================================================
#
# What this program does:
# This program organizes files inside a selected folder.
#
# It automatically creates folders such as:
#
# - Images
# - Videos
# - Audio
# - PDFs
# - Documents
# - Text Files
# - Spreadsheets
# - Presentations
# - Archives
# - Code
# - Applications
# - Fonts
# - eBooks
# - Databases
# - CAD and 3D
# - Disk Images
# - Torrents
# - Other
#
# Files are moved into the correct folder based on
# their file extension.
#
# Required libraries:
# None.
#
# Everything used here is included with Python.
#
# Run with:
#
# py file-organizer\file_organizer.py
#
# IMPORTANT:
# This program MOVES files.
# Test it first with a folder containing copies of files.
# ============================================================


import tkinter as tk

from tkinter import filedialog, messagebox

# os helps us work with files and folders
import os

# shutil moves files
import shutil

# pathlib makes file paths easier to work with
from pathlib import Path


# ============================================================
# File categories
# ============================================================
#
# Each category contains commonly used file extensions.
#
# Extensions are written in lowercase because the program
# converts file extensions to lowercase before checking them.
# ============================================================

FILE_TYPES = {

    # --------------------------------------------------------
    # Images
    # --------------------------------------------------------

    "Images": {

        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".webp",
        ".tiff",
        ".tif",
        ".svg",
        ".ico",
        ".heic",
        ".heif",
        ".raw",
        ".cr2",
        ".nef",
        ".arw",
        ".dng",
        ".avif",
        ".jfif"

    },


    # --------------------------------------------------------
    # Videos
    # --------------------------------------------------------

    "Videos": {

        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
        ".mpeg",
        ".mpg",
        ".3gp",
        ".ts",
        ".mts",
        ".m2ts",
        ".vob"

    },


    # --------------------------------------------------------
    # Audio
    # --------------------------------------------------------

    "Audio": {

        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".m4a",
        ".wma",
        ".opus",
        ".aiff",
        ".aif",
        ".mid",
        ".midi",
        ".amr"

    },


    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    "PDFs": {

        ".pdf"

    },


    # --------------------------------------------------------
    # Documents
    # --------------------------------------------------------

    "Documents": {

        ".doc",
        ".docx",
        ".odt",
        ".rtf",
        ".pages",
        ".wps",
        ".wpd"

    },


    # --------------------------------------------------------
    # Text files
    # --------------------------------------------------------

    "Text Files": {

        ".txt",
        ".md",
        ".log",
        ".nfo",
        ".tex"

    },


    # --------------------------------------------------------
    # Spreadsheets
    # --------------------------------------------------------

    "Spreadsheets": {

        ".xls",
        ".xlsx",
        ".xlsm",
        ".xlsb",
        ".csv",
        ".ods",
        ".numbers",
        ".tsv"

    },


    # --------------------------------------------------------
    # Presentations
    # --------------------------------------------------------

    "Presentations": {

        ".ppt",
        ".pptx",
        ".pptm",
        ".odp",
        ".key"

    },


    # --------------------------------------------------------
    # Archives / compressed files
    # --------------------------------------------------------

    "Archives": {

        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".bz2",
        ".xz",
        ".tgz",
        ".tbz",
        ".cab",
        ".z"

    },


    # --------------------------------------------------------
    # Programming / code files
    # --------------------------------------------------------

    "Code": {

        ".py",
        ".pyw",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".html",
        ".htm",
        ".css",
        ".scss",
        ".sass",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".cs",
        ".php",
        ".rb",
        ".go",
        ".rs",
        ".swift",
        ".kt",
        ".kts",
        ".dart",
        ".lua",
        ".pl",
        ".r",
        ".sql",
        ".sh",
        ".bat",
        ".cmd",
        ".ps1",
        ".vue",
        ".svelte",

        # Configuration / data files commonly used in projects
        ".json",
        ".xml",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg"

    },


    # --------------------------------------------------------
    # Applications and installers
    # --------------------------------------------------------

    "Applications": {

        ".exe",
        ".msi",
        ".msix",
        ".appx",
        ".apk",
        ".deb",
        ".rpm",
        ".dmg",
        ".pkg"

    },


    # --------------------------------------------------------
    # Fonts
    # --------------------------------------------------------

    "Fonts": {

        ".ttf",
        ".otf",
        ".woff",
        ".woff2",
        ".eot"

    },


    # --------------------------------------------------------
    # eBooks
    # --------------------------------------------------------

    "eBooks": {

        ".epub",
        ".mobi",
        ".azw",
        ".azw3",
        ".fb2",
        ".djvu"

    },


    # --------------------------------------------------------
    # Databases
    # --------------------------------------------------------

    "Databases": {

        ".db",
        ".sqlite",
        ".sqlite3",
        ".mdb",
        ".accdb",
        ".dbf"

    },


    # --------------------------------------------------------
    # CAD and 3D files
    # --------------------------------------------------------

    "CAD and 3D": {

        ".dwg",
        ".dxf",
        ".stl",
        ".obj",
        ".fbx",
        ".blend",
        ".3ds",
        ".step",
        ".stp",
        ".iges",
        ".igs",
        ".skp"

    },


    # --------------------------------------------------------
    # Disk images
    # --------------------------------------------------------

    "Disk Images": {

        ".iso",
        ".img",
        ".vhd",
        ".vhdx",
        ".vmdk"

    },


    # --------------------------------------------------------
    # Torrent files
    # --------------------------------------------------------

    "Torrents": {

        ".torrent"

    }

}


# ============================================================
# Selected folder
# ============================================================

selected_folder = ""


# ============================================================
# Choose folder
# ============================================================

def choose_folder():

    global selected_folder

    folder = filedialog.askdirectory(
        title="Choose Folder to Organize"
    )

    if not folder:
        return

    selected_folder = folder

    folder_label.config(
        text=folder
    )

    status_label.config(
        text="Folder selected. Click Organize Files."
    )


# ============================================================
# Find category for a file
# ============================================================

def get_category(extension):

    # Go through every category
    for category, extensions in FILE_TYPES.items():

        # Check whether the file extension belongs there
        if extension in extensions:

            return category

    # Anything we do not recognize goes here
    return "Other"


# ============================================================
# Create a unique file name
# ============================================================
#
# Example:
#
# photo.jpg
#
# If photo.jpg already exists:
#
# photo_1.jpg
#
# If that also exists:
#
# photo_2.jpg
#
# This prevents files from being overwritten.
# ============================================================

def get_unique_destination(destination):

    # If the file name does not already exist,
    # use it normally.
    if not destination.exists():

        return destination

    # File name without extension
    stem = destination.stem

    # File extension
    suffix = destination.suffix

    # Parent folder
    parent = destination.parent

    counter = 1

    while True:

        new_name = (
            f"{stem}_{counter}{suffix}"
        )

        new_destination = (
            parent / new_name
        )

        # Stop when we find a name that does not exist
        if not new_destination.exists():

            return new_destination

        counter += 1


# ============================================================
# Organize files
# ============================================================

def organize_files():

    if not selected_folder:

        messagebox.showwarning(
            "No Folder",
            "Please choose a folder first."
        )

        return

    # Ask for confirmation because files will actually move
    answer = messagebox.askyesno(

        "Organize Files",

        "This will move files into category folders.\n\n"
        "Do you want to continue?"

    )

    if not answer:

        return

    try:

        folder_path = Path(
            selected_folder
        )

        moved_files = 0

        skipped_files = 0

        # ====================================================
        # Look through everything in the selected folder
        # ====================================================

        for item in folder_path.iterdir():

            # ------------------------------------------------
            # Ignore folders
            #
            # This program only organizes files directly
            # inside the selected folder.
            # ------------------------------------------------

            if item.is_dir():

                continue

            # ------------------------------------------------
            # Ignore the organizer itself if the Python file
            # happens to be inside the selected folder.
            # ------------------------------------------------

            if item.name == Path(__file__).name:

                skipped_files += 1

                continue

            # Get extension
            extension = item.suffix.lower()

            # ------------------------------------------------
            # Files without extensions
            # ------------------------------------------------

            if not extension:

                category = "Other"

            else:

                category = get_category(
                    extension
                )

            # ------------------------------------------------
            # Create category folder
            # ------------------------------------------------

            destination_folder = (
                folder_path / category
            )

            destination_folder.mkdir(
                exist_ok=True
            )

            # ------------------------------------------------
            # Destination file
            # ------------------------------------------------

            destination = (
                destination_folder
                / item.name
            )

            # Make sure we do not overwrite another file
            destination = get_unique_destination(
                destination
            )

            # ------------------------------------------------
            # Move file
            # ------------------------------------------------

            shutil.move(
                str(item),
                str(destination)
            )

            moved_files += 1

        # ====================================================
        # Finished
        # ====================================================

        status_label.config(

            text=(
                f"Finished! {moved_files} files organized."
            )

        )

        messagebox.showinfo(

            "Finished",

            f"File organization completed!\n\n"
            f"Files moved: {moved_files}\n"
            f"Files skipped: {skipped_files}"

        )

    except Exception as error:

        messagebox.showerror(

            "Error",

            f"Something went wrong:\n\n{error}"

        )

        status_label.config(
            text="Organization failed."
        )


# ============================================================
# Main window
# ============================================================

window = tk.Tk()


window.title(
    "File Organizer"
)


window.geometry(
    "650x430"
)


window.minsize(
    600,
    400
)


# ============================================================
# Title
# ============================================================

title_label = tk.Label(

    window,

    text="File Organizer",

    font=(
        "Segoe UI",
        20,
        "bold"
    )

)


title_label.pack(
    pady=(30, 5)
)


# ============================================================
# Description
# ============================================================

description_label = tk.Label(

    window,

    text=(
        "Automatically organize files by type.\n"
        "Images, videos, audio, documents, archives, code and more."
    ),

    justify="center"

)


description_label.pack(
    pady=(5, 25)
)


# ============================================================
# Choose folder
# ============================================================

choose_button = tk.Button(

    window,

    text="Choose Folder",

    command=choose_folder,

    width=22,

    height=2

)


choose_button.pack(
    pady=5
)


# ============================================================
# Selected folder
# ============================================================

folder_label = tk.Label(

    window,

    text="No folder selected",

    wraplength=550

)


folder_label.pack(
    pady=15
)


# ============================================================
# Organize button
# ============================================================

organize_button = tk.Button(

    window,

    text="Organize Files",

    command=organize_files,

    width=22,

    height=2

)


organize_button.pack(
    pady=10
)


# ============================================================
# Warning
# ============================================================

warning_label = tk.Label(

    window,

    text=(
        "⚠ Files will be moved into new folders.\n"
        "Test with copies first if the files are important."
    ),

    justify="center"

)


warning_label.pack(
    pady=15
)


# ============================================================
# Status
# ============================================================

status_label = tk.Label(

    window,

    text="Choose a folder to begin."

)


status_label.pack(
    pady=10
)


# ============================================================
# Keep window open
# ============================================================

window.mainloop()
