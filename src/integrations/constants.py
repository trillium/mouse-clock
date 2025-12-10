# constants.py
# Mouse Clock constants and color definitions

CLOCK_LETTERS = "abcdefghijkl"

colors = "center red blue green yellow purple pink"

COLORS = {
    "GRAY": "9999995f",        # Background color
    "GREEN": "00ff00ff",       # Text color
    "RED": "ff0000ff",         # Dot and active grid color
    "LIGHT_GREEN": "00ff007f", # Cross color
    "BLACK": "000000ff",       # Inactive grid color
    "BLUE": "0000ffff",        # New blue color
    "PINK": "ff00ffff",        # New pink color
    "ORANGE": "ffa500ff",      # New orange color
    "YELLOW": "FFD700ff",      # Gold-like bright yellow (fixed to 8-digit hex)
    "PURPLE": "800080ff",      # Classic purple (fixed to 8-digit hex)
    "CENTER": "000000ff",      # Center color (black)
}

COLOR_BACKGROUND = COLORS["GRAY"]
COLOR_TEXT = COLORS["GREEN"]
COLOR_DOT = COLORS["RED"]
COLOR_CROSS = COLORS["LIGHT_GREEN"]
COLOR_ACTIVE = COLORS["RED"]
COLOR_INACTIVE = COLORS["BLACK"]

COLOR_LIST = [COLORS[color.upper()] for color in colors.split() if color.upper() in COLORS]
COLOR_MAP = {color: COLORS[color.upper()] for color in colors.split()}
COLOR_POS = {color.lower(): index for index, color in enumerate(COLOR_MAP.keys())}
