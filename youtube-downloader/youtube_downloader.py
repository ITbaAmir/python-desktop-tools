# ============================================================
# YouTube Downloader
# ============================================================
#
# What this program does:
#
# This program downloads permitted videos using yt-dlp.
#
# Features:
# - MP4 video download
# - MP3 audio download
# - Video quality selection
# - Audio quality selection
# - Very low video quality support
# - Estimated file size before downloading
# - Download progress bar
# - Choose download folder
#
# Required Python library:
#
# py -m pip install -U "yt-dlp[default]"
#
# Required additional programs:
#
# FFmpeg:
# winget install Gyan.FFmpeg
#
# Deno:
# winget install DenoLand.Deno
#
# Check installations with:
#
# ffmpeg -version
# deno --version
#
# IMPORTANT:
# Only download videos you own, have permission to download,
# or are otherwise allowed to download.
# ============================================================


import tkinter as tk

from tkinter import ttk, filedialog, messagebox

import yt_dlp

import threading

import os


# ============================================================
# Global variables
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
# Reset size information
# ============================================================
#
# If format or quality changes, the old file-size estimate
# may no longer be correct.
# ============================================================

def reset_size_info(event=None):

    size_label.config(
        text="Estimated size: Not checked"
    )


# ============================================================
# Format changed
# ============================================================
#
# MP4 shows video resolutions.
# MP3 shows audio bitrates.
# ============================================================

def format_changed(event=None):

    selected_format = format_box.get()

    # --------------------------------------------------------
    # MP4
    # --------------------------------------------------------

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
            "360p",
            "240p",
            "144p",

            "Lowest available"

        ]

        quality_box.set(
            "1080p"
        )

    # --------------------------------------------------------
    # MP3
    # --------------------------------------------------------

    else:

        quality_label.config(
            text="MP3 Quality:"
        )

        quality_box["values"] = [

            "320 kbps",
            "256 kbps",
            "192 kbps",
            "128 kbps",
            "96 kbps",
            "64 kbps"

        ]

        quality_box.set(
            "192 kbps"
        )

    reset_size_info()


# ============================================================
# Format file size
# ============================================================
#
# Converts bytes into KB, MB or GB.
# ============================================================

def format_file_size(size_bytes):

    if not size_bytes:

        return "Unknown"

    size_bytes = float(
        size_bytes
    )

    # Kilobytes
    if size_bytes < 1024 * 1024:

        kb = (
            size_bytes / 1024
        )

        return f"{kb:.1f} KB"

    # Megabytes
    mb = (
        size_bytes
        / (1024 * 1024)
    )

    if mb < 1024:

        return f"{mb:.1f} MB"

    # Gigabytes
    gb = (
        mb / 1024
    )

    return f"{gb:.2f} GB"


# ============================================================
# Get size of one yt-dlp format
# ============================================================
#
# yt-dlp sometimes provides an exact filesize.
#
# If exact filesize is unavailable, filesize_approx may be
# available instead.
# ============================================================

def get_format_size(media_format):

    if not media_format:

        return None

    # Exact size
    size = media_format.get(
        "filesize"
    )

    # Approximate size
    if not size:

        size = media_format.get(
            "filesize_approx"
        )

    # --------------------------------------------------------
    # If yt-dlp does not provide either filesize, estimate
    # from bitrate and video duration.
    # --------------------------------------------------------

    if not size:

        bitrate = media_format.get(
            "tbr"
        )

        duration = media_format.get(
            "duration"
        )

        if bitrate and duration:

            # bitrate is kilobits per second.
            #
            # Convert:
            #
            # kbps -> bits -> bytes
            size = (
                bitrate
                * 1000
                * duration
                / 8
            )

    return size


# ============================================================
# Video format selector
# ============================================================

def get_video_format_selector(quality):

    # --------------------------------------------------------
    # Best available
    # --------------------------------------------------------

    if quality == "Best":

        return (
            "bestvideo+bestaudio/best"
        )

    # --------------------------------------------------------
    # Lowest
    # --------------------------------------------------------
    #
    # Actual smallest format selection is additionally
    # influenced by format_sort below.
    # --------------------------------------------------------

    if quality == "Lowest available":

        return (
            "bestvideo*+bestaudio/best"
        )

    # --------------------------------------------------------
    # Selected resolution
    # --------------------------------------------------------

    height = quality.replace(
        "p",
        ""
    )

    # Choose best video at or below requested resolution.
    #
    # Example:
    #
    # 720p means:
    #
    # highest available video that is not higher than 720p.
    #
    # Then add best audio.
    # --------------------------------------------------------

    return (

        f"bestvideo[height<={height}]"
        f"+bestaudio/"
        f"best[height<={height}]"

    )


# ============================================================
# Create MP4 options
# ============================================================

def get_video_options(quality):

    format_selector = get_video_format_selector(
        quality
    )

    options = {

        "format":
            format_selector,

        "merge_output_format":
            "mp4",

        "outtmpl":
            os.path.join(
                download_folder,
                "%(title)s.%(ext)s"
            ),

        "progress_hooks": [
            progress_hook
                ],

        # Do not download entire playlists accidentally
        "noplaylist":
            True,

        # Use Deno for YouTube's JavaScript challenges
        "js_runtimes": {
            "deno": {}
                }

    }

    # --------------------------------------------------------
    # Lowest available
    # --------------------------------------------------------
    #
    # yt-dlp recommends sorting by size/bitrate/resolution
    # when the goal is the smallest possible download.
    # --------------------------------------------------------

    if quality == "Lowest available":

        options["format_sort"] = [

            "+size",
            "+br",
            "+res",
            "+fps"

        ]

    return options


# ============================================================
# Create MP3 options
# ============================================================

def get_audio_options(quality):

    # Example:
    #
    # "192 kbps"
    #
    # becomes:
    #
    # "192"

    bitrate = quality.split()[0]

    options = {

        # Download best available source audio.
        #
        # FFmpeg converts it afterwards.
        "format":
            "bestaudio/best",

        "outtmpl":
            os.path.join(
                download_folder,
                "%(title)s.%(ext)s"
            ),

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
# Check file size
# ============================================================

def check_size():

    url = url_entry.get().strip()

    # --------------------------------------------------------
    # URL required
    # --------------------------------------------------------

    if not url:

        messagebox.showwarning(

            "Missing URL",

            "Please enter a video URL first."

        )

        return

    # Disable button while checking
    size_button.config(
        state="disabled"
    )

    size_label.config(
        text="Estimated size: Checking..."
    )

    status_label.config(
        text="Reading video information..."
    )

    # Do this in another thread so GUI stays responsive
    threading.Thread(

        target=get_media_size,

        args=(url,),

        daemon=True

    ).start()


# ============================================================
# Download video information without downloading
# ============================================================

def get_media_size(url):

    try:

        selected_format = format_box.get()

        selected_quality = quality_box.get()

        # ----------------------------------------------------
        # Only read information.
        # Nothing gets downloaded here.
        # ----------------------------------------------------

        info_options = {

            "quiet":
                True,

            "no_warnings":
                True,

            "noplaylist":
                True,

            "skip_download":
                True,

            "js_runtimes": {
                "deno": {}
            }

        }

        with yt_dlp.YoutubeDL(
            info_options
        ) as downloader:

            info = downloader.extract_info(

                url,

                download=False

            )

        # ----------------------------------------------------
        # MP3 size
        # ----------------------------------------------------

        if selected_format == "MP3":

            estimated_size = estimate_mp3_size(

                info,

                selected_quality

            )

        # ----------------------------------------------------
        # MP4 size
        # ----------------------------------------------------

        else:

            estimated_size = estimate_mp4_size(

                info,

                selected_quality

            )

        window.after(

            0,

            show_size_result,

            estimated_size

        )

    except Exception as error:

        window.after(

            0,

            size_check_failed,

            str(error)

        )


# ============================================================
# Estimate MP3 size
# ============================================================

def estimate_mp3_size(info, quality):

    duration = info.get(
        "duration"
    )

    if not duration:

        return None

    # Example:
    #
    # "192 kbps"
    #
    # becomes:
    #
    # 192

    bitrate = int(
        quality.split()[0]
    )

    # --------------------------------------------------------
    # Estimated MP3 size:
    #
    # duration in seconds
    # × bitrate in kilobits/second
    # × 1000
    # ÷ 8
    #
    # = bytes
    # --------------------------------------------------------

    size_bytes = (

        duration
        * bitrate
        * 1000
        / 8

    )

    return size_bytes


# ============================================================
# Estimate MP4 size
# ============================================================

def estimate_mp4_size(info, quality):

    formats = info.get(
        "formats",
        []
    )

    video_only_formats = []

    audio_only_formats = []

    combined_formats = []

    # ========================================================
    # Separate available formats
    # ========================================================

    for media_format in formats:

        vcodec = media_format.get(
            "vcodec"
        )

        acodec = media_format.get(
            "acodec"
        )

        has_video = (

            vcodec
            and vcodec != "none"

        )

        has_audio = (

            acodec
            and acodec != "none"

        )

        # Video only
        if has_video and not has_audio:

            video_only_formats.append(
                media_format
            )

        # Audio only
        elif has_audio and not has_video:

            audio_only_formats.append(
                media_format
            )

        # Video + audio together
        elif has_video and has_audio:

            combined_formats.append(
                media_format
            )

    # ========================================================
    # Best available audio
    # ========================================================

    selected_audio = None

    if audio_only_formats:

        selected_audio = max(

            audio_only_formats,

            key=lambda item: (

                item.get("abr")
                or item.get("tbr")
                or 0

            )

        )

    # ========================================================
    # BEST VIDEO
    # ========================================================

    if quality == "Best":

        if video_only_formats:

            selected_video = max(

                video_only_formats,

                key=lambda item: (

                    item.get("height")
                    or 0,

                    item.get("fps")
                    or 0,

                    item.get("tbr")
                    or 0

                )

            )

            video_size = get_format_size(
                selected_video
            )

            audio_size = get_format_size(
                selected_audio
            )

            if video_size:

                return (

                    video_size
                    + (audio_size or 0)

                )

        # Fall back to combined format
        if combined_formats:

            selected_combined = max(

                combined_formats,

                key=lambda item: (

                    item.get("height")
                    or 0,

                    item.get("tbr")
                    or 0

                )

            )

            return get_format_size(
                selected_combined
            )

        return None

    # ========================================================
    # LOWEST AVAILABLE
    # ========================================================

    if quality == "Lowest available":

        possible_files = []

        # ----------------------------------------------------
        # Separate video + audio combinations
        # ----------------------------------------------------

        audio_size = get_format_size(
            selected_audio
        )

        for video in video_only_formats:

            video_size = get_format_size(
                video
            )

            if video_size:

                total_size = (

                    video_size
                    + (audio_size or 0)

                )

                possible_files.append(

                    (
                        total_size,
                        video
                    )

                )

        # ----------------------------------------------------
        # Already combined formats
        # ----------------------------------------------------

        for combined in combined_formats:

            combined_size = get_format_size(
                combined
            )

            if combined_size:

                possible_files.append(

                    (
                        combined_size,
                        combined
                    )

                )

        if possible_files:

            smallest = min(

                possible_files,

                key=lambda item:
                item[0]

            )

            return smallest[0]

        return None

    # ========================================================
    # SPECIFIC RESOLUTION
    # ========================================================

    target_height = int(

        quality.replace(
            "p",
            ""
        )

    )

    # --------------------------------------------------------
    # Video-only streams at or below target resolution
    # --------------------------------------------------------

    usable_video_formats = [

        item

        for item in video_only_formats

        if (

            item.get("height")

            and

            item.get("height")
            <= target_height

        )

    ]

    if usable_video_formats:

        # Choose highest available resolution that does not
        # exceed target.
        selected_video = max(

            usable_video_formats,

            key=lambda item: (

                item.get("height")
                or 0,

                item.get("tbr")
                or 0

            )

        )

        video_size = get_format_size(
            selected_video
        )

        audio_size = get_format_size(
            selected_audio
        )

        if video_size:

            return (

                video_size
                + (audio_size or 0)

            )

    # --------------------------------------------------------
    # Fall back to combined video/audio format
    # --------------------------------------------------------

    usable_combined_formats = [

        item

        for item in combined_formats

        if (

            item.get("height")

            and

            item.get("height")
            <= target_height

        )

    ]

    if usable_combined_formats:

        selected_combined = max(

            usable_combined_formats,

            key=lambda item: (

                item.get("height")
                or 0,

                item.get("tbr")
                or 0

            )

        )

        return get_format_size(
            selected_combined
        )

    return None


# ============================================================
# Show file size
# ============================================================

def show_size_result(size_bytes):

    size_button.config(
        state="normal"
    )

    if size_bytes:

        readable_size = format_file_size(
            size_bytes
        )

        size_label.config(

            text=(
                f"Estimated size: ~{readable_size}"
            )

        )

        status_label.config(
            text="File size estimate ready."
        )

    else:

        size_label.config(
            text="Estimated size: Unknown"
        )

        status_label.config(

            text=(
                "YouTube did not provide enough "
                "information to estimate the size."
            )

        )


# ============================================================
# Size check failed
# ============================================================

def size_check_failed(error):

    size_button.config(
        state="normal"
    )

    size_label.config(
        text="Estimated size: Unknown"
    )

    status_label.config(
        text="Could not check file size."
    )

    messagebox.showerror(

        "Size Check Error",

        f"Could not check the file size:\n\n{error}"

    )


# ============================================================
# Start download
# ============================================================

def start_download():

    url = url_entry.get().strip()

    # URL required
    if not url:

        messagebox.showwarning(

            "Missing URL",

            "Please enter a video URL."

        )

        return

    # Folder required
    if not download_folder:

        messagebox.showwarning(

            "Missing Folder",

            "Please choose a download folder."

        )

        return

    download_button.config(
        state="disabled"
    )

    size_button.config(
        state="disabled"
    )

    progress_bar["value"] = 0

    status_label.config(
        text="Starting download..."
    )

    threading.Thread(

        target=download_media,

        args=(url,),

        daemon=True

    ).start()


# ============================================================
# Actual download
# ============================================================

def download_media(url):

    try:

        selected_format = format_box.get()

        selected_quality = quality_box.get()

        # MP4
        if selected_format == "MP4":

            options = get_video_options(
                selected_quality
            )

        # MP3
        else:

            options = get_audio_options(
                selected_quality
            )

        with yt_dlp.YoutubeDL(
            options
        ) as downloader:

            downloader.download(
                [url]
            )

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
# yt-dlp progress information
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

        # Some downloads only provide an estimated size.
        if total is None:

            total = data.get(
                "total_bytes_estimate"
            )

        if total:

            percent = (

                downloaded
                / total

            ) * 100

            window.after(

                0,

                update_progress,

                percent

            )

        else:

            # We know it is downloading, but not the percentage.
            window.after(

                0,

                status_label.config,

                {
                    "text":
                    "Downloading..."
                }

            )

    # --------------------------------------------------------
    # Raw download finished
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

    # Make sure value cannot exceed 100.
    percent = min(
        100,
        percent
    )

    progress_bar["value"] = percent

    status_label.config(

        text=f"Downloading... {percent:.1f}%"

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

    size_button.config(
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

    size_button.config(
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
# Main window
# ============================================================

window = tk.Tk()


window.title(
    "YouTube Downloader"
)


window.geometry(
    "680x650"
)


window.minsize(
    620,
    610
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


# ============================================================
# Description
# ============================================================

description_label = tk.Label(

    window,

    text=(

        "Download permitted videos as "
        "MP4 video or MP3 audio."

    )

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

    width=68,

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


# Reset size if URL changes.
url_entry.bind(

    "<KeyRelease>",

    reset_size_info

)


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
# Format
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

    width=17

)


format_box.grid(

    row=0,

    column=1,

    padx=10

)


format_box.set(
    "MP4"
)


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
        "360p",
        "240p",
        "144p",

        "Lowest available"

    ],

    state="readonly",

    width=17

)


quality_box.grid(

    row=0,

    column=3,

    padx=10

)


quality_box.set(
    "1080p"
)


quality_box.bind(

    "<<ComboboxSelected>>",

    reset_size_info

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

    wraplength=580

)


folder_label.pack(
    pady=5
)


# ============================================================
# Check File Size
# ============================================================

size_button = tk.Button(

    window,

    text="Check File Size",

    command=check_size,

    width=22,

    height=2

)


size_button.pack(
    pady=(15, 5)
)


size_label = tk.Label(

    window,

    text="Estimated size: Not checked",

    font=(

        "Segoe UI",

        10,

        "bold"

    )

)


size_label.pack(
    pady=5
)


# ============================================================
# Information about estimate
# ============================================================

size_info_label = tk.Label(

    window,

    text=(

        "The displayed size is an estimate and "
        "can differ slightly from the final file."

    ),

    font=(

        "Segoe UI",

        9

    )

)


size_info_label.pack(
    pady=(0, 10)
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
    pady=10
)


# ============================================================
# Progress bar
# ============================================================

progress_bar = ttk.Progressbar(

    window,

    length=520,

    mode="determinate",

    maximum=100

)


progress_bar.pack(
    pady=15
)


# ============================================================
# Status
# ============================================================

status_label = tk.Label(

    window,

    text="Enter a video URL to begin.",

    wraplength=580

)


status_label.pack(
    pady=10
)


# ============================================================
# Keep window open
# ============================================================

window.mainloop()
