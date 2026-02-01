"""
Info overlay rendering.

Draws a help/cheat sheet showing available voice commands.
"""

from typing import Tuple
from talon.skia import Paint

from ...rendering.drawing import draw_text, draw_line, draw_rect

# Clock face letters with phonetic names
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
]

# Line styles grouped by color assignment
LINE_STYLES_BY_COLOR = {
    "red": ["dash", "dot", "tick"],
    "blue": ["blip", "long", "morse"],
    "green": ["twin", "chain", "wave"],
    "yellow": ["zig", "barb", "rail"],
    "purple": ["cross", "link", "bead"],
    "pink": ["spike", "hash", "saw"],
}


def draw_info_overlay(
    canvas,
    screen_rect: Tuple[float, float, float, float],
):
    """
    Draw the info/help overlay showing available voice commands.

    Args:
        canvas: Talon canvas object
        screen_rect: (left, top, right, bottom) screen bounds
    """
    left, top, right, bottom = screen_rect
    screen_width = right - left
    screen_height = bottom - top

    # Colors
    bg_color = "000000aa"
    text_color = "ffffffff"
    header_color = "00ff88ff"
    muted_color = "888888ff"

    # Layout
    padding = 40
    col_width = 280
    row_height = 28
    section_gap = 40

    # Draw semi-transparent background
    draw_rect(canvas, (left, top, screen_width, screen_height), bg_color, thickness=0, filled=True)

    # Title
    title_y = top + padding
    draw_text(canvas, (left + padding, title_y), "MOUSE CLOCK COMMANDS", header_color, font_size=24, anchor="left")

    content_top = title_y + 50

    # === COLUMN 1: Letters ===
    col1_x = left + padding
    y = content_top

    draw_text(canvas, (col1_x, y), "LETTERS (Clock Face)", header_color, font_size=18, anchor="left")
    y += row_height + 10

    for letter, phonetic, number in CLOCK_FACE_LETTERS:
        # letter -> phonetic (number)
        line = f"{letter}  ->  {phonetic}  ({number})"
        draw_text(canvas, (col1_x, y), line, text_color, font_size=16, anchor="left")
        y += row_height

    # === COLUMN 2: Colors ===
    col2_x = col1_x + col_width
    y = content_top

    draw_text(canvas, (col2_x, y), "COLORS", header_color, font_size=18, anchor="left")
    y += row_height + 10

    for color_name, color_hex in COLORS:
        # Draw color swatch
        swatch_size = 16
        draw_rect(canvas, (col2_x, y - 12, swatch_size, swatch_size), color_hex, thickness=0, filled=True)
        # Draw name
        draw_text(canvas, (col2_x + swatch_size + 10, y), color_name, text_color, font_size=16, anchor="left")
        y += row_height

    y += section_gap

    # Commands section
    draw_text(canvas, (col2_x, y), "COMMANDS", header_color, font_size=18, anchor="left")
    y += row_height + 10

    commands = [
        ("widen", "Increase radius"),
        ("narrow", "Decrease radius"),
        ("recenter", "Move clock to mouse"),
        ("touch", "Click and close"),
        ("reverse", "Opposite of last"),
    ]

    for cmd, desc in commands:
        draw_text(canvas, (col2_x, y), cmd, text_color, font_size=16, anchor="left")
        draw_text(canvas, (col2_x + 100, y), desc, muted_color, font_size=14, anchor="left")
        y += row_height

    # === COLUMN 3: Line Styles ===
    col3_x = col2_x + col_width
    y = content_top

    draw_text(canvas, (col3_x, y), "LINE STYLES (by color)", header_color, font_size=18, anchor="left")
    y += row_height + 10

    line_sample_width = 60

    for color_name, color_hex in COLORS:
        styles = LINE_STYLES_BY_COLOR.get(color_name, [])

        # Color header (outline only so line samples are visible)
        draw_rect(canvas, (col3_x, y - 12, 12, 12), color_hex, thickness=2, filled=False)
        draw_text(canvas, (col3_x + 18, y), f"{color_name}:", text_color, font_size=14, anchor="left")
        y += row_height - 4

        for style in styles:
            # Style name
            draw_text(canvas, (col3_x + 20, y), style, muted_color, font_size=14, anchor="left")
            # Draw line sample
            sample_x = col3_x + 80
            draw_line(canvas, (sample_x, y - 6), (sample_x + line_sample_width, y - 6), color_hex, thickness=2, line_style=style)
            y += row_height - 6

        y += 8  # Gap between colors

    # === Footer with mode cycling hint ===
    footer_y = bottom - padding
    draw_text(canvas, (left + padding, footer_y), "Press super-w to cycle display modes", muted_color, font_size=14, anchor="left")
