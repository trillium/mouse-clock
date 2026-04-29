"""
Clock letters overlay rendering.

Draws letters in a grid: rows = letters, columns = colors.
Each letter appears once per color, horizontally distributed.
Columns can be "letters" (letter grid) or "line" (vertical colored line).
"""

from typing import List, Optional, Tuple

from ...rendering.colors import get_color
from ...rendering.drawing import draw_text, draw_rect, draw_line
from .config import (
    get_text_color, get_text_bg_color,
    get_clock_letters_colors, get_clock_letters_letters, get_column_types,
)
from .layout import calculate_row_positions, calculate_column_positions
from ...rendering.colors import parse_hex_color, relative_luminance
from ..shared.alpha import apply_alpha, set_alpha


def _is_dark_color(color_hex: str) -> bool:
    """Check if a color is very dark (needs light background for readability)."""
    try:
        r, g, b, _ = parse_hex_color(color_hex)
        lum = relative_luminance(r, g, b)
        return lum < 0.05  # Only true black and near-black
    except (ValueError, IndexError):
        return False


# Light background for dark text colors
LIGHT_BG_COLOR = "ffffffaa"  # Semi-transparent white

# Line column width
LINE_COLUMN_WIDTH = 3


def _draw_line_column(canvas, x, screen_top, screen_bottom, color, alpha):
    """Draw a vertical colored line spanning the full screen height.

    Args:
        canvas: Talon canvas object
        x: X position for the line
        screen_top: Top of screen
        screen_bottom: Bottom of screen
        color: Color name string
        alpha: Current alpha value (0-255)
    """
    raw_color = get_color(color)
    line_color = apply_alpha(raw_color, "clock_letters")
    draw_line(canvas, (x, screen_top), (x, screen_bottom), line_color, LINE_COLUMN_WIDTH)


def _draw_guide_lines(
    canvas, left, top, right, bottom,
    row_positions, col_positions,
    letters, colors,
    pending_letter: Optional[List[str]],
    pending_color: Optional[List[str]],
):
    """Draw guide lines for pending partial inputs.

    Letter pending -> horizontal line at that letter's row.
    Color pending -> vertical line at that color's column.
    """
    guide_color = apply_alpha("00ffffcc", "clock_letters")
    thickness = 2

    if pending_letter:
        for ltr in pending_letter:
            ltr_lower = ltr.lower()
            if ltr_lower in letters:
                idx = letters.index(ltr_lower)
                y = row_positions[idx]
                draw_line(canvas, (left, y), (right, y), guide_color, thickness)

    if pending_color:
        for clr in pending_color:
            clr_lower = clr.lower()
            if clr_lower in colors:
                idx = colors.index(clr_lower)
                x = col_positions[idx]
                draw_line(canvas, (x, top), (x, bottom), guide_color, thickness)


def draw_clock_letters_overlay(
    canvas,
    screen_rect: Tuple[float, float, float, float],
    alpha: int = 255,
    pending_letter: Optional[List[str]] = None,
    pending_color: Optional[List[str]] = None,
):
    """
    Draw the clock letters overlay with pluggable column renderers.

    Columns with type "letters" draw the standard letter grid.
    Columns with type "line" draw a vertical colored line.

    Args:
        canvas: Talon canvas object
        screen_rect: (left, top, right, bottom) screen bounds
        alpha: Overall transparency (0-255) for fade effects
    """
    set_alpha("clock_letters", alpha)

    left, top, right, bottom = screen_rect
    screen_width = right - left
    screen_height = bottom - top

    # Clear screen with semi-transparent background
    draw_rect(canvas, (left, top, screen_width, screen_height), "000000aa", thickness=0, filled=True)

    colors = get_clock_letters_colors()
    letters = get_clock_letters_letters()

    if not colors or not letters:
        print("[clock_letters] WARNING: no colors or letters, returning early")
        return

    column_types = get_column_types()
    row_positions = calculate_row_positions(top, bottom, len(letters))
    col_positions = calculate_column_positions(left, right, len(colors))

    bg_color = apply_alpha(get_text_bg_color(), "clock_letters")

    # First pass: draw "line" columns (full-height vertical lines)
    for col_idx, color_name in enumerate(colors):
        if col_idx < len(column_types) and column_types[col_idx] == "line":
            _draw_line_column(canvas, col_positions[col_idx], top, bottom, color_name, alpha)

    # Calculate dash positions (midpoint between each pair of color columns)
    dash_info = []
    for i in range(len(col_positions) - 1):
        dash_x = (col_positions[i] + col_positions[i + 1]) / 2
        dash_info.append((dash_x, colors[i]))

    # Second pass: draw letters for "letters" columns, row by row
    for row_idx, letter in enumerate(letters):
        y = row_positions[row_idx]

        for col_idx, color_name in enumerate(colors):
            # Skip "line" columns — they were drawn in the first pass
            col_type = column_types[col_idx] if col_idx < len(column_types) else "letters"
            if col_type == "line":
                continue

            x = col_positions[col_idx]
            raw_color = get_color(color_name)
            text_color = apply_alpha(raw_color, "clock_letters")

            # Use light background for dark text colors (like black)
            if _is_dark_color(raw_color):
                box_bg = apply_alpha(LIGHT_BG_COLOR, "clock_letters")
            else:
                box_bg = bg_color

            # Draw background box centered at (x, y)
            box_size = 24
            box_left = x - box_size / 2
            box_top = y - box_size / 2
            draw_rect(
                canvas,
                (box_left, box_top, box_size, box_size),
                box_bg,
                thickness=0,
                filled=True
            )

            # Draw the letter (centered in box)
            draw_text(
                canvas,
                (x, y),
                letter.upper(),
                text_color,
                font_size=18,
                anchor="center"
            )

        # Draw dashes between columns for this row (colored by left column)
        for dash_x, dash_color_name in dash_info:
            dash_color = apply_alpha(get_color(dash_color_name), "clock_letters")
            draw_text(
                canvas,
                (dash_x, y),
                "-",
                dash_color,
                font_size=18,
                anchor="center"
            )

    # Draw guide lines for any pending partial input
    _draw_guide_lines(
        canvas, left, top, right, bottom,
        row_positions, col_positions,
        letters, colors,
        pending_letter, pending_color,
    )
