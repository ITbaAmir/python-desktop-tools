# ============================================================
# Barcode Generator
# ============================================================
#
# What this program does:
# This program creates a barcode from text or numbers.
# The barcode is shown inside the program before saving it.
#
# Required libraries:
# Open the VS Code terminal and run:
#
# pip install python-barcode pillow
#
# You only need to install these libraries once.
# ============================================================


# tkinter creates the window and buttons
import tkinter as tk

# messagebox shows popup messages
# filedialog lets the user choose where to save the barcode
from tkinter import messagebox, filedialog

# barcode creates the barcode
import barcode

# ImageWriter lets barcode save the result as a PNG image
from barcode.writer import ImageWriter

# Pillow is used to display the barcode inside tkinter
from PIL import Image, ImageTk

# BytesIO temporarily stores the generated barcode in memory
from io import BytesIO


# This variable stores the generated barcode image
barcode_image = None


# ------------------------------------------------------------
# Function: create_barcode
# Creates the barcode and shows a preview.
# ------------------------------------------------------------
def create_barcode():

    global barcode_image

    # Get the text entered by the user
    text = text_entry.get().strip()

    # Check if the input is empty
    if not text:
        messagebox.showwarning(
            "Missing Text",
            "Please enter some text or numbers."
        )
        return

    try:

        # Code128 supports letters, numbers and many symbols,
        # so it is a good general-purpose barcode format.
        barcode_class = barcode.get_barcode_class("code128")

        # Create the barcode object
        generated_barcode = barcode_class(
            text,
            writer=ImageWriter()
        )

        # Create temporary memory storage
        memory_file = BytesIO()

        # Write the barcode image into memory
        generated_barcode.write(memory_file)

        # Go back to the beginning of the memory file
        memory_file.seek(0)

        # Open the generated barcode image
        barcode_image = Image.open(memory_file).copy()

        # Create a smaller copy for the preview
        preview_image = barcode_image.copy()

        # Resize it so it fits nicely inside the window
        preview_image.thumbnail((450, 220))

        # Convert the image so tkinter can display it
        preview_photo = ImageTk.PhotoImage(preview_image)

        # Show the image
        barcode_preview.config(image=preview_photo)

        # Keep a reference to the image
        barcode_preview.image = preview_photo

        # Enable the Save button
        save_button.config(state="normal")

        # Update the status message
        status_label.config(
            text="Barcode created successfully."
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Something went wrong:\n\n{error}"
        )


# ------------------------------------------------------------
# Function: save_barcode
# Saves the barcode as a PNG image.
# ------------------------------------------------------------
def save_barcode():

    # Make sure a barcode exists
    if barcode_image is None:
        messagebox.showwarning(
            "No Barcode",
            "Please create a barcode first."
        )
        return

    # Ask the user where the image should be saved
    file_path = filedialog.asksaveasfilename(
        title="Save Barcode",
        defaultextension=".png",
        filetypes=[
            ("PNG Image", "*.png")
        ]
    )

    # Stop if the user cancels
    if not file_path:
        return

    try:

        # Save the barcode image
        barcode_image.save(file_path)

        messagebox.showinfo(
            "Saved",
            "Barcode saved successfully!"
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Could not save the barcode:\n\n{error}"
        )


# ============================================================
# Create the main window
# ============================================================

window = tk.Tk()

window.title("Barcode Generator")

window.geometry("550x500")

window.minsize(550, 500)


# ------------------------------------------------------------
# Title
# ------------------------------------------------------------

title_label = tk.Label(
    window,
    text="Barcode Generator",
    font=("Segoe UI", 18, "bold")
)

title_label.pack(pady=(20, 10))


# ------------------------------------------------------------
# Instructions
# ------------------------------------------------------------

instruction_label = tk.Label(
    window,
    text="Enter text or numbers:"
)

instruction_label.pack()


# ------------------------------------------------------------
# Input field
# ------------------------------------------------------------

text_entry = tk.Entry(
    window,
    width=55,
    font=("Segoe UI", 11)
)

text_entry.pack(
    pady=10,
    padx=20
)

text_entry.focus()


# ------------------------------------------------------------
# Create button
# ------------------------------------------------------------

create_button = tk.Button(
    window,
    text="Create Barcode",
    command=create_barcode,
    width=20,
    height=2
)

create_button.pack(pady=10)


# ------------------------------------------------------------
# Barcode preview
# ------------------------------------------------------------

barcode_preview = tk.Label(window)

barcode_preview.pack(
    pady=15,
    padx=20
)


# ------------------------------------------------------------
# Save button
#
# Disabled until a barcode has been created.
# ------------------------------------------------------------

save_button = tk.Button(
    window,
    text="Save Barcode",
    command=save_barcode,
    width=20,
    height=2,
    state="disabled"
)

save_button.pack(pady=10)


# ------------------------------------------------------------
# Status message
# ------------------------------------------------------------

status_label = tk.Label(
    window,
    text="Enter something above and create your barcode."
)

status_label.pack(pady=5)


# ============================================================
# Keep the window open
# ============================================================

window.mainloop()
