"""
Info panel data constants.

All display data (letters, colors, styles) and visual style constants
used by the info overlay.
"""

# Clock face letters with phonetic names and clock positions
CLOCK_FACE_LETTERS = [
    ("a", "air", "1"),
    ("b", "bat", "2"),
    ("c", "cap", "3"),
    ("d", "drum", "4"),
    ("e", "each", "5"),
    ("f", "fine", "6"),
    ("g", "gust", "7"),
    ("h", "harp", "8"),
    ("i", "sit", "9"),
    ("j", "jury", "10"),
    ("k", "crunch", "11"),
    ("l", "look", "12"),
]

# Colors available
COLORS = [
    ("red", "ff0000ff"),
    ("blue", "0088ffff"),
    ("green", "00ff00ff"),
    ("yellow", "ffff00ff"),
    ("purple", "8800ffff"),
    ("pink", "ff00ffff"),
    ("black", "000000ff"),
    ("white", "ffffffff"),
    ("teal", "008080ff"),
]

# All line styles (every color can use any style)
# Disabled: morse, barb, spike, saw (asymmetric), zig, wave
LINE_STYLES = [
    "solid", "dash", "dot", "tick", "blip", "long",
    "twin", "chain", "rail", "cross", "link", "bead", "hash",
]

# Visual style constants
HEADER_COLOR = "00ff88ff"
TEXT_COLOR = "ffffffff"
MUTED_COLOR = "ccccccff"
ROW_HEIGHT = 28
SECTION_GAP = 40
BG_COLOR = "000000aa"
