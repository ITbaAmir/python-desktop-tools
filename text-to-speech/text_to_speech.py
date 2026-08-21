# ============================================================
# Text to Speech
# ============================================================
#
# What this program does:
# This program reads written text out loud.
#
# You can choose:
# - Language: English, German or Farsi
# - Voice: Male or Female
# - Speaking speed
#
# You can also save the speech as an MP3 file.
#
# Required libraries:
# Open the VS Code terminal and run:
#
# pip install edge-tts pygame
#
# You only need to install these libraries once.
#
# IMPORTANT:
# This program requires an internet connection because
# Microsoft Edge online voices are used.
# ============================================================


import tkinter as tk

# ttk gives us dropdown menus
from tkinter import ttk, messagebox, filedialog

# edge_tts creates the speech audio
import edge_tts

# pygame plays the created MP3 file
import pygame

# asyncio is needed because edge_tts works asynchronously
import asyncio

# threading prevents the window from freezing
import threading

# tempfile creates a temporary MP3 file
import tempfile

# os lets us remove temporary files
import os

# time is used when stopping/restarting playback
import time


# ============================================================
# Voice settings
# ============================================================
#
# Each language has one female and one male voice.
#
# These are Microsoft neural voices.
# ============================================================

VOICES = {

    "English": {
        "Female": "en-US-JennyNeural",
        "Male": "en-US-GuyNeural"
    },

    "German": {
        "Female": "de-DE-KatjaNeural",
        "Male": "de-DE-ConradNeural"
    },

    "Farsi": {
        "Female": "fa-IR-DilaraNeural",
        "Male": "fa-IR-FaridNeural"
    }
}


# ============================================================
# Variables used by the program
# ============================================================

temporary_audio_file = None

is_creating_audio = False


# ============================================================
# Start pygame audio system
# ============================================================

pygame.mixer.init()


# ------------------------------------------------------------
# Function: get_selected_voice
#
# Finds the correct Microsoft voice based on the selected
# language and gender.
# ------------------------------------------------------------
def get_selected_voice():

    language = language_box.get()
    gender = gender_box.get()

    return VOICES[language][gender]


# ------------------------------------------------------------
# Function: get_speed
#
# Converts the slider number into the format edge-tts needs.
#
# Example:
#
# 20  becomes +20%
# -20 becomes -20%
# 0   becomes +0%
# ------------------------------------------------------------
def get_speed():

    speed = int(speed_slider.get())

    if speed >= 0:
        return f"+{speed}%"

    return f"{speed}%"


# ------------------------------------------------------------
# Function: update_speed_label
#
# Updates the text next to the speed slider.
# ------------------------------------------------------------
def update_speed_label(value):

    speed = int(float(value))

    if speed > 0:
        speed_text = f"+{speed}% Faster"

    elif speed < 0:
        speed_text = f"{speed}% Slower"

    else:
        speed_text = "Normal Speed"

    speed_value_label.config(
        text=speed_text
    )


# ------------------------------------------------------------
# Function: create_audio
#
# Creates the MP3 file using Microsoft Edge TTS.
# ------------------------------------------------------------
async def create_audio(text, output_file):

    voice = get_selected_voice()

    speed = get_speed()

    # Create the speech
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=speed
    )

    # Save it as an MP3 file
    await communicate.save(output_file)


# ------------------------------------------------------------
# Function: speak_text
#
# Runs when the Speak button is clicked.
#
# A separate thread is used so the program window does not
# freeze while the audio is being created.
# ------------------------------------------------------------
def speak_text():

    global is_creating_audio

    text = text_box.get(
        "1.0",
        tk.END
    ).strip()

    # Check if there is text
    if not text:

        messagebox.showwarning(
            "Missing Text",
            "Please enter some text first."
        )

        return

    # Stop previous audio first
    stop_speech()

    # Prevent several audio-generation jobs from running
    # at exactly the same time.
    if is_creating_audio:
        return

    is_creating_audio = True

    status_label.config(
        text="Creating speech..."
    )

    # Run the speech creation in another thread
    threading.Thread(
        target=generate_and_play,
        args=(text,),
        daemon=True
    ).start()


# ------------------------------------------------------------
# Function: generate_and_play
#
# Creates the temporary MP3 file and then plays it.
#
# A NEW audio file is generated every time Speak is clicked.
# This makes repeated clicking much more reliable.
# ------------------------------------------------------------
def generate_and_play(text):

    global temporary_audio_file
    global is_creating_audio

    try:

        # Create a temporary MP3 file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3"
        )

        temporary_audio_file = temp_file.name

        temp_file.close()

        # Create the speech audio
        asyncio.run(
            create_audio(
                text,
                temporary_audio_file
            )
        )

        # Stop any audio that may still be playing
        pygame.mixer.music.stop()

        # Load the new MP3 file
        pygame.mixer.music.load(
            temporary_audio_file
        )

        # Play it
        pygame.mixer.music.play()

        status_label.config(
            text="Speaking..."
        )

        # Wait until playback finishes
        while pygame.mixer.music.get_busy():

            time.sleep(0.1)

        status_label.config(
            text="Finished speaking."
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Could not create the speech:\n\n{error}"
        )

        status_label.config(
            text="Speech failed."
        )

    finally:

        is_creating_audio = False


# ------------------------------------------------------------
# Function: stop_speech
#
# Stops currently playing speech.
# ------------------------------------------------------------
def stop_speech():

    try:

        pygame.mixer.music.stop()

        status_label.config(
            text="Speech stopped."
        )

    except Exception:
        pass


# ------------------------------------------------------------
# Function: save_as_mp3
#
# Saves the text as an MP3 using the currently selected:
#
# - Language
# - Voice
# - Speed
# ------------------------------------------------------------
def save_as_mp3():

    text = text_box.get(
        "1.0",
        tk.END
    ).strip()

    if not text:

        messagebox.showwarning(
            "Missing Text",
            "Please enter some text first."
        )

        return

    # Ask where the file should be saved
    file_path = filedialog.asksaveasfilename(
        title="Save Speech as MP3",
        defaultextension=".mp3",
        filetypes=[
            ("MP3 Audio", "*.mp3")
        ]
    )

    if not file_path:
        return

    status_label.config(
        text="Creating MP3..."
    )

    # Create the MP3 in another thread
    threading.Thread(
        target=create_saved_mp3,
        args=(text, file_path),
        daemon=True
    ).start()


# ------------------------------------------------------------
# Function: create_saved_mp3
#
# Performs the actual MP3 creation.
# ------------------------------------------------------------
def create_saved_mp3(text, file_path):

    try:

        asyncio.run(
            create_audio(
                text,
                file_path
            )
        )

        status_label.config(
            text="MP3 saved successfully."
        )

        messagebox.showinfo(
            "Saved",
            "The MP3 file was saved successfully!"
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Could not save the MP3:\n\n{error}"
        )

        status_label.config(
            text="Could not save MP3."
        )


# ------------------------------------------------------------
# Function: clear_text
#
# Removes everything from the text box.
# ------------------------------------------------------------
def clear_text():

    stop_speech()

    text_box.delete(
        "1.0",
        tk.END
    )

    status_label.config(
        text="Text cleared."
    )


# ------------------------------------------------------------
# Function: close_program
#
# Stops audio and closes pygame before the window closes.
# ------------------------------------------------------------
def close_program():

    try:

        pygame.mixer.music.stop()

        pygame.mixer.quit()

    except Exception:
        pass

    window.destroy()


# ============================================================
# Create main window
# ============================================================

window = tk.Tk()

window.title(
    "Text to Speech"
)

window.geometry(
    "700x670"
)

window.minsize(
    650,
    650
)


# ============================================================
# Title
# ============================================================

title_label = tk.Label(
    window,
    text="Text to Speech",
    font=("Segoe UI", 18, "bold")
)

title_label.pack(
    pady=(20, 5)
)


description_label = tk.Label(
    window,
    text="Choose a language, voice and speed, then enter your text."
)

description_label.pack(
    pady=(0, 15)
)


# ============================================================
# Settings frame
# ============================================================

settings_frame = tk.Frame(
    window
)

settings_frame.pack(
    pady=5
)


# ------------------------------------------------------------
# Language
# ------------------------------------------------------------

language_label = tk.Label(
    settings_frame,
    text="Language:"
)

language_label.grid(
    row=0,
    column=0,
    padx=10,
    pady=5
)


language_box = ttk.Combobox(
    settings_frame,
    values=[
        "English",
        "German",
        "Farsi"
    ],
    state="readonly",
    width=15
)

language_box.grid(
    row=0,
    column=1,
    padx=10,
    pady=5
)

# Default language
language_box.set(
    "English"
)


# ------------------------------------------------------------
# Gender
# ------------------------------------------------------------

gender_label = tk.Label(
    settings_frame,
    text="Voice:"
)

gender_label.grid(
    row=0,
    column=2,
    padx=10,
    pady=5
)


gender_box = ttk.Combobox(
    settings_frame,
    values=[
        "Female",
        "Male"
    ],
    state="readonly",
    width=15
)

gender_box.grid(
    row=0,
    column=3,
    padx=10,
    pady=5
)

# Default voice
gender_box.set(
    "Female"
)


# ============================================================
# Speed controls
# ============================================================

speed_frame = tk.Frame(
    window
)

speed_frame.pack(
    pady=15
)


speed_label = tk.Label(
    speed_frame,
    text="Speaking Speed:"
)

speed_label.pack()


# Speed range:
#
# -50 = 50% slower
#  0  = normal
# +50 = 50% faster
speed_slider = tk.Scale(
    speed_frame,
    from_=-50,
    to=50,
    orient="horizontal",
    length=350,
    command=update_speed_label
)

speed_slider.set(
    0
)

speed_slider.pack()


speed_value_label = tk.Label(
    speed_frame,
    text="Normal Speed"
)

speed_value_label.pack()


# ============================================================
# Text box
# ============================================================

text_label = tk.Label(
    window,
    text="Text:"
)

text_label.pack()


text_box = tk.Text(
    window,
    width=70,
    height=15,
    font=("Segoe UI", 11),
    wrap="word"
)

text_box.pack(
    padx=20,
    pady=10
)

text_box.focus()


# ============================================================
# Buttons
# ============================================================

button_frame = tk.Frame(
    window
)

button_frame.pack(
    pady=10
)


# Speak
speak_button = tk.Button(
    button_frame,
    text="▶ Speak",
    command=speak_text,
    width=13,
    height=2
)

speak_button.grid(
    row=0,
    column=0,
    padx=5
)


# Stop
stop_button = tk.Button(
    button_frame,
    text="■ Stop",
    command=stop_speech,
    width=13,
    height=2
)

stop_button.grid(
    row=0,
    column=1,
    padx=5
)


# Save
save_button = tk.Button(
    button_frame,
    text="Save MP3",
    command=save_as_mp3,
    width=13,
    height=2
)

save_button.grid(
    row=0,
    column=2,
    padx=5
)


# Clear
clear_button = tk.Button(
    button_frame,
    text="Clear",
    command=clear_text,
    width=13,
    height=2
)

clear_button.grid(
    row=0,
    column=3,
    padx=5
)


# ============================================================
# Status
# ============================================================

status_label = tk.Label(
    window,
    text="Enter some text to begin."
)

status_label.pack(
    pady=15
)


# Run close_program when the user presses X
window.protocol(
    "WM_DELETE_WINDOW",
    close_program
)


# ============================================================
# Keep window open
# ============================================================

window.mainloop()
