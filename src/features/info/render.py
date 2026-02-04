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

# Style constants
HEADER_COLOR = "00ff88ff"
TEXT_COLOR = "ffffffff"
MUTED_COLOR = "888888ff"
ROW_HEIGHT = 28
SECTION_GAP = 40


def draw_letters_section(canvas, x: float, y: float) -> float:
    """Draw the letters/clock face section. Returns final y position."""
    draw_text(canvas, (x, y), "LETTERS (Clock Face)", HEADER_COLOR, font_size=18, anchor="left")
    y += ROW_HEIGHT + 10

    for letter, phonetic, number in CLOCK_FACE_LETTERS:
        line = f"{letter}  ->  {phonetic}  ({number})"
        draw_text(canvas, (x, y), line, TEXT_COLOR, font_size=16, anchor="left")
        y += ROW_HEIGHT

    return y


def draw_colors_section(canvas, x: float, y: float) -> float:
    """Draw the colors section. Returns final y position."""
    draw_text(canvas, (x, y), "COLORS", HEADER_COLOR, font_size=18, anchor="left")
    y += ROW_HEIGHT + 10

    for color_name, color_hex in COLORS:
        swatch_size = 16
        draw_rect(canvas, (x, y - 12, swatch_size, swatch_size), color_hex, thickness=0, filled=True)
        draw_text(canvas, (x + swatch_size + 10, y), color_name, TEXT_COLOR, font_size=16, anchor="left")
        y += ROW_HEIGHT

    return y


def draw_commands_section(canvas, x: float, y: float) -> float:
    """Draw the commands section. Returns final y position."""
    draw_text(canvas, (x, y), "COMMANDS", HEADER_COLOR, font_size=18, anchor="left")
    y += ROW_HEIGHT + 10

    commands = [
        ("widen", "Increase radius"),
        ("narrow", "Decrease radius"),
        ("recenter", "Move clock to mouse"),
        ("touch", "Click and close"),
        ("reverse", "Opposite of last"),
    ]

    # Indent to match color names (swatch_size 16 + 10 gap = 26)
    indent = 26
    for cmd, desc in commands:
        draw_text(canvas, (x + indent, y), cmd, TEXT_COLOR, font_size=16, anchor="left")
        draw_text(canvas, (x + indent + 100, y), desc, MUTED_COLOR, font_size=14, anchor="left")
        y += ROW_HEIGHT

    return y


def draw_line_styles_section(canvas, x: float, y: float) -> float:
    """Draw the line styles section. Returns final y position."""
    draw_text(canvas, (x, y), "LINE STYLES", HEADER_COLOR, font_size=18, anchor="left")
    y += ROW_HEIGHT + 10

    # Collect all unique styles
    all_styles = []
    for styles in LINE_STYLES_BY_COLOR.values():
        for style in styles:
            if style not in all_styles:
                all_styles.append(style)

    h_line_length = 50
    v_line_length = 22  # Shorter to fit within row height
    style_color = "00aaffff"  # Neutral blue for visibility
    v_stagger_step = 25  # Horizontal offset between stagger positions

    for i, style in enumerate(all_styles):
        # Style name
        draw_text(canvas, (x, y), style, TEXT_COLOR, font_size=14, anchor="left")

        # Horizontal sample
        h_start_x = x + 70
        h_y = y - 6
        # White base line showing click area
        draw_line(canvas, (h_start_x, h_y), (h_start_x + h_line_length, h_y), "ffffffff", thickness=1, line_style="solid")
        # Styled line on top
        draw_line(canvas, (h_start_x, h_y), (h_start_x + h_line_length, h_y), style_color, thickness=2, line_style=style)

        # Vertical sample - staggered horizontally in 3-step pattern
        stagger_offset = (i % 3) * v_stagger_step
        v_x = h_start_x + h_line_length + 20 + stagger_offset
        v_start_y = y - 6 - (v_line_length // 2)
        v_end_y = y - 6 + (v_line_length // 2)
        # White base line showing click area
        draw_line(canvas, (v_x, v_start_y), (v_x, v_end_y), "ffffffff", thickness=1, line_style="solid")
        # Styled line on top
        draw_line(canvas, (v_x, v_start_y), (v_x, v_end_y), style_color, thickness=2, line_style=style)

        y += ROW_HEIGHT

    return y


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

    # Layout
    bg_color = "000000aa"
    padding = 40
    col_width = 340

    # Draw semi-transparent background
    draw_rect(canvas, (left, top, screen_width, screen_height), bg_color, thickness=0, filled=True)

    # Title
    title_y = top + padding
    draw_text(canvas, (left + padding, title_y), "MOUSE CLOCK COMMANDS", HEADER_COLOR, font_size=24, anchor="left")

    content_top = title_y + 50

    # Column positions
    col1_x = left + padding
    col2_x = col1_x + col_width
    col3_x = col2_x + col_width

    # Column 1: Letters
    draw_letters_section(canvas, col1_x, content_top)

    # Column 2: Line Styles
    draw_line_styles_section(canvas, col2_x, content_top)

    # Column 3: Colors + Commands
    y = draw_colors_section(canvas, col3_x, content_top)
    y += SECTION_GAP
    draw_commands_section(canvas, col3_x, y)

    # Footer
    footer_y = bottom - padding
    draw_text(canvas, (left + padding, footer_y), "Press super-w to cycle display modes", MUTED_COLOR, font_size=14, anchor="left")
