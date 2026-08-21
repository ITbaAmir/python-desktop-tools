# ============================================================
# Background Remover
# ============================================================
#
# What this program does:
# This program removes the background from an image.
#
# You can:
# - Choose an image
# - See the original image
# - Remove the background
# - See the result
# - Save the result as a transparent PNG file
#
# Required libraries:
# Open the VS Code terminal and run:
#
# pip install "rembg[cpu]" pillow
#
# IMPORTANT:
# rembg currently requires Python 3.11, 3.12 or 3.13.
#
# The first background removal may take longer because
# the AI model may need to be downloaded automatically.
# ============================================================


# tkinter creates the window and buttons
import tkinter as tk

# filedialog lets us choose and save files
# messagebox shows popup messages
from tkinter import filedialog, messagebox

# Pillow loads, resizes and displays images
from PIL import Image, ImageTk

# rembg removes the background
from rembg import remove

# threading prevents the window from freezing
# while the AI is processing the image
import threading

# io lets us work with image data in memory
import io


# ============================================================
# Variables
# ============================================================

# Stores the original image
original_image = None

# Stores the finished transparent image
result_image = None


# ------------------------------------------------------------
# Function: choose_image
#
# Lets the user choose an image from the computer.
# ------------------------------------------------------------
def choose_image():

    global original_image
    global result_image

    file_path = filedialog.askopenfilename(
        title="Choose Image",
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp"),
            ("PNG Files", "*.png"),
            ("JPEG Files", "*.jpg *.jpeg")
        ]
    )

    # Stop if the user cancels
    if not file_path:
        return

    try:

        # Open the selected image
        original_image = Image.open(file_path)

        # Clear the previous result
        result_image = None

        # Show the original image
        show_image(
            original_image,
            original_preview
        )

        # Remove previous result preview
        result_preview.config(
            image="",
            text="Result will appear here"
        )

        result_preview.image = None

        # Disable save until a new result exists
        save_button.config(
            state="disabled"
        )

        # Enable remove button
        remove_button.config(
            state="normal"
        )

        status_label.config(
            text="Image selected. Click Remove Background."
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Could not open the image:\n\n{error}"
        )


# ------------------------------------------------------------
# Function: show_image
#
# Makes a preview copy and shows it inside the program.
# ------------------------------------------------------------
def show_image(image, label):

    # Create a copy so the original image is not changed
    preview = image.copy()

    # Resize the preview while keeping the correct proportions
    preview.thumbnail(
        (330, 330)
    )

    # Convert the image so tkinter can display it
    photo = ImageTk.PhotoImage(
        preview
    )

    # Display the image
    label.config(
        image=photo,
        text=""
    )

    # Keep a reference so tkinter does not remove the image
    label.image = photo


# ------------------------------------------------------------
# Function: start_background_removal
#
# Starts the removal process in a separate thread.
# ------------------------------------------------------------
def start_background_removal():

    if original_image is None:

        messagebox.showwarning(
            "No Image",
            "Please choose an image first."
        )

        return

    # Disable buttons while processing
    remove_button.config(
        state="disabled"
    )

    choose_button.config(
        state="disabled"
    )

    save_button.config(
        state="disabled"
    )

    status_label.config(
        text="Removing background..."
    )

    # Run the AI processing separately so the window
    # stays responsive
    threading.Thread(
        target=remove_background,
        daemon=True
    ).start()


# ------------------------------------------------------------
# Function: remove_background
#
# Performs the actual AI background removal.
# ------------------------------------------------------------
def remove_background():

    global result_image

    try:

        # Create temporary memory storage
        input_buffer = io.BytesIO()

        # Save the original image into memory as PNG
        original_image.save(
            input_buffer,
            format="PNG"
        )

        # Get the image bytes
        input_data = input_buffer.getvalue()

        # Remove the background
        output_data = remove(
            input_data
        )

        # Open the transparent result
        result_image = Image.open(
            io.BytesIO(output_data)
        ).convert("RGBA")

        # Update the window safely
        window.after(
            0,
            background_removal_finished
        )

    except Exception as error:

        window.after(
            0,
            lambda: background_removal_error(error)
        )


# ------------------------------------------------------------
# Function: background_removal_finished
#
# Runs after the AI finishes successfully.
# ------------------------------------------------------------
def background_removal_finished():

    # Show the result
    show_image(
        result_image,
        result_preview
    )

    # Enable buttons again
    choose_button.config(
        state="normal"
    )

    remove_button.config(
        state="normal"
    )

    save_button.config(
        state="normal"
    )

    status_label.config(
        text="Background removed successfully."
    )


# ------------------------------------------------------------
# Function: background_removal_error
#
# Shows an error if background removal fails.
# ------------------------------------------------------------
def background_removal_error(error):

    choose_button.config(
        state="normal"
    )

    remove_button.config(
        state="normal"
    )

    status_label.config(
        text="Background removal failed."
    )

    messagebox.showerror(
        "Error",
        f"Could not remove the background:\n\n{error}"
    )


# ------------------------------------------------------------
# Function: save_result
#
# Saves the transparent image as PNG.
# ------------------------------------------------------------
def save_result():

    if result_image is None:

        messagebox.showwarning(
            "No Result",
            "Please remove the background first."
        )

        return

    file_path = filedialog.asksaveasfilename(
        title="Save Image",
        defaultextension=".png",
        filetypes=[
            ("PNG Image", "*.png")
        ]
    )

    if not file_path:
        return

    try:

        # PNG supports transparent backgrounds
        result_image.save(
            file_path,
            format="PNG"
        )

        messagebox.showinfo(
            "Saved",
            "The transparent image was saved successfully!"
        )

        status_label.config(
            text="Image saved successfully."
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Could not save the image:\n\n{error}"
        )


# ============================================================
# Create the main window
# ============================================================

window = tk.Tk()

window.title(
    "Background Remover"
)

window.geometry(
    "800x600"
)

window.minsize(
    750,
    550
)


# ============================================================
# Title
# ============================================================

title_label = tk.Label(
    window,
    text="Background Remover",
    font=("Segoe UI", 18, "bold")
)

title_label.pack(
    pady=(20, 5)
)


description_label = tk.Label(
    window,
    text="Choose an image, remove its background, then save it as PNG."
)

description_label.pack(
    pady=(0, 15)
)


# ============================================================
# Choose image button
# ============================================================

choose_button = tk.Button(
    window,
    text="Choose Image",
    command=choose_image,
    width=20,
    height=2
)

choose_button.pack(
    pady=5
)


# ============================================================
# Preview area
# ============================================================

preview_frame = tk.Frame(
    window
)

preview_frame.pack(
    pady=15,
    padx=20,
    fill="both",
    expand=True
)


# ------------------------------------------------------------
# Original image area
# ------------------------------------------------------------

original_frame = tk.Frame(
    preview_frame
)

original_frame.pack(
    side="left",
    expand=True,
    fill="both",
    padx=10
)


original_title = tk.Label(
    original_frame,
    text="Original",
    font=("Segoe UI", 12, "bold")
)

original_title.pack(
    pady=5
)


original_preview = tk.Label(
    original_frame,
    text="Original image will appear here",
    width=40,
    height=18,
    relief="groove"
)

original_preview.pack(
    expand=True,
    fill="both"
)


# ------------------------------------------------------------
# Result image area
# ------------------------------------------------------------

result_frame = tk.Frame(
    preview_frame
)

result_frame.pack(
    side="right",
    expand=True,
    fill="both",
    padx=10
)


result_title = tk.Label(
    result_frame,
    text="Background Removed",
    font=("Segoe UI", 12, "bold")
)

result_title.pack(
    pady=5
)


result_preview = tk.Label(
    result_frame,
    text="Result will appear here",
    width=40,
    height=18,
    relief="groove"
)

result_preview.pack(
    expand=True,
    fill="both"
)


# ============================================================
# Buttons
# ============================================================

button_frame = tk.Frame(
    window
)

button_frame.pack(
    pady=10
)


remove_button = tk.Button(
    button_frame,
    text="Remove Background",
    command=start_background_removal,
    width=20,
    height=2,
    state="disabled"
)

remove_button.grid(
    row=0,
    column=0,
    padx=10
)


save_button = tk.Button(
    button_frame,
    text="Save PNG",
    command=save_result,
    width=20,
    height=2,
    state="disabled"
)

save_button.grid(
    row=0,
    column=1,
    padx=10
)


# ============================================================
# Status
# ============================================================

status_label = tk.Label(
    window,
    text="Choose an image to begin."
)

status_label.pack(
    pady=(5, 20)
)


# ============================================================
# Keep the window open
# ============================================================

window.mainloop()
