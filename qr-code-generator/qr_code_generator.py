# ============================================================
# QR Code Generator
# ============================================================
#
# What this program does:
# This program creates a QR code from text or a website address.
# It uses a simple Windows popup interface.
#
# Required library:
# Open the VS Code terminal and run:
#
# pip install qrcode[pil]
#
# You only need to install this library once.
# ============================================================


# tkinter creates the window and buttons
import tkinter as tk

# messagebox shows small popup messages
# filedialog lets the user choose where to save the QR code
from tkinter import messagebox, filedialog

# qrcode creates the actual QR code image
import qrcode


# ------------------------------------------------------------
# Function: create_qr_code
# This function runs when the user clicks the button.
# ------------------------------------------------------------
def create_qr_code():

    # Get the text from the input box
    text = text_entry.get().strip()

    # Check if the user entered something
    if not text:
        messagebox.showwarning(
            "Missing Text",
            "Please enter some text or a website address."
        )
        return

    # Ask the user where the QR code should be saved
    file_path = filedialog.asksaveasfilename(
        title="Save QR Code",
        defaultextension=".png",
        filetypes=[
            ("PNG Image", "*.png")
        ]
    )

    # If the user cancels the save window,
    # stop the function
    if not file_path:
        return

    try:

        # Create the QR code from the entered text
        qr_image = qrcode.make(text)

        # Save the QR code as a PNG image
        qr_image.save(file_path)

        # Show a success popup
        messagebox.showinfo(
            "Success",
            "QR code created successfully!"
        )

    except Exception as error:

        # Show an error message if something goes wrong
        messagebox.showerror(
            "Error",
            f"Something went wrong:\n\n{error}"
        )


# ============================================================
# Create the main program window
# ============================================================

window = tk.Tk()

# Window title
window.title("QR Code Generator")

# Window size
window.geometry("500x230")

# Prevent the window from becoming too small
window.minsize(500, 230)


# ------------------------------------------------------------
# Title
# ------------------------------------------------------------

title_label = tk.Label(
    window,
    text="QR Code Generator",
    font=("Segoe UI", 18, "bold")
)

title_label.pack(pady=(20, 10))


# ------------------------------------------------------------
# Instruction text
# ------------------------------------------------------------

instruction_label = tk.Label(
    window,
    text="Enter text or a website address:"
)

instruction_label.pack()


# ------------------------------------------------------------
# Text input box
# ------------------------------------------------------------

text_entry = tk.Entry(
    window,
    width=55,
    font=("Segoe UI", 11)
)

text_entry.pack(pady=10, padx=20)

# Automatically place the cursor in the text box
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


# ============================================================
# Keep the window open
# ============================================================

window.mainloop()