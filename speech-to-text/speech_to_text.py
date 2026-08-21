# ============================================================
# Speech to Text
# ============================================================
#
# What this program does:
# This program converts speech from your microphone into text.
#
# Supported languages:
# - English
# - German
# - Farsi / Persian
#
# Features:
# - Choose language
# - Record speech from microphone
# - Add recognized speech to the text box
# - Edit the text manually
# - Clear the text
# - Save the text as a TXT file
#
# Required library:
#
# py -m pip install "SpeechRecognition[audio]"
#
# This installs:
# - SpeechRecognition
# - PyAudio for microphone access
#
# IMPORTANT:
# This version uses Google's online speech recognition service,
# so an internet connection is required for recognition.
#
# Run with:
#
# py speech-to-text\speech_to_text.py
# ============================================================


import tkinter as tk

from tkinter import ttk, messagebox, filedialog

# SpeechRecognition handles microphone recording
# and converts speech into text.
import speech_recognition as sr

# threading keeps the window responsive while listening.
import threading


# ============================================================
# Language settings
# ============================================================
#
# These language codes tell the speech recognition service
# which language we are speaking.
# ============================================================

LANGUAGES = {

    "English": "en-US",

    "German": "de-DE",

    "Farsi": "fa-IR"

}


# ============================================================
# Create recognizer
# ============================================================

recognizer = sr.Recognizer()


# This helps the program automatically adapt to changing
# microphone/background noise levels.
recognizer.dynamic_energy_threshold = True


# Used to prevent multiple recordings at the same time.
is_listening = False


# ============================================================
# Start listening
# ============================================================

def start_listening():

    global is_listening

    # Do not start another recording if one is already active.
    if is_listening:

        return

    is_listening = True

    listen_button.config(
        state="disabled",
        text="Listening..."
    )

    status_label.config(
        text="Preparing microphone..."
    )

    # Run microphone work in a separate thread.
    threading.Thread(

        target=listen_and_recognize,

        daemon=True

    ).start()


# ============================================================
# Listen and recognize
# ============================================================

def listen_and_recognize():

    global is_listening

    try:

        # ----------------------------------------------------
        # Open default microphone
        # ----------------------------------------------------

        with sr.Microphone() as source:

            window.after(

                0,

                status_label.config,

                {
                    "text":
                    "Adjusting for background noise..."
                }

            )

            # Listen briefly to the room before recording.
            #
            # This helps SpeechRecognition understand
            # what counts as background noise.
            recognizer.adjust_for_ambient_noise(

                source,

                duration=0.7

            )

            window.after(

                0,

                status_label.config,

                {
                    "text":
                    "Listening... Speak now."
                }

            )

            # ------------------------------------------------
            # Record one spoken phrase
            # ------------------------------------------------
            #
            # timeout:
            # Maximum time to wait for the user to BEGIN.
            #
            # phrase_time_limit:
            # Maximum length of one recording.
            # ------------------------------------------------

            audio = recognizer.listen(

                source,

                timeout=8,

                phrase_time_limit=30

            )

        window.after(

            0,

            status_label.config,

            {
                "text":
                "Recognizing speech..."
            }

        )

        # Get selected language
        language_name = language_box.get()

        language_code = LANGUAGES[
            language_name
        ]

        # ----------------------------------------------------
        # Convert speech to text
        # ----------------------------------------------------

        recognized_text = recognizer.recognize_google(

            audio,

            language=language_code

        )

        # Add the text to our GUI safely.
        window.after(

            0,

            add_recognized_text,

            recognized_text

        )

    # ========================================================
    # User did not start talking before timeout
    # ========================================================

    except sr.WaitTimeoutError:

        window.after(

            0,

            show_listening_timeout

        )

    # ========================================================
    # Speech was heard but could not be understood
    # ========================================================

    except sr.UnknownValueError:

        window.after(

            0,

            show_unknown_speech

        )

    # ========================================================
    # Online recognition service error
    # ========================================================

    except sr.RequestError as error:

        window.after(

            0,

            show_service_error,

            str(error)

        )

    # ========================================================
    # Microphone or other unexpected error
    # ========================================================

    except Exception as error:

        window.after(

            0,

            show_general_error,

            str(error)

        )

    finally:

        is_listening = False

        window.after(

            0,

            reset_listen_button

        )


# ============================================================
# Add recognized text
# ============================================================

def add_recognized_text(text):

    # Check if the text box already has something.
    current_text = text_box.get(

        "1.0",

        tk.END

    ).strip()

    # Add a space between old and new text.
    if current_text:

        text_box.insert(

            tk.END,

            " "

        )

    # Add newly recognized text.
    text_box.insert(

        tk.END,

        text

    )

    # Automatically scroll to the end.
    text_box.see(

        tk.END

    )

    status_label.config(

        text="Speech recognized successfully."

    )


# ============================================================
# Reset Listen button
# ============================================================

def reset_listen_button():

    listen_button.config(

        state="normal",

        text="🎤 Start Listening"

    )


# ============================================================
# Timeout message
# ============================================================

def show_listening_timeout():

    status_label.config(

        text="No speech detected."

    )

    messagebox.showwarning(

        "No Speech",

        "I did not hear you start speaking.\n\n"
        "Click Start Listening and try again."

    )


# ============================================================
# Unknown speech
# ============================================================

def show_unknown_speech():

    status_label.config(

        text="Could not understand the speech."

    )

    messagebox.showwarning(

        "Could Not Understand",

        "Speech was detected, but it could not be understood.\n\n"
        "Try speaking more clearly or check the selected language."

    )


# ============================================================
# Recognition service error
# ============================================================

def show_service_error(error):

    status_label.config(

        text="Speech recognition service error."

    )

    messagebox.showerror(

        "Recognition Error",

        "The online speech recognition service could not be reached.\n\n"
        f"{error}"

    )


# ============================================================
# Other error
# ============================================================

def show_general_error(error):

    status_label.config(

        text="An error occurred."

    )

    messagebox.showerror(

        "Error",

        f"Something went wrong:\n\n{error}"

    )


# ============================================================
# Clear text
# ============================================================

def clear_text():

    text_box.delete(

        "1.0",

        tk.END

    )

    status_label.config(

        text="Text cleared."

    )


# ============================================================
# Copy is not required because normal Windows shortcuts
# already work inside the tkinter Text box:
#
# Ctrl + C
# Ctrl + X
# Ctrl + V
# ============================================================


# ============================================================
# Save text
# ============================================================

def save_text():

    text = text_box.get(

        "1.0",

        tk.END

    ).strip()

    # Make sure there is something to save.
    if not text:

        messagebox.showwarning(

            "No Text",

            "There is no text to save."

        )

        return

    # Ask where the TXT file should be saved.
    file_path = filedialog.asksaveasfilename(

        title="Save Transcription",

        defaultextension=".txt",

        filetypes=[

            (
                "Text File",
                "*.txt"
            )

        ]

    )

    if not file_path:

        return

    try:

        # UTF-8 is important because it correctly supports
        # English, German and Farsi characters.
        with open(

            file_path,

            "w",

            encoding="utf-8"

        ) as file:

            file.write(
                text
            )

        status_label.config(

            text="Text saved successfully."

        )

        messagebox.showinfo(

            "Saved",

            "The transcription was saved successfully."

        )

    except Exception as error:

        messagebox.showerror(

            "Save Error",

            f"Could not save the file:\n\n{error}"

        )


# ============================================================
# Main window
# ============================================================

window = tk.Tk()


window.title(

    "Speech to Text"

)


window.geometry(

    "720x600"

)


window.minsize(

    650,

    550

)


# ============================================================
# Title
# ============================================================

title_label = tk.Label(

    window,

    text="Speech to Text",

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
        "Choose your language, click Start Listening, "
        "and speak into your microphone."
    )

)


description_label.pack(

    pady=(0, 20)

)


# ============================================================
# Language selection
# ============================================================

language_frame = tk.Frame(

    window

)


language_frame.pack(

    pady=5

)


language_label = tk.Label(

    language_frame,

    text="Language:"

)


language_label.grid(

    row=0,

    column=0,

    padx=10

)


language_box = ttk.Combobox(

    language_frame,

    values=[

        "English",

        "German",

        "Farsi"

    ],

    state="readonly",

    width=20

)


language_box.grid(

    row=0,

    column=1,

    padx=10

)


language_box.set(

    "English"

)


# ============================================================
# Listen button
# ============================================================

listen_button = tk.Button(

    window,

    text="🎤 Start Listening",

    command=start_listening,

    width=22,

    height=2,

    font=(

        "Segoe UI",

        11

    )

)


listen_button.pack(

    pady=20

)


# ============================================================
# Text area
# ============================================================

text_label = tk.Label(

    window,

    text="Transcription:",

    font=(

        "Segoe UI",

        11,

        "bold"

    )

)


text_label.pack()


# ------------------------------------------------------------
# Text box + scrollbar
# ------------------------------------------------------------

text_frame = tk.Frame(

    window

)


text_frame.pack(

    padx=25,

    pady=10,

    fill="both",

    expand=True

)


text_box = tk.Text(

    text_frame,

    width=70,

    height=17,

    font=(

        "Segoe UI",

        11

    ),

    wrap="word"

)


text_box.pack(

    side="left",

    fill="both",

    expand=True

)


scrollbar = tk.Scrollbar(

    text_frame,

    command=text_box.yview

)


scrollbar.pack(

    side="right",

    fill="y"

)


text_box.config(

    yscrollcommand=scrollbar.set

)


# ============================================================
# Bottom buttons
# ============================================================

button_frame = tk.Frame(

    window

)


button_frame.pack(

    pady=10

)


clear_button = tk.Button(

    button_frame,

    text="Clear",

    command=clear_text,

    width=15,

    height=2

)


clear_button.grid(

    row=0,

    column=0,

    padx=10

)


save_button = tk.Button(

    button_frame,

    text="Save TXT",

    command=save_text,

    width=15,

    height=2

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

    text="Ready."

)


status_label.pack(

    pady=(5, 20)

)


# ============================================================
# Keep window running
# ============================================================

window.mainloop()
