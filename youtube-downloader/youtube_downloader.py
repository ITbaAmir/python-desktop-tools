# ============================================================
# YouTube Downloader
# ============================================================
#
# What this program does:
# This program downloads videos using yt-dlp.
#
# You can choose:
# - MP4 video
# - MP3 audio
# - Video quality
# - MP3 audio quality
# - Download folder
#
# Required Python library:
#
#! pip install -U "yt-dlp[default]"
#! winget install DenoLand.Deno
#! pip install -U yt-dlp
#
# You also need FFmpeg installed on Windows.
#
# FFmpeg is required for:
# - Combining high-quality video + audio
# - Creating MP3 files
#
# IMPORTANT:
# Only download videos you own, have permission to download,
# or are otherwise allowed to download.
# ============================================================


import tkinter as tk

# ttk gives us dropdown menus and the progress bar
from tkinter import ttk, filedialog, messagebox

# yt_dlp does the actual downloading
import yt_dlp

# threading keeps the window responsive during downloads
import threading

# os is used for folder paths
import os


# ============================================================
# Variables
# ============================================================

download_folder = ""


# ============================================================
# Choose download folder
# ============================================================

def choose_folder():

    global download_folder

    folder = filedialog.askdirectory(
        title="Choose Download Folder"
    )

    if not folder:
        return

    download_folder = folder

    folder_label.config(
        text=folder
    )

    status_label.config(
        text="Download folder selected."
    )


# ============================================================
# Format changed
#
# If MP4 is selected, show video quality.
# If MP3 is selected, show audio quality.
# ============================================================

def format_changed(event=None):

    selected_format = format_box.get()

    if selected_format == "MP4":

        quality_label.config(
            text="Video Quality:"
        )

        quality_box["values"] = [
            "Best",
            "2160p",
            "1440p",
            "1080p",
            "720p",
            "480p",
            "360p"
        ]

        quality_box.set(
            "1080p"
        )

    else:

        quality_label.config(
            text="MP3 Quality:"
        )

        quality_box["values"] = [
            "320 kbps",
            "256 kbps",
            "192 kbps",
            "128 kbps"
        ]

        quality_box.set(
            "192 kbps"
        )


# ============================================================
# Download button
# ============================================================

def start_download():

    url = url_entry.get().strip()

    # Make sure a URL was entered
    if not url:

        messagebox.showwarning(
            "Missing URL",
            "Please enter a video URL."
        )

        return

    # Make sure a download folder was selected
    if not download_folder:

        messagebox.showwarning(
            "Missing Folder",
            "Please choose a download folder."
        )

        return

    # Disable the button during the download
    download_button.config(
        state="disabled"
    )

    progress_bar["value"] = 0

    status_label.config(
        text="Starting download..."
    )

    # Run download in another thread
    threading.Thread(
        target=download_media,
        args=(url,),
        daemon=True
    ).start()


# ============================================================
# Progress information from yt-dlp
# ============================================================

def progress_hook(data):

    status = data.get(
        "status"
    )

    # --------------------------------------------------------
    # Downloading
    # --------------------------------------------------------

    if status == "downloading":

        downloaded = data.get(
            "downloaded_bytes",
            0
        )

        total = data.get(
            "total_bytes"
        )

        # Some videos only provide an estimated total size
        if total is None:

            total = data.get(
                "total_bytes_estimate"
            )

        if total:

            percent = (
                downloaded / total
            ) * 100

            # Update GUI safely
            window.after(
                0,
                update_progress,
                percent
            )

    # --------------------------------------------------------
    # yt-dlp finished downloading the raw file
    # --------------------------------------------------------

    elif status == "finished":

        window.after(
            0,
            status_label.config,
            {
                "text":
                "Download finished. Processing file..."
            }
        )


# ============================================================
# Update progress bar
# ============================================================

def update_progress(percent):

    progress_bar["value"] = percent

    status_label.config(
        text=f"Downloading... {percent:.1f}%"
    )


# ============================================================
# Create MP4 options
# ============================================================

def get_video_options(quality):

    # --------------------------------------------------------
    # Best available
    # --------------------------------------------------------

    if quality == "Best":

        format_selector = (
            "bestvideo+bestaudio/best"
        )

    else:

        # Remove the "p"
        #
        # Example:
        # 1080p becomes 1080

        height = quality.replace(
            "p",
            ""
        )

        # Choose the best video that does not exceed
        # the selected resolution.
        #
        # Then combine it with the best audio.
        #
        # If separate streams are unavailable,
        # use the best combined format instead.

        format_selector = (
            f"bestvideo[height<={height}]"
            f"+bestaudio/"
            f"best[height<={height}]"
        )

    options = {

        "format":
            format_selector,

        # Ask FFmpeg to create an MP4 container
        "merge_output_format":
            "mp4",

        # File name:
        #
        # Video Title.mp4

        "outtmpl":
            os.path.join(
                download_folder,
                "%(title)s.%(ext)s"
            ),

        # Send progress information to our function
        "progress_hooks": [
            progress_hook
        ],

        # Avoid downloading playlists accidentally
        "noplaylist":
            True,

        "js_runtimes": {
            "deno": {}
        }
    }

    return options


# ============================================================
# Create MP3 options
# ============================================================

def get_audio_options(quality):

    # Extract just the number
    #
    # Example:
    # "192 kbps" becomes "192"

    bitrate = quality.split()[0]

    options = {

        # Download the best available audio
        "format":
            "bestaudio/best",

        "outtmpl":
            os.path.join(
                download_folder,
                "%(title)s.%(ext)s"
            ),

        # FFmpeg converts the downloaded audio to MP3
        "postprocessors": [

            {
                "key":
                    "FFmpegExtractAudio",

                "preferredcodec":
                    "mp3",

                "preferredquality":
                    bitrate
            }

        ],


        "progress_hooks": [
            progress_hook
        ],

        "noplaylist":
            True,

        "js_runtimes": {
            "deno": {}
                }
    }

    return options


# ============================================================
# Actual download
# ============================================================

def download_media(url):

    try:

        selected_format = format_box.get()

        quality = quality_box.get()

        # ----------------------------------------------------
        # MP4
        # ----------------------------------------------------

        if selected_format == "MP4":

            options = get_video_options(
                quality
            )

        # ----------------------------------------------------
        # MP3
        # ----------------------------------------------------

        else:

            options = get_audio_options(
                quality
            )

        # Create yt-dlp downloader
        with yt_dlp.YoutubeDL(
            options
        ) as downloader:

            # Download the URL
            downloader.download(
                [url]
            )

        # Run success function in the GUI thread
        window.after(
            0,
            download_finished
        )

    except Exception as error:

        window.after(
            0,
            download_failed,
            str(error)
        )


# ============================================================
# Download finished
# ============================================================

def download_finished():

    progress_bar["value"] = 100

    status_label.config(
        text="Download completed successfully!"
    )

    download_button.config(
        state="normal"
    )

    messagebox.showinfo(
        "Finished",
        "Your download has finished successfully!"
    )


# ============================================================
# Download error
# ============================================================

def download_failed(error):

    download_button.config(
        state="normal"
    )

    status_label.config(
        text="Download failed."
    )

    messagebox.showerror(
        "Download Error",
        f"Could not download the file:\n\n{error}"
    )


# ============================================================
# Create main window
# ============================================================

window = tk.Tk()

window.title(
    "YouTube Downloader"
)

window.geometry(
    "650x520"
)

window.minsize(
    600,
    500
)


# ============================================================
# Title
# ============================================================

title_label = tk.Label(
    window,
    text="YouTube Downloader",
    font=(
        "Segoe UI",
        18,
        "bold"
    )
)

title_label.pack(
    pady=(20, 5)
)


description_label = tk.Label(
    window,
    text="Download permitted videos as MP4 video or MP3 audio."
)

description_label.pack(
    pady=(0, 20)
)


# ============================================================
# URL
# ============================================================

url_label = tk.Label(
    window,
    text="Video URL:"
)

url_label.pack()


url_entry = tk.Entry(
    window,
    width=65,
    font=(
        "Segoe UI",
        11
    )
)

url_entry.pack(
    padx=20,
    pady=8
)

url_entry.focus()


# ============================================================
# Format settings
# ============================================================

settings_frame = tk.Frame(
    window
)

settings_frame.pack(
    pady=15
)


# ------------------------------------------------------------
# MP4 / MP3
# ------------------------------------------------------------

format_label = tk.Label(
    settings_frame,
    text="Format:"
)

format_label.grid(
    row=0,
    column=0,
    padx=10,
    pady=5
)


format_box = ttk.Combobox(
    settings_frame,
    values=[
        "MP4",
        "MP3"
    ],
    state="readonly",
    width=15
)

format_box.grid(
    row=0,
    column=1,
    padx=10
)

format_box.set(
    "MP4"
)


# Run format_changed whenever MP4/MP3 changes
format_box.bind(
    "<<ComboboxSelected>>",
    format_changed
)


# ------------------------------------------------------------
# Quality
# ------------------------------------------------------------

quality_label = tk.Label(
    settings_frame,
    text="Video Quality:"
)

quality_label.grid(
    row=0,
    column=2,
    padx=10
)


quality_box = ttk.Combobox(
    settings_frame,
    values=[
        "Best",
        "2160p",
        "1440p",
        "1080p",
        "720p",
        "480p",
        "360p"
    ],
    state="readonly",
    width=15
)

quality_box.grid(
    row=0,
    column=3,
    padx=10
)

quality_box.set(
    "1080p"
)


# ============================================================
# Download folder
# ============================================================

folder_button = tk.Button(
    window,
    text="Choose Download Folder",
    command=choose_folder,
    width=25,
    height=2
)

folder_button.pack(
    pady=10
)


folder_label = tk.Label(
    window,
    text="No folder selected",
    wraplength=550
)

folder_label.pack(
    pady=5
)


# ============================================================
# Download button
# ============================================================

download_button = tk.Button(
    window,
    text="Download",
    command=start_download,
    width=22,
    height=2
)

download_button.pack(
    pady=15
)


# ============================================================
# Progress bar
# ============================================================

progress_bar = ttk.Progressbar(
    window,
    length=500,
    mode="determinate",
    maximum=100
)

progress_bar.pack(
    pady=10
)


# ============================================================
# Status
# ============================================================

status_label = tk.Label(
    window,
    text="Enter a video URL to begin."
)

status_label.pack(
    pady=10
)


# ============================================================
# Keep window open
# ============================================================

window.mainloop()
