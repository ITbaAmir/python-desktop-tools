# ============================================================
# Image to PDF Converter
# ============================================================
#
# What this program does:
# This program combines one or more images into a single PDF.
#
# You can:
# - Select multiple images
# - Change their order
# - Remove images from the list
# - Save all images as one PDF file
#
# Supported image types:
# - JPG / JPEG
# - PNG
# - BMP
# - WebP
# - TIFF
#
# Required library:
#
# pip install pillow
#
# You only need to install Pillow once.
#
# Run with:
#
# py image-to-pdf\image_to_pdf.py
# ============================================================


import tkinter as tk

from tkinter import filedialog, messagebox

# Pillow opens and converts images
from PIL import Image

# Path makes file names easier to work with
from pathlib import Path


# ============================================================
# Selected images
# ============================================================
#
# This list stores the full paths of all selected images.
# ============================================================

selected_images = []


# ============================================================
# Refresh list
# ============================================================
#
# Updates the list shown inside the program.
# ============================================================

def refresh_list():

    image_listbox.delete(
        0,
        tk.END
    )

    for index, image_path in enumerate(
        selected_images,
        start=1
    ):

        file_name = Path(
            image_path
        ).name

        image_listbox.insert(
            tk.END,
            f"{index}. {file_name}"
        )

    image_count_label.config(
        text=f"{len(selected_images)} image(s) selected"
    )


# ============================================================
# Add images
# ============================================================

def add_images():

    files = filedialog.askopenfilenames(

        title="Choose Images",

        filetypes=[

            (
                "Image Files",
                "*.jpg *.jpeg *.png *.bmp *.webp *.tif *.tiff"
            ),

            (
                "JPEG Images",
                "*.jpg *.jpeg"
            ),

            (
                "PNG Images",
                "*.png"
            ),

            (
                "All Files",
                "*.*"
            )

        ]

    )

    # Stop if the user cancels
    if not files:
        return

    # Add each selected file
    for file_path in files:

        # Avoid adding the exact same image twice
        if file_path not in selected_images:

            selected_images.append(
                file_path
            )

    refresh_list()

    status_label.config(
        text="Images added."
    )


# ============================================================
# Remove selected image
# ============================================================

def remove_image():

    selection = image_listbox.curselection()

    if not selection:

        messagebox.showwarning(
            "No Image Selected",
            "Please select an image from the list."
        )

        return

    index = selection[0]

    selected_images.pop(
        index
    )

    refresh_list()

    status_label.config(
        text="Image removed."
    )


# ============================================================
# Move image up
# ============================================================

def move_up():

    selection = image_listbox.curselection()

    if not selection:
        return

    index = selection[0]

    # First image cannot move higher
    if index == 0:
        return

    # Swap with the image above
    selected_images[index - 1], selected_images[index] = (

        selected_images[index],
        selected_images[index - 1]

    )

    refresh_list()

    # Select the moved image again
    image_listbox.selection_set(
        index - 1
    )


# ============================================================
# Move image down
# ============================================================

def move_down():

    selection = image_listbox.curselection()

    if not selection:
        return

    index = selection[0]

    # Last image cannot move lower
    if index >= len(selected_images) - 1:
        return

    # Swap with the image below
    selected_images[index + 1], selected_images[index] = (

        selected_images[index],
        selected_images[index + 1]

    )

    refresh_list()

    # Select the moved image again
    image_listbox.selection_set(
        index + 1
    )


# ============================================================
# Clear list
# ============================================================

def clear_images():

    if not selected_images:
        return

    answer = messagebox.askyesno(

        "Clear Images",

        "Remove all selected images from the list?"

    )

    if not answer:
        return

    selected_images.clear()

    refresh_list()

    status_label.config(
        text="Image list cleared."
    )


# ============================================================
# Convert image for PDF
# ============================================================
#
# PDFs work best with RGB images.
#
# PNG and some other formats can contain transparent areas.
# We place transparent images onto a white background.
# ============================================================

def prepare_image_for_pdf(image_path):

    image = Image.open(
        image_path
    )

    # --------------------------------------------------------
    # Handle transparent images
    # --------------------------------------------------------

    if image.mode in (
        "RGBA",
        "LA"
    ):

        # Convert to RGBA first
        image = image.convert(
            "RGBA"
        )

        # Create white background
        background = Image.new(

            "RGB",

            image.size,

            "white"

        )

        # Paste transparent image onto white background
        background.paste(

            image,

            mask=image.getchannel(
                "A"
            )

        )

        return background

    # --------------------------------------------------------
    # Handle palette images with transparency
    # --------------------------------------------------------

    if image.mode == "P":

        image = image.convert(
            "RGBA"
        )

        background = Image.new(

            "RGB",

            image.size,

            "white"

        )

        background.paste(

            image,

            mask=image.getchannel(
                "A"
            )

        )

        return background

    # --------------------------------------------------------
    # Everything else
    # --------------------------------------------------------

    return image.convert(
        "RGB"
    )


# ============================================================
# Create PDF
# ============================================================

def create_pdf():

    # Make sure images exist
    if not selected_images:

        messagebox.showwarning(

            "No Images",

            "Please add at least one image first."

        )

        return

    # Ask where to save the PDF
    save_path = filedialog.asksaveasfilename(

        title="Save PDF",

        defaultextension=".pdf",

        filetypes=[

            (
                "PDF File",
                "*.pdf"
            )

        ]

    )

    if not save_path:
        return

    try:

        status_label.config(
            text="Creating PDF..."
        )

        window.update_idletasks()

        pdf_images = []

        # ----------------------------------------------------
        # Open and prepare every image
        # ----------------------------------------------------

        for image_path in selected_images:

            converted_image = prepare_image_for_pdf(
                image_path
            )

            pdf_images.append(
                converted_image
            )

        # ----------------------------------------------------
        # First image becomes the first PDF page
        # ----------------------------------------------------

        first_image = pdf_images[0]

        # Everything else becomes additional pages
        additional_images = pdf_images[1:]

        # ----------------------------------------------------
        # Save as PDF
        # ----------------------------------------------------

        first_image.save(

            save_path,

            "PDF",

            save_all=True,

            append_images=additional_images,

            resolution=100.0

        )

        # Close images after saving
        for image in pdf_images:

            image.close()

        status_label.config(
            text="PDF created successfully."
        )

        messagebox.showinfo(

            "Success",

            "Your PDF was created successfully!"

        )

    except Exception as error:

        status_label.config(
            text="PDF creation failed."
        )

        messagebox.showerror(

            "Error",

            f"Could not create the PDF:\n\n{error}"

        )


# ============================================================
# Main window
# ============================================================

window = tk.Tk()


window.title(
    "Image to PDF Converter"
)


window.geometry(
    "700x620"
)


window.minsize(
    650,
    570
)


# ============================================================
# Title
# ============================================================

title_label = tk.Label(

    window,

    text="Image to PDF Converter",

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
        "Select images, arrange their order, "
        "and combine them into one PDF."
    )

)


description_label.pack(
    pady=(0, 20)
)


# ============================================================
# Add images
# ============================================================

add_button = tk.Button(

    window,

    text="Add Images",

    command=add_images,

    width=20,

    height=2

)


add_button.pack(
    pady=5
)


# ============================================================
# Image count
# ============================================================

image_count_label = tk.Label(

    window,

    text="0 image(s) selected"

)


image_count_label.pack(
    pady=5
)


# ============================================================
# Image list
# ============================================================

list_frame = tk.Frame(
    window
)


list_frame.pack(
    pady=10
)


image_listbox = tk.Listbox(

    list_frame,

    width=65,

    height=15,

    font=(
        "Segoe UI",
        10
    )

)


image_listbox.grid(

    row=0,
    column=0,

    padx=5

)


# Scrollbar
scrollbar = tk.Scrollbar(

    list_frame,

    command=image_listbox.yview

)


scrollbar.grid(

    row=0,
    column=1,

    sticky="ns"

)


image_listbox.config(
    yscrollcommand=scrollbar.set
)


# ============================================================
# Order buttons
# ============================================================

order_buttons = tk.Frame(
    window
)


order_buttons.pack(
    pady=5
)


move_up_button = tk.Button(

    order_buttons,

    text="Move Up",

    command=move_up,

    width=12

)


move_up_button.grid(

    row=0,
    column=0,

    padx=5

)


move_down_button = tk.Button(

    order_buttons,

    text="Move Down",

    command=move_down,

    width=12

)


move_down_button.grid(

    row=0,
    column=1,

    padx=5

)


remove_button = tk.Button(

    order_buttons,

    text="Remove",

    command=remove_image,

    width=12

)


remove_button.grid(

    row=0,
    column=2,

    padx=5

)


clear_button = tk.Button(

    order_buttons,

    text="Clear All",

    command=clear_images,

    width=12

)


clear_button.grid(

    row=0,
    column=3,

    padx=5

)


# ============================================================
# Create PDF button
# ============================================================

create_button = tk.Button(

    window,

    text="Create PDF",

    command=create_pdf,

    width=22,

    height=2

)


create_button.pack(
    pady=20
)


# ============================================================
# Status
# ============================================================

status_label = tk.Label(

    window,

    text="Add images to begin."

)


status_label.pack(
    pady=5
)


# ============================================================
# Keep window open
# ============================================================

window.mainloop()
