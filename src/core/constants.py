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
    "GREEN": "36b33fff",       # Cursorless green
    "RED": "e02d28ff",         # Cursorless red
    "LIGHT_GREEN": "00ff007f", # Cross color
    "BLACK": "000000ff",       # Cursorless userColor1
    "WHITE": "ffffffff",       # Cursorless userColor3
    "TEAL": "00d1d1ff",        # Cursorless userColor4
    "BLUE": "089ad3ff",        # Cursorless blue
    "PINK": "e06caaff",        # Cursorless pink
    "ORANGE": "ffa500ff",      # Orange color (unused currently)
    "YELLOW": "e5c02cff",      # Cursorless yellow
    "PURPLE": "8e44adff",      # Cursorless userColor2
    "CENTER": "b9b6cdff",      # Cursorless default
}

# Semantic color aliases
COLOR_BACKGROUND = COLORS["GRAY"]
COLOR_TEXT = COLORS["GREEN"]
COLOR_DOT = COLORS["RED"]
COLOR_CROSS = COLORS["LIGHT_GREEN"]
COLOR_ACTIVE = COLORS["RED"]
COLOR_INACTIVE = COLORS["BLACK"]
DEFAULT_TEXT_COLOR = COLORS["GREEN"]
DEFAULT_TEXT_BG_COLOR = "000000aa"  # Semi-transparent black

# Color lists and mappings
COLOR_LIST = [COLORS[color.upper()] for color in COLOR_NAMES.split() if color.upper() in COLORS]
COLOR_MAP = {color: COLORS[color.upper()] for color in COLOR_NAMES.split()}
COLOR_POS = {color.lower(): index for index, color in enumerate(COLOR_MAP.keys())}

# Colors shown in info panels and pie chart (excludes internal-only colors like gray, light_green, center)
DISPLAY_COLORS = ["black", "red", "blue", "green", "yellow", "purple", "pink", "white", "teal"]

# Screen dimensions fallback
DEFAULT_SCREEN_WIDTH = 1920
DEFAULT_SCREEN_HEIGHT = 1080

# Drawing configuration
DEFAULT_STROKE_WIDTH = 2
DEFAULT_DOT_RADIUS = 5

# Display modes
DISPLAY_MODE_CIRCLES = "circles"
DISPLAY_MODE_CLOCK_LETTERS = "clock_letters"
DISPLAY_MODES = [DISPLAY_MODE_CIRCLES, DISPLAY_MODE_CLOCK_LETTERS]

# Cursorless hat shapes: SVG filename stem -> one-syllable spoken form
HAT_NAMES = {
    "bolt": "bolt",
    "crosshairs": "cross",
    "curve": "curve",
    "default": "dot",
    "ex": "ex",
    "eye": "eye",
    "fox": "fox",
    "frame": "frame",
    "hole": "hole",
    "play": "play",
    "wing": "wing",
}
HAT_SHAPES = [name for name in HAT_NAMES.values() if name != "dot"]
HAT_SHAPE_LIST = {v: v for v in HAT_NAMES.values()}
