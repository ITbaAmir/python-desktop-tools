# ============================================================
# Stopwatch + Timer
# ============================================================
#
# What this program does:
# This program combines two useful tools in one window:
#
# 1. Stopwatch
#    - Start
#    - Pause
#    - Reset
#    - Lap times
#
# 2. Timer
#    - Set hours, minutes and seconds
#    - Start
#    - Pause
#    - Reset
#    - Shows a popup when the timer reaches zero
#
# Required libraries:
# None.
#
# tkinter and time are included with Python.
#
# Run with:
#
# py stopwatch-timer\stopwatch_timer.py
# ============================================================


import tkinter as tk
from tkinter import ttk, messagebox

import time


# ============================================================
# Main window
# ============================================================

window = tk.Tk()

window.title("Stopwatch + Timer")

window.geometry("650x600")
window.minsize(600, 550)


# ============================================================
# Create tabs
# ============================================================

tabs = ttk.Notebook(window)

tabs.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=15
)


# Stopwatch tab
stopwatch_tab = tk.Frame(tabs)

tabs.add(
    stopwatch_tab,
    text="Stopwatch"
)


# Timer tab
timer_tab = tk.Frame(tabs)

tabs.add(
    timer_tab,
    text="Timer"
)


# ============================================================
# STOPWATCH
# ============================================================


# ------------------------------------------------------------
# Stopwatch variables
# ------------------------------------------------------------

stopwatch_running = False

stopwatch_start_time = 0

stopwatch_elapsed_before_pause = 0

lap_number = 0


# ------------------------------------------------------------
# Format stopwatch time
#
# Example:
# 65.32 seconds
#
# becomes:
#
# 00:01:05.32
# ------------------------------------------------------------

def format_stopwatch_time(seconds):

    hours = int(
        seconds // 3600
    )

    minutes = int(
        (seconds % 3600) // 60
    )

    secs = int(
        seconds % 60
    )

    hundredths = int(
        (seconds - int(seconds)) * 100
    )

    return (
        f"{hours:02}:"
        f"{minutes:02}:"
        f"{secs:02}."
        f"{hundredths:02}"
    )


# ------------------------------------------------------------
# Update stopwatch
# ------------------------------------------------------------

def update_stopwatch():

    if stopwatch_running:

        current_time = time.perf_counter()

        elapsed = (
            stopwatch_elapsed_before_pause
            + current_time
            - stopwatch_start_time
        )

        stopwatch_display.config(
            text=format_stopwatch_time(elapsed)
        )

        # Update again after 50 milliseconds
        window.after(
            50,
            update_stopwatch
        )


# ------------------------------------------------------------
# Start stopwatch
# ------------------------------------------------------------

def start_stopwatch():

    global stopwatch_running
    global stopwatch_start_time

    # Do nothing if it is already running
    if stopwatch_running:
        return

    stopwatch_running = True

    stopwatch_start_time = time.perf_counter()

    stopwatch_status.config(
        text="Running..."
    )

    update_stopwatch()


# ------------------------------------------------------------
# Pause stopwatch
# ------------------------------------------------------------

def pause_stopwatch():

    global stopwatch_running
    global stopwatch_elapsed_before_pause

    if not stopwatch_running:
        return

    current_time = time.perf_counter()

    stopwatch_elapsed_before_pause += (
        current_time
        - stopwatch_start_time
    )

    stopwatch_running = False

    stopwatch_status.config(
        text="Paused"
    )


# ------------------------------------------------------------
# Reset stopwatch
# ------------------------------------------------------------

def reset_stopwatch():

    global stopwatch_running
    global stopwatch_start_time
    global stopwatch_elapsed_before_pause
    global lap_number

    stopwatch_running = False

    stopwatch_start_time = 0

    stopwatch_elapsed_before_pause = 0

    lap_number = 0

    stopwatch_display.config(
        text="00:00:00.00"
    )

    stopwatch_status.config(
        text="Ready"
    )

    # Remove all lap times
    lap_listbox.delete(
        0,
        tk.END
    )


# ------------------------------------------------------------
# Get current stopwatch time
# ------------------------------------------------------------

def get_current_stopwatch_time():

    if stopwatch_running:

        return (
            stopwatch_elapsed_before_pause
            + time.perf_counter()
            - stopwatch_start_time
        )

    return stopwatch_elapsed_before_pause


# ------------------------------------------------------------
# Add lap time
# ------------------------------------------------------------

def add_lap():

    global lap_number

    current_time = get_current_stopwatch_time()

    # Do not create a lap at exactly zero
    if current_time <= 0:
        return

    lap_number += 1

    lap_text = (
        f"Lap {lap_number}: "
        f"{format_stopwatch_time(current_time)}"
    )

    lap_listbox.insert(
        tk.END,
        lap_text
    )

    # Scroll automatically to newest lap
    lap_listbox.see(
        tk.END
    )


# ============================================================
# STOPWATCH INTERFACE
# ============================================================

stopwatch_title = tk.Label(
    stopwatch_tab,
    text="Stopwatch",
    font=("Segoe UI", 20, "bold")
)

stopwatch_title.pack(
    pady=(25, 15)
)


stopwatch_display = tk.Label(
    stopwatch_tab,
    text="00:00:00.00",
    font=("Consolas", 34, "bold")
)

stopwatch_display.pack(
    pady=15
)


# ------------------------------------------------------------
# Stopwatch buttons
# ------------------------------------------------------------

stopwatch_buttons = tk.Frame(
    stopwatch_tab
)

stopwatch_buttons.pack(
    pady=10
)


start_stopwatch_button = tk.Button(
    stopwatch_buttons,
    text="Start",
    command=start_stopwatch,
    width=11,
    height=2
)

start_stopwatch_button.grid(
    row=0,
    column=0,
    padx=5
)


pause_stopwatch_button = tk.Button(
    stopwatch_buttons,
    text="Pause",
    command=pause_stopwatch,
    width=11,
    height=2
)

pause_stopwatch_button.grid(
    row=0,
    column=1,
    padx=5
)


lap_button = tk.Button(
    stopwatch_buttons,
    text="Lap",
    command=add_lap,
    width=11,
    height=2
)

lap_button.grid(
    row=0,
    column=2,
    padx=5
)


reset_stopwatch_button = tk.Button(
    stopwatch_buttons,
    text="Reset",
    command=reset_stopwatch,
    width=11,
    height=2
)

reset_stopwatch_button.grid(
    row=0,
    column=3,
    padx=5
)


# ------------------------------------------------------------
# Lap list
# ------------------------------------------------------------

lap_label = tk.Label(
    stopwatch_tab,
    text="Lap Times:",
    font=("Segoe UI", 11, "bold")
)

lap_label.pack(
    pady=(20, 5)
)


lap_listbox = tk.Listbox(
    stopwatch_tab,
    width=45,
    height=10,
    font=("Consolas", 11)
)

lap_listbox.pack(
    pady=5
)


stopwatch_status = tk.Label(
    stopwatch_tab,
    text="Ready"
)

stopwatch_status.pack(
    pady=10
)


# ============================================================
# TIMER
# ============================================================


# ------------------------------------------------------------
# Timer variables
# ------------------------------------------------------------

timer_running = False

timer_remaining_seconds = 0

timer_end_time = 0


# ------------------------------------------------------------
# Format timer time
# ------------------------------------------------------------

def format_timer_time(seconds):

    # Prevent negative numbers
    seconds = max(
        0,
        int(seconds)
    )

    hours = seconds // 3600

    minutes = (
        seconds % 3600
    ) // 60

    secs = seconds % 60

    return (
        f"{hours:02}:"
        f"{minutes:02}:"
        f"{secs:02}"
    )


# ------------------------------------------------------------
# Read timer input
# ------------------------------------------------------------

def get_timer_input():

    try:

        hours = int(
            hours_entry.get() or 0
        )

        minutes = int(
            minutes_entry.get() or 0
        )

        seconds = int(
            seconds_entry.get() or 0
        )

    except ValueError:

        messagebox.showerror(
            "Invalid Time",
            "Please enter whole numbers only."
        )

        return None

    # Negative values are not allowed
    if (
        hours < 0
        or minutes < 0
        or seconds < 0
    ):

        messagebox.showerror(
            "Invalid Time",
            "Time cannot be negative."
        )

        return None

    # Make minute / second fields normal
    if minutes > 59 or seconds > 59:

        messagebox.showwarning(
            "Invalid Time",
            "Minutes and seconds should be between 0 and 59."
        )

        return None

    total_seconds = (
        hours * 3600
        + minutes * 60
        + seconds
    )

    return total_seconds


# ------------------------------------------------------------
# Start timer
# ------------------------------------------------------------

def start_timer():

    global timer_running
    global timer_remaining_seconds
    global timer_end_time

    if timer_running:
        return

    # If the timer has no paused time stored,
    # read the values from the input boxes.
    if timer_remaining_seconds <= 0:

        selected_time = get_timer_input()

        if selected_time is None:
            return

        if selected_time == 0:

            messagebox.showwarning(
                "No Time",
                "Please enter a timer duration."
            )

            return

        timer_remaining_seconds = selected_time

    timer_running = True

    timer_end_time = (
        time.monotonic()
        + timer_remaining_seconds
    )

    timer_status.config(
        text="Running..."
    )

    update_timer()


# ------------------------------------------------------------
# Update timer
# ------------------------------------------------------------

def update_timer():

    global timer_running
    global timer_remaining_seconds

    if not timer_running:
        return

    remaining = (
        timer_end_time
        - time.monotonic()
    )

    # Timer finished
    if remaining <= 0:

        timer_running = False

        timer_remaining_seconds = 0

        timer_display.config(
            text="00:00:00"
        )

        timer_status.config(
            text="Time is up!"
        )

        # Windows notification sound
        try:
            window.bell()
        except Exception:
            pass

        messagebox.showinfo(
            "Timer Finished",
            "Time is up!"
        )

        return

    timer_remaining_seconds = remaining

    timer_display.config(
        text=format_timer_time(remaining)
    )

    window.after(
        200,
        update_timer
    )


# ------------------------------------------------------------
# Pause timer
# ------------------------------------------------------------

def pause_timer():

    global timer_running
    global timer_remaining_seconds

    if not timer_running:
        return

    timer_remaining_seconds = max(
        0,
        timer_end_time
        - time.monotonic()
    )

    timer_running = False

    timer_display.config(
        text=format_timer_time(
            timer_remaining_seconds
        )
    )

    timer_status.config(
        text="Paused"
    )


# ------------------------------------------------------------
# Reset timer
# ------------------------------------------------------------

def reset_timer():

    global timer_running
    global timer_remaining_seconds
    global timer_end_time

    timer_running = False

    timer_remaining_seconds = 0

    timer_end_time = 0

    timer_display.config(
        text="00:00:00"
    )

    timer_status.config(
        text="Ready"
    )


# ------------------------------------------------------------
# Clear timer input fields
# ------------------------------------------------------------

def clear_timer_inputs():

    hours_entry.delete(
        0,
        tk.END
    )

    minutes_entry.delete(
        0,
        tk.END
    )

    seconds_entry.delete(
        0,
        tk.END
    )

    hours_entry.insert(
        0,
        "0"
    )

    minutes_entry.insert(
        0,
        "0"
    )

    seconds_entry.insert(
        0,
        "0"
    )


# ============================================================
# TIMER INTERFACE
# ============================================================

timer_title = tk.Label(
    timer_tab,
    text="Countdown Timer",
    font=("Segoe UI", 20, "bold")
)

timer_title.pack(
    pady=(25, 15)
)


timer_display = tk.Label(
    timer_tab,
    text="00:00:00",
    font=("Consolas", 34, "bold")
)

timer_display.pack(
    pady=15
)


# ------------------------------------------------------------
# Timer input area
# ------------------------------------------------------------

timer_input_frame = tk.Frame(
    timer_tab
)

timer_input_frame.pack(
    pady=15
)


# Hours
hours_label = tk.Label(
    timer_input_frame,
    text="Hours"
)

hours_label.grid(
    row=0,
    column=0,
    padx=10
)


hours_entry = tk.Entry(
    timer_input_frame,
    width=8,
    justify="center",
    font=("Segoe UI", 12)
)

hours_entry.grid(
    row=1,
    column=0,
    padx=10,
    pady=5
)

hours_entry.insert(
    0,
    "0"
)


# Minutes
minutes_label = tk.Label(
    timer_input_frame,
    text="Minutes"
)

minutes_label.grid(
    row=0,
    column=1,
    padx=10
)


minutes_entry = tk.Entry(
    timer_input_frame,
    width=8,
    justify="center",
    font=("Segoe UI", 12)
)

minutes_entry.grid(
    row=1,
    column=1,
    padx=10,
    pady=5
)

minutes_entry.insert(
    0,
    "0"
)


# Seconds
seconds_label = tk.Label(
    timer_input_frame,
    text="Seconds"
)

seconds_label.grid(
    row=0,
    column=2,
    padx=10
)


seconds_entry = tk.Entry(
    timer_input_frame,
    width=8,
    justify="center",
    font=("Segoe UI", 12)
)

seconds_entry.grid(
    row=1,
    column=2,
    padx=10,
    pady=5
)

seconds_entry.insert(
    0,
    "0"
)


# ------------------------------------------------------------
# Timer buttons
# ------------------------------------------------------------

timer_buttons = tk.Frame(
    timer_tab
)

timer_buttons.pack(
    pady=20
)


start_timer_button = tk.Button(
    timer_buttons,
    text="Start",
    command=start_timer,
    width=12,
    height=2
)

start_timer_button.grid(
    row=0,
    column=0,
    padx=5
)


pause_timer_button = tk.Button(
    timer_buttons,
    text="Pause",
    command=pause_timer,
    width=12,
    height=2
)

pause_timer_button.grid(
    row=0,
    column=1,
    padx=5
)


reset_timer_button = tk.Button(
    timer_buttons,
    text="Reset",
    command=reset_timer,
    width=12,
    height=2
)

reset_timer_button.grid(
    row=0,
    column=2,
    padx=5
)


clear_timer_button = tk.Button(
    timer_buttons,
    text="Clear",
    command=clear_timer_inputs,
    width=12,
    height=2
)

clear_timer_button.grid(
    row=0,
    column=3,
    padx=5
)


timer_status = tk.Label(
    timer_tab,
    text="Ready"
)

timer_status.pack(
    pady=15
)


# ============================================================
# Keep program open
# ============================================================

window.mainloop()
