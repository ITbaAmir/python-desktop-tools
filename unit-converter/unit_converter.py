# ============================================================
# Unit Converter
# ============================================================
#
# What this program does:
# This program converts between commonly used units.
#
# Supported categories:
# - Length
# - Weight / Mass
# - Temperature
# - Area
# - Volume
# - Speed
# - Time
# - Data Storage
# - Pressure
# - Energy
#
# Required libraries:
# None.
#
# tkinter is included with normal Python installations.
#
# Run with:
#
# py unit-converter\unit_converter.py
# ============================================================


import tkinter as tk
from tkinter import ttk, messagebox


# ============================================================
# Conversion information
# ============================================================
#
# For most categories we convert the entered value into one
# common "base unit" and then convert it to the target unit.
#
# Example:
#
# Length uses meters as the base unit.
#
# Kilometers -> meters -> miles
#
# Temperature is handled separately because Celsius,
# Fahrenheit and Kelvin need special formulas.
# ============================================================


CONVERSIONS = {

    # --------------------------------------------------------
    # Length
    # Base unit: Meter
    # --------------------------------------------------------

    "Length": {

        "Meter (m)": 1,
        "Kilometer (km)": 1000,
        "Centimeter (cm)": 0.01,
        "Millimeter (mm)": 0.001,

        "Mile (mi)": 1609.344,
        "Yard (yd)": 0.9144,
        "Foot (ft)": 0.3048,
        "Inch (in)": 0.0254
    },


    # --------------------------------------------------------
    # Weight / Mass
    # Base unit: Kilogram
    # --------------------------------------------------------

    "Weight / Mass": {

        "Kilogram (kg)": 1,
        "Gram (g)": 0.001,
        "Milligram (mg)": 0.000001,
        "Metric Ton (t)": 1000,

        "Pound (lb)": 0.45359237,
        "Ounce (oz)": 0.028349523125,
        "Stone (st)": 6.35029318
    },


    # --------------------------------------------------------
    # Area
    # Base unit: Square Meter
    # --------------------------------------------------------

    "Area": {

        "Square Meter (m²)": 1,

        "Square Kilometer (km²)": 1_000_000,

        "Square Centimeter (cm²)": 0.0001,

        "Square Millimeter (mm²)": 0.000001,

        "Hectare (ha)": 10_000,

        "Acre": 4046.8564224,

        "Square Mile (mi²)": 2_589_988.110336,

        "Square Foot (ft²)": 0.09290304,

        "Square Inch (in²)": 0.00064516
    },


    # --------------------------------------------------------
    # Volume
    # Base unit: Liter
    # --------------------------------------------------------

    "Volume": {

        "Liter (L)": 1,

        "Milliliter (mL)": 0.001,

        "Cubic Meter (m³)": 1000,

        "Cubic Centimeter (cm³)": 0.001,

        "US Gallon": 3.785411784,

        "US Quart": 0.946352946,

        "US Pint": 0.473176473,

        "US Cup": 0.2365882365,

        "US Fluid Ounce": 0.0295735295625,

        "Tablespoon": 0.01478676478125,

        "Teaspoon": 0.00492892159375
    },


    # --------------------------------------------------------
    # Speed
    # Base unit: Meter per Second
    # --------------------------------------------------------

    "Speed": {

        "Meter/Second (m/s)": 1,

        "Kilometer/Hour (km/h)": 0.2777777778,

        "Mile/Hour (mph)": 0.44704,

        "Foot/Second (ft/s)": 0.3048,

        "Knot": 0.5144444444
    },


    # --------------------------------------------------------
    # Time
    # Base unit: Second
    # --------------------------------------------------------

    "Time": {

        "Second": 1,

        "Millisecond": 0.001,

        "Minute": 60,

        "Hour": 3600,

        "Day": 86400,

        "Week": 604800
    },


    # --------------------------------------------------------
    # Data Storage
    #
    # Uses binary computer units:
    #
    # 1 KB = 1024 bytes
    # --------------------------------------------------------

    "Data Storage": {

        "Byte (B)": 1,

        "Kilobyte (KB)": 1024,

        "Megabyte (MB)": 1024 ** 2,

        "Gigabyte (GB)": 1024 ** 3,

        "Terabyte (TB)": 1024 ** 4,

        "Petabyte (PB)": 1024 ** 5
    },


    # --------------------------------------------------------
    # Pressure
    # Base unit: Pascal
    # --------------------------------------------------------

    "Pressure": {

        "Pascal (Pa)": 1,

        "Kilopascal (kPa)": 1000,

        "Megapascal (MPa)": 1_000_000,

        "Bar": 100000,

        "Atmosphere (atm)": 101325,

        "PSI": 6894.757293168
    },


    # --------------------------------------------------------
    # Energy
    # Base unit: Joule
    # --------------------------------------------------------

    "Energy": {

        "Joule (J)": 1,

        "Kilojoule (kJ)": 1000,

        "Megajoule (MJ)": 1_000_000,

        "Calorie (cal)": 4.184,

        "Kilocalorie (kcal)": 4184,

        "Watt-hour (Wh)": 3600,

        "Kilowatt-hour (kWh)": 3_600_000
    }
}


# ============================================================
# Temperature units
# ============================================================

TEMPERATURE_UNITS = [

    "Celsius (°C)",
    "Fahrenheit (°F)",
    "Kelvin (K)"

]


# ============================================================
# Update unit dropdown menus
# ============================================================

def category_changed(event=None):

    category = category_box.get()

    # Temperature uses its own unit list
    if category == "Temperature":

        units = TEMPERATURE_UNITS

    else:

        units = list(
            CONVERSIONS[category].keys()
        )

    # Change the available units
    from_unit_box["values"] = units
    to_unit_box["values"] = units

    # Automatically select first and second units
    from_unit_box.set(
        units[0]
    )

    if len(units) > 1:

        to_unit_box.set(
            units[1]
        )

    else:

        to_unit_box.set(
            units[0]
        )

    # Clear old result
    result_label.config(
        text="Result will appear here"
    )


# ============================================================
# Temperature conversion
# ============================================================

def convert_temperature(value, from_unit, to_unit):

    # --------------------------------------------------------
    # First convert everything to Celsius
    # --------------------------------------------------------

    if from_unit == "Celsius (°C)":

        celsius = value

    elif from_unit == "Fahrenheit (°F)":

        celsius = (
            value - 32
        ) * 5 / 9

    elif from_unit == "Kelvin (K)":

        celsius = (
            value - 273.15
        )

    else:

        return value

    # --------------------------------------------------------
    # Convert Celsius to target unit
    # --------------------------------------------------------

    if to_unit == "Celsius (°C)":

        return celsius

    elif to_unit == "Fahrenheit (°F)":

        return (
            celsius * 9 / 5
        ) + 32

    elif to_unit == "Kelvin (K)":

        return (
            celsius + 273.15
        )


# ============================================================
# Convert
# ============================================================

def convert():

    # Get the text entered by the user
    value_text = value_entry.get().strip()

    # Make sure something was entered
    if not value_text:

        messagebox.showwarning(
            "Missing Value",
            "Please enter a value."
        )

        return

    # Try converting the entered text into a number
    try:

        value = float(
            value_text
        )

    except ValueError:

        messagebox.showerror(
            "Invalid Number",
            "Please enter a valid number."
        )

        return

    category = category_box.get()

    from_unit = from_unit_box.get()

    to_unit = to_unit_box.get()

    # --------------------------------------------------------
    # Temperature
    # --------------------------------------------------------

    if category == "Temperature":

        result = convert_temperature(
            value,
            from_unit,
            to_unit
        )

    # --------------------------------------------------------
    # All other categories
    # --------------------------------------------------------

    else:

        conversion_table = CONVERSIONS[
            category
        ]

        # Convert entered value into the base unit
        base_value = (
            value
            * conversion_table[from_unit]
        )

        # Convert the base unit into the target unit
        result = (
            base_value
            / conversion_table[to_unit]
        )

    # --------------------------------------------------------
    # Format result
    # --------------------------------------------------------
    #
    # .12g removes unnecessary zeros while still allowing
    # very large or very small numbers.
    # --------------------------------------------------------

    formatted_result = format(
        result,
        ".12g"
    )

    result_label.config(

        text=(
            f"{value:g} {from_unit}\n\n"
            f"=\n\n"
            f"{formatted_result} {to_unit}"
        )

    )


# ============================================================
# Swap units
# ============================================================

def swap_units():

    from_unit = from_unit_box.get()

    to_unit = to_unit_box.get()

    from_unit_box.set(
        to_unit
    )

    to_unit_box.set(
        from_unit
    )

    # Automatically convert again if a value exists
    if value_entry.get().strip():

        convert()


# ============================================================
# Clear everything
# ============================================================

def clear():

    value_entry.delete(
        0,
        tk.END
    )

    result_label.config(
        text="Result will appear here"
    )

    value_entry.focus()


# ============================================================
# Main window
# ============================================================

window = tk.Tk()


window.title(
    "Unit Converter"
)


window.geometry(
    "620x560"
)


window.minsize(
    580,
    520
)


# ============================================================
# Title
# ============================================================

title_label = tk.Label(

    window,

    text="Unit Converter",

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

    text="Convert between common units quickly and easily."

)


description_label.pack(
    pady=(0, 20)
)


# ============================================================
# Category
# ============================================================

category_label = tk.Label(

    window,

    text="Category:"

)


category_label.pack()


category_box = ttk.Combobox(

    window,

    values=[

        "Length",

        "Weight / Mass",

        "Temperature",

        "Area",

        "Volume",

        "Speed",

        "Time",

        "Data Storage",

        "Pressure",

        "Energy"

    ],

    state="readonly",

    width=28

)


category_box.pack(
    pady=7
)


category_box.set(
    "Length"
)


category_box.bind(

    "<<ComboboxSelected>>",

    category_changed

)


# ============================================================
# Value
# ============================================================

value_label = tk.Label(

    window,

    text="Value:"

)


value_label.pack(
    pady=(10, 0)
)


value_entry = tk.Entry(

    window,

    width=30,

    font=(
        "Segoe UI",
        13
    ),

    justify="center"

)


value_entry.pack(
    pady=7
)


# Pressing Enter also converts
value_entry.bind(

    "<Return>",

    lambda event: convert()

)


# ============================================================
# Unit selection
# ============================================================

units_frame = tk.Frame(
    window
)


units_frame.pack(
    pady=15
)


# ------------------------------------------------------------
# From
# ------------------------------------------------------------

from_label = tk.Label(

    units_frame,

    text="From"

)


from_label.grid(

    row=0,
    column=0,

    padx=15

)


from_unit_box = ttk.Combobox(

    units_frame,

    state="readonly",

    width=25

)


from_unit_box.grid(

    row=1,
    column=0,

    padx=10,
    pady=5

)


# ------------------------------------------------------------
# Swap button
# ------------------------------------------------------------

swap_button = tk.Button(

    units_frame,

    text="⇄",

    command=swap_units,

    width=4,

    font=(
        "Segoe UI",
        13
    )

)


swap_button.grid(

    row=1,
    column=1,

    padx=5

)


# ------------------------------------------------------------
# To
# ------------------------------------------------------------

to_label = tk.Label(

    units_frame,

    text="To"

)


to_label.grid(

    row=0,
    column=2,

    padx=15

)


to_unit_box = ttk.Combobox(

    units_frame,

    state="readonly",

    width=25

)


to_unit_box.grid(

    row=1,
    column=2,

    padx=10,
    pady=5

)


# ============================================================
# Convert button
# ============================================================

convert_button = tk.Button(

    window,

    text="Convert",

    command=convert,

    width=20,

    height=2

)


convert_button.pack(
    pady=10
)


# ============================================================
# Result
# ============================================================

result_frame = tk.Frame(

    window,

    relief="groove",

    borderwidth=2,

    padx=20,

    pady=20

)


result_frame.pack(

    padx=30,

    pady=10,

    fill="x"

)


result_label = tk.Label(

    result_frame,

    text="Result will appear here",

    font=(
        "Segoe UI",
        12,
        "bold"
    ),

    justify="center"

)


result_label.pack()


# ============================================================
# Clear button
# ============================================================

clear_button = tk.Button(

    window,

    text="Clear",

    command=clear,

    width=15

)


clear_button.pack(
    pady=10
)


# ============================================================
# Initialize units
# ============================================================

category_changed()


value_entry.focus()


# ============================================================
# Keep the window open
# ============================================================

window.mainloop()
