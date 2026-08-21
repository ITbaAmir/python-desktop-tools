# ============================================================
# PDF Password Protector
# ============================================================
#
# What this program does:
# This program lets you choose a PDF file, enter a password,
# and save a new password-protected copy of the PDF.
#
# Required library:
# Open the VS Code terminal and run:
#
# pip install pypdf
#
# You only need to install this library once.
# ============================================================


# tkinter creates the window and controls
import tkinter as tk

# filedialog lets the user choose files
# messagebox shows popup messages
from tkinter import filedialog, messagebox

# Path helps us work with file names and folders
from pathlib import Path

# pypdf reads, copies and encrypts PDF files
from pypdf import PdfReader, PdfWriter


# This variable stores the selected PDF file path
selected_pdf = None


# ------------------------------------------------------------
# Function: choose_pdf
# Lets the user select a PDF file.
# ------------------------------------------------------------
def choose_pdf():

    global selected_pdf

    # Open a file selection window
    file_path = filedialog.askopenfilename(
        title="Choose PDF File",
        filetypes=[
            ("PDF Files", "*.pdf")
        ]
    )

    # Stop if the user cancels
    if not file_path:
        return

    # Store the selected file
    selected_pdf = file_path

    # Show only the file name inside the program
    file_name = Path(file_path).name

    selected_file_label.config(
        text=f"Selected: {file_name}"
    )

    status_label.config(
        text="PDF selected. Enter a password below."
    )


# ------------------------------------------------------------
# Function: protect_pdf
# Creates a password-protected copy of the selected PDF.
# ------------------------------------------------------------
def protect_pdf():

    # Make sure the user selected a PDF first
    if not selected_pdf:
        messagebox.showwarning(
            "No PDF Selected",
            "Please choose a PDF file first."
        )
        return

    # Get the password entered by the user
    password = password_entry.get()

    # Get the confirmation password
    confirm_password = confirm_password_entry.get()

    # Check if the password is empty
    if not password:
        messagebox.showwarning(
            "Missing Password",
            "Please enter a password."
        )
        return

    # Make sure both passwords match
    if password != confirm_password:
        messagebox.showwarning(
            "Passwords Do Not Match",
            "The two passwords are different."
        )
        return

    # Suggest a useful output file name
    original_path = Path(selected_pdf)

    suggested_name = (
        original_path.stem
        + "_protected.pdf"
    )

    # Ask where the protected PDF should be saved
    save_path = filedialog.asksaveasfilename(
        title="Save Protected PDF",
        initialfile=suggested_name,
        defaultextension=".pdf",
        filetypes=[
            ("PDF Files", "*.pdf")
        ]
    )

    # Stop if the user cancels
    if not save_path:
        return

    try:

        # Open the original PDF
        reader = PdfReader(selected_pdf)

        # Create a new PDF writer
        writer = PdfWriter()

        # Copy every page from the original PDF
        for page in reader.pages:
            writer.add_page(page)

        # Protect the PDF with the entered password
        writer.encrypt(password)

        # Save the new protected PDF
        with open(save_path, "wb") as output_file:
            writer.write(output_file)

        # Show success message
        messagebox.showinfo(
            "Success",
            "The password-protected PDF was created successfully!"
        )

        status_label.config(
            text="Protected PDF saved successfully."
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Something went wrong:\n\n{error}"
        )


# ============================================================
# Create the main program window
# ============================================================

window = tk.Tk()

window.title("PDF Password Protector")

window.geometry("520x420")

window.minsize(520, 420)


# ------------------------------------------------------------
# Title
# ------------------------------------------------------------

title_label = tk.Label(
    window,
    text="PDF Password Protector",
    font=("Segoe UI", 18, "bold")
)

title_label.pack(
    pady=(20, 10)
)


# ------------------------------------------------------------
# Description
# ------------------------------------------------------------

description_label = tk.Label(
    window,
    text="Choose a PDF and create a password-protected copy."
)

description_label.pack(
    pady=(0, 15)
)


# ------------------------------------------------------------
# Choose PDF button
# ------------------------------------------------------------

choose_button = tk.Button(
    window,
    text="Choose PDF",
    command=choose_pdf,
    width=20,
    height=2
)

choose_button.pack(
    pady=5
)


# ------------------------------------------------------------
# Selected file information
# ------------------------------------------------------------

selected_file_label = tk.Label(
    window,
    text="No PDF selected"
)

selected_file_label.pack(
    pady=10
)


# ------------------------------------------------------------
# Password label
# ------------------------------------------------------------

password_label = tk.Label(
    window,
    text="Password:"
)

password_label.pack()


# ------------------------------------------------------------
# Password input
#
# show="*" hides the password while typing.
# ------------------------------------------------------------

password_entry = tk.Entry(
    window,
    width=35,
    font=("Segoe UI", 11),
    show="*"
)

password_entry.pack(
    pady=(5, 10)
)


# ------------------------------------------------------------
# Confirm password label
# ------------------------------------------------------------

confirm_password_label = tk.Label(
    window,
    text="Confirm Password:"
)

confirm_password_label.pack()


# ------------------------------------------------------------
# Confirm password input
# ------------------------------------------------------------

confirm_password_entry = tk.Entry(
    window,
    width=35,
    font=("Segoe UI", 11),
    show="*"
)

confirm_password_entry.pack(
    pady=(5, 15)
)


# ------------------------------------------------------------
# Protect PDF button
# ------------------------------------------------------------

protect_button = tk.Button(
    window,
    text="Protect PDF",
    command=protect_pdf,
    width=20,
    height=2
)

protect_button.pack(
    pady=5
)


# ------------------------------------------------------------
# Status message
# ------------------------------------------------------------

status_label = tk.Label(
    window,
    text="Choose a PDF to begin."
)

status_label.pack(
    pady=15
)


# ============================================================
# Keep the program window open
# ============================================================

window.mainloop()
