"""
Pure constants for the mouse clock system.

Color definitions, radius defaults, screen fallbacks, and drawing constants.
No imports, no functions — safe for any module to import.
"""

# Clock configuration
CLOCK_LETTERS = "abcdefghijkl"

# Direction offsets for cell targeting
DIRECTIONS = ("top", "bottom", "left", "right")

# Radius configuration
DEFAULT_RADIUS = 300
MIN_RADIUS = 20

# Color names (note: 7 colors including center, not 5 as in original design doc)
COLOR_NAMES = "center red blue green yellow purple pink black white teal"

# Color hex values (8-digit RGBA format for Talon/Skia)
COLORS = {
    "GRAY": "9999995f",        # Background color
    "GREEN": "00ff00ff",       # Text color
    "RED": "ff0000ff",         # Dot and active grid color
    "LIGHT_GREEN": "00ff007f", # Cross color
    "BLACK": "000000ff",       # Black
    "WHITE": "ffffffff",       # White
    "TEAL": "008080ff",        # Teal
    "BLUE": "0000ffff",        # Blue ring color
    "PINK": "ff00ffff",        # Pink ring color
    "ORANGE": "ffa500ff",      # Orange color (unused currently)
    "YELLOW": "FFD700ff",      # Gold-like bright yellow
    "PURPLE": "800080ff",      # Classic purple
    "CENTER": "000000ff",      # Center color (black)
}

# Semantic color aliases
COLOR_BACKGROUND = COLORS["GRAY"]
COLOR_TEXT = COLORS["GREEN"]
COLOR_DOT = COLORS["RED"]
COLOR_CROSS = COLORS["LIGHT_GREEN"]
COLOR_ACTIVE = COLORS["RED"]
COLOR_INACTIVE = COLORS["BLACK"]

# Color lists and mappings
COLOR_LIST = [COLORS[color.upper()] for color in COLOR_NAMES.split() if color.upper() in COLORS]
COLOR_MAP = {color: COLORS[color.upper()] for color in COLOR_NAMES.split()}
COLOR_POS = {color.lower(): index for index, color in enumerate(COLOR_MAP.keys())}

# Screen dimensions fallback
DEFAULT_SCREEN_WIDTH = 1920
DEFAULT_SCREEN_HEIGHT = 1080

# Drawing configuration
DEFAULT_STROKE_WIDTH = 2
DEFAULT_DOT_RADIUS = 5
