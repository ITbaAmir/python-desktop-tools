# ============================================================
# Classic Snake Game
# ============================================================
#
# What this program does:
# This is a classic Snake game.
#
# Rules:
# - Control the snake with the arrow keys.
# - Eat the food to grow longer.
# - Each food gives you points.
# - If the snake hits a wall, the game ends.
# - If the snake hits itself, the game ends.
#
# Features:
# - Score
# - High score
# - Difficulty selection
# - Restart button
#
# Required libraries:
# None.
#
# tkinter and random are included with Python.
#
# Run with:
#
# py snake-game\snake_game.py
# ============================================================


import tkinter as tk
from tkinter import ttk

import random


# ============================================================
# Game settings
# ============================================================

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

CELL_SIZE = 20


# Number of cells across the board
GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE

GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE


# ============================================================
# Difficulty settings
#
# Smaller number = faster snake
# ============================================================

DIFFICULTIES = {

    "Easy": 150,
    "Normal": 100,
    "Hard": 70,
    "Very Hard": 45

}


# ============================================================
# Game variables
# ============================================================

snake = []

food = None

direction = "Right"

next_direction = "Right"

score = 0

high_score = 0

game_running = False

game_over = False

game_job = None


# ============================================================
# Start / restart game
# ============================================================

def start_game():

    global snake
    global food

    global direction
    global next_direction

    global score

    global game_running
    global game_over

    global game_job

    # Cancel previous scheduled game loop
    if game_job is not None:

        try:

            window.after_cancel(
                game_job
            )

        except Exception:

            pass

    # Clear the board
    canvas.delete(
        "all"
    )

    # Reset score
    score = 0

    update_score()

    # Start snake in the middle of the board
    center_x = GRID_WIDTH // 2

    center_y = GRID_HEIGHT // 2

    snake = [

        (center_x, center_y),

        (center_x - 1, center_y),

        (center_x - 2, center_y)

    ]

    direction = "Right"

    next_direction = "Right"

    game_running = True

    game_over = False

    status_label.config(
        text="Use the arrow keys to move."
    )

    # Create first food
    create_food()

    # Draw everything
    draw_game()

    # Start game loop
    game_loop()


# ============================================================
# Create food
# ============================================================

def create_food():

    global food

    # Find positions that are not occupied by the snake
    available_positions = []

    for x in range(
        GRID_WIDTH
    ):

        for y in range(
            GRID_HEIGHT
        ):

            position = (
                x,
                y
            )

            if position not in snake:

                available_positions.append(
                    position
                )

    # If no free space exists, the player filled the board
    if not available_positions:

        end_game(
            "You filled the entire board!"
        )

        return

    food = random.choice(
        available_positions
    )


# ============================================================
# Draw game
# ============================================================

def draw_game():

    canvas.delete(
        "all"
    )

    # --------------------------------------------------------
    # Draw snake
    # --------------------------------------------------------

    for index, segment in enumerate(
        snake
    ):

        x, y = segment

        x1 = x * CELL_SIZE

        y1 = y * CELL_SIZE

        x2 = x1 + CELL_SIZE

        y2 = y1 + CELL_SIZE

        # Snake head is slightly different
        if index == 0:

            fill_color = "#2e8b57"

        else:

            fill_color = "#3cb371"

        canvas.create_rectangle(

            x1,
            y1,
            x2,
            y2,

            fill=fill_color,

            outline="#1f5f3d"

        )

    # --------------------------------------------------------
    # Draw food
    # --------------------------------------------------------

    if food is not None:

        food_x, food_y = food

        x1 = food_x * CELL_SIZE

        y1 = food_y * CELL_SIZE

        x2 = x1 + CELL_SIZE

        y2 = y1 + CELL_SIZE

        canvas.create_oval(

            x1 + 2,
            y1 + 2,

            x2 - 2,
            y2 - 2,

            fill="#d9534f",

            outline="#8b0000"

        )


# ============================================================
# Change direction
# ============================================================

def change_direction(new_direction):

    global next_direction

    if not game_running:

        return

    # Prevent the snake from instantly reversing direction.
    #
    # Example:
    # If moving Right, pressing Left would make the snake
    # immediately collide with itself.
    opposite_directions = {

        "Up": "Down",

        "Down": "Up",

        "Left": "Right",

        "Right": "Left"

    }

    if new_direction != opposite_directions[
        direction
    ]:

        next_direction = new_direction


# ============================================================
# Keyboard controls
# ============================================================

def key_pressed(event):

    key = event.keysym

    if key == "Up":

        change_direction(
            "Up"
        )

    elif key == "Down":

        change_direction(
            "Down"
        )

    elif key == "Left":

        change_direction(
            "Left"
        )

    elif key == "Right":

        change_direction(
            "Right"
        )

    # W A S D also work
    elif key.lower() == "w":

        change_direction(
            "Up"
        )

    elif key.lower() == "s":

        change_direction(
            "Down"
        )

    elif key.lower() == "a":

        change_direction(
            "Left"
        )

    elif key.lower() == "d":

        change_direction(
            "Right"
        )

    # Space can restart after game over
    elif key == "space":

        if game_over:

            start_game()


# ============================================================
# Game loop
# ============================================================

def game_loop():

    global direction
    global snake

    global score
    global high_score

    global game_job

    if not game_running:

        return

    direction = next_direction

    # Current snake head
    head_x, head_y = snake[0]

    # --------------------------------------------------------
    # Calculate new head position
    # --------------------------------------------------------

    if direction == "Up":

        head_y -= 1

    elif direction == "Down":

        head_y += 1

    elif direction == "Left":

        head_x -= 1

    elif direction == "Right":

        head_x += 1

    new_head = (
        head_x,
        head_y
    )

    # ========================================================
    # Wall collision
    # ========================================================

    if (
        head_x < 0
        or head_x >= GRID_WIDTH
        or head_y < 0
        or head_y >= GRID_HEIGHT
    ):

        end_game(
            "You hit the wall!"
        )

        return

    # ========================================================
    # Self collision
    # ========================================================

    if new_head in snake:

        end_game(
            "The snake hit itself!"
        )

        return

    # Add new head
    snake.insert(
        0,
        new_head
    )

    # ========================================================
    # Food collision
    # ========================================================

    if new_head == food:

        score += 10

        if score > high_score:

            high_score = score

        update_score()

        # Snake does NOT lose its tail here,
        # so it becomes one block longer.
        create_food()

    else:

        # Remove last snake block.
        #
        # This makes the snake appear to move forward.
        snake.pop()

    # Redraw everything
    draw_game()

    # Get selected game speed
    delay = DIFFICULTIES[
        difficulty_box.get()
    ]

    # Schedule next movement
    game_job = window.after(
        delay,
        game_loop
    )


# ============================================================
# Update score
# ============================================================

def update_score():

    score_label.config(

        text=f"Score: {score}"

    )

    high_score_label.config(

        text=f"High Score: {high_score}"

    )


# ============================================================
# Game over
# ============================================================

def end_game(reason):

    global game_running
    global game_over

    game_running = False

    game_over = True

    status_label.config(

        text=(
            f"{reason}  "
            "Press Restart or Space."
        )

    )

    # Draw game over message over the board
    canvas.create_rectangle(

        120,
        245,

        480,
        355,

        fill="black",

        stipple="gray50"

    )

    canvas.create_text(

        WINDOW_WIDTH // 2,

        275,

        text="GAME OVER",

        font=(
            "Segoe UI",
            28,
            "bold"
        ),

        fill="white"

    )

    canvas.create_text(

        WINDOW_WIDTH // 2,

        320,

        text=f"Score: {score}",

        font=(
            "Segoe UI",
            16
        ),

        fill="white"

    )


# ============================================================
# Main window
# ============================================================

window = tk.Tk()


window.title(
    "Classic Snake"
)


window.resizable(
    False,
    False
)


# ============================================================
# Top section
# ============================================================

top_frame = tk.Frame(
    window
)


top_frame.pack(
    pady=(10, 5)
)


# ------------------------------------------------------------
# Score
# ------------------------------------------------------------

score_label = tk.Label(

    top_frame,

    text="Score: 0",

    font=(
        "Segoe UI",
        12,
        "bold"
    )

)


score_label.grid(

    row=0,
    column=0,

    padx=20

)


# ------------------------------------------------------------
# High score
# ------------------------------------------------------------

high_score_label = tk.Label(

    top_frame,

    text="High Score: 0",

    font=(
        "Segoe UI",
        12,
        "bold"
    )

)


high_score_label.grid(

    row=0,
    column=1,

    padx=20

)


# ------------------------------------------------------------
# Difficulty
# ------------------------------------------------------------

difficulty_label = tk.Label(

    top_frame,

    text="Difficulty:"

)


difficulty_label.grid(

    row=0,
    column=2,

    padx=(20, 5)

)


difficulty_box = ttk.Combobox(

    top_frame,

    values=[

        "Easy",
        "Normal",
        "Hard",
        "Very Hard"

    ],

    state="readonly",

    width=12

)


difficulty_box.grid(

    row=0,
    column=3,

    padx=5

)


difficulty_box.set(
    "Normal"
)


# ============================================================
# Game canvas
# ============================================================

canvas = tk.Canvas(

    window,

    width=WINDOW_WIDTH,

    height=WINDOW_HEIGHT,

    background="#202020",

    highlightthickness=2,

    highlightbackground="#555555"

)


canvas.pack(
    padx=15,
    pady=10
)


# ============================================================
# Bottom controls
# ============================================================

bottom_frame = tk.Frame(
    window
)


bottom_frame.pack(
    pady=(0, 10)
)


restart_button = tk.Button(

    bottom_frame,

    text="Restart",

    command=start_game,

    width=15,

    height=2

)


restart_button.grid(

    row=0,
    column=0,

    padx=10

)


status_label = tk.Label(

    bottom_frame,

    text="Use the arrow keys to move.",

    width=40

)


status_label.grid(

    row=0,
    column=1,

    padx=10

)


# ============================================================
# Keyboard input
# ============================================================

window.bind(
    "<KeyPress>",
    key_pressed
)


# ============================================================
# Start first game
# ============================================================

start_game()


# Make sure keyboard input goes to this window
window.focus_force()


# ============================================================
# Keep program running
# ============================================================

window.mainloop()
