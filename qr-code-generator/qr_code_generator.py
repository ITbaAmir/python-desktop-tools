# ============================================================
# QR Code Generator
# ============================================================
#
# What this program does:
# This program creates a QR code from text or a website address.
# The QR code is shown inside the program before saving it.
#
# Required library:
# Open the VS Code terminal and run:
#
# pip install qrcode[pil]
#
# You only need to install this library once.
# ============================================================


# tkinter creates the window, buttons and text fields
import tkinter as tk

# messagebox shows popup messages
# filedialog lets the user choose where to save the QR code
from tkinter import messagebox, filedialog

# qrcode creates the QR code
import qrcode

# ImageTk allows us to display the QR image inside tkinter
from PIL import ImageTk


# This variable will hold the generated QR code image.
# We create it here so both functions can use it.
qr_image = None


# ------------------------------------------------------------
# Function: create_qr_code
# Creates the QR code and displays it inside the window.
# ------------------------------------------------------------
def create_qr_code():

    global qr_image

    # Get the text entered by the user
    text = text_entry.get().strip()

    # Check if the text box is empty
    if not text:
        messagebox.showwarning(
            "Missing Text",
            "Please enter some text or a website address."
        )
        return

    try:

        # Create the QR code
        qr_image = qrcode.make(text)

        # Resize a copy for displaying inside the program
        preview_image = qr_image.resize((250, 250))

        # Convert the image so tkinter can display it
        preview_photo = ImageTk.PhotoImage(preview_image)

        # Put the QR image inside the label
        qr_preview.config(image=preview_photo)

        # Keep a reference to the image.
        # Without this line, tkinter may remove the image.
        qr_preview.image = preview_photo

        # Enable the Save button now that a QR code exists
        save_button.config(state="normal")

        status_label.config(
            text="QR code created successfully."
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Something went wrong:\n\n{error}"
        )


# ------------------------------------------------------------
# Function: save_qr_code
# Lets the user save the generated QR code as a PNG file.
# ------------------------------------------------------------
def save_qr_code():

    # Make sure a QR code has been created first
    if qr_image is None:
        messagebox.showwarning(
            "No QR Code",
            "Please create a QR code first."
        )
        return

    # Ask where the file should be saved
    file_path = filedialog.asksaveasfilename(
        title="Save QR Code",
        defaultextension=".png",
        filetypes=[
            ("PNG Image", "*.png")
        ]
    )

    # If the user closes the save window, do nothing
    if not file_path:
        return

    try:

        # Save the original QR code image
        qr_image.save(file_path)

        messagebox.showinfo(
            "Saved",
            "QR code saved successfully!"
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Could not save the QR code:\n\n{error}"
        )


# ============================================================
# Create the main program window
# ============================================================

window = tk.Tk()

window.title("QR Code Generator")

# A larger window is needed because we now show the QR code
window.geometry("520x600")

window.minsize(520, 600)


# ------------------------------------------------------------
# Program title
# ------------------------------------------------------------

title_label = tk.Label(
    window,
    text="QR Code Generator",
    font=("Segoe UI", 18, "bold")
)

title_label.pack(pady=(20, 10))


# ------------------------------------------------------------
# Instructions
# ------------------------------------------------------------

instruction_label = tk.Label(
    window,
    text="Enter text or a website address:"
)

instruction_label.pack()


# ------------------------------------------------------------
# Text input
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

# Put the cursor automatically inside the input field
text_entry.focus()


# ------------------------------------------------------------
# Create QR Code button
# ------------------------------------------------------------

create_button = tk.Button(
    window,
    text="Create QR Code",
    command=create_qr_code,
    width=20,
    height=2
)

create_button.pack(pady=10)


# ------------------------------------------------------------
# QR Code preview
#
# The generated QR code will appear here.
# ------------------------------------------------------------

qr_preview = tk.Label(
    window
)

qr_preview.pack(pady=10)


# ------------------------------------------------------------
# Save button
#
# It starts disabled because no QR code exists yet.
# ------------------------------------------------------------

save_button = tk.Button(
    window,
    text="Save QR Code",
    command=save_qr_code,
    width=20,
    height=2,
    state="disabled"
)

save_button.pack(pady=10)


# ------------------------------------------------------------
# Status text
# ------------------------------------------------------------

status_label = tk.Label(
    window,
    text="Enter something above and create your QR code."
)

status_label.pack(pady=5)


# ============================================================
# Keep the window running
# ============================================================

window.mainloop()
