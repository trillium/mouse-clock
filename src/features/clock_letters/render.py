"""
Clock letters overlay rendering.

Draws letters in a grid: rows = letters, columns = colors.
Each letter appears once per color, horizontally distributed.
"""

print("reloaded clock_letters/render.py")

from typing import Tuple, List

from ...rendering.colors import get_color, with_alpha
from ...rendering.drawing import draw_text, draw_rect
from .config import get_text_color, get_text_bg_color, get_clock_letters_colors, get_clock_letters_letters
from .layout import calculate_row_positions, calculate_column_positions
from ..info.contrast import parse_hex_color, relative_luminance

# Module-level alpha for fade animations
_current_alpha = 255


def _apply_alpha(color_hex: str) -> str:
    """Apply current fade alpha to a color."""
    if _current_alpha >= 255:
        return color_hex
    existing_alpha = int(color_hex[6:8], 16) if len(color_hex) >= 8 else 255
    new_alpha = (existing_alpha * _current_alpha) // 255
    return with_alpha(color_hex, new_alpha)


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


def draw_clock_letters_overlay(
    canvas,
    screen_rect: Tuple[float, float, float, float],
    alpha: int = 255
):
    """
    Draw the clock letters overlay.

    Layout:
        a  a  a  a    <- letter 'a' in red, blue, green, yellow
        b  b  b  b    <- letter 'b' in red, blue, green, yellow
        ...

    Args:
        canvas: Talon canvas object
        screen_rect: (left, top, right, bottom) screen bounds
        alpha: Overall transparency (0-255) for fade effects
    """
    global _current_alpha
    _current_alpha = alpha

    left, top, right, bottom = screen_rect
    screen_width = right - left
    screen_height = bottom - top

    # Clear screen with semi-transparent background (matches info mode)
    # This ensures previous mode's content is properly covered
    draw_rect(canvas, (left, top, screen_width, screen_height), "000000aa", thickness=0, filled=True)

    colors = get_clock_letters_colors()
    letters = get_clock_letters_letters()
    # print(f"[clock_letters] colors={colors}, letters={letters}")

    if not colors or not letters:
        print("[clock_letters] WARNING: no colors or letters, returning early")
        return

    row_positions = calculate_row_positions(top, bottom, len(letters))
    col_positions = calculate_column_positions(left, right, len(colors))
    # print(f"[clock_letters] row_positions: first={row_positions[0]:.1f}, last={row_positions[-1]:.1f}")
    # print(f"[clock_letters] col_positions: first={col_positions[0]:.1f}, last={col_positions[-1]:.1f}")
    # print(f"[clock_letters] first letter 'a' red at ({col_positions[0]:.1f}, {row_positions[0]:.1f})")

    bg_color = _apply_alpha(get_text_bg_color())

    # Calculate dash positions (midpoint between each pair of color columns)
    # Each dash takes the color of the column to its left
    dash_info = []
    for i in range(len(col_positions) - 1):
        dash_x = (col_positions[i] + col_positions[i + 1]) / 2
        dash_info.append((dash_x, colors[i]))  # position and color name

    # Draw each letter at each color position
    for row_idx, letter in enumerate(letters):
        y = row_positions[row_idx]

        for col_idx, color_name in enumerate(colors):
            x = col_positions[col_idx]
            raw_color = get_color(color_name)
            text_color = _apply_alpha(raw_color)

            # Use light background for dark text colors (like black)
            if _is_dark_color(raw_color):
                box_bg = _apply_alpha(LIGHT_BG_COLOR)
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
            dash_color = _apply_alpha(get_color(dash_color_name))
            draw_text(
                canvas,
                (dash_x, y),
                "-",
                dash_color,
                font_size=18,
                anchor="center"
            )

    # print(f"[clock_letters] drew {len(letters)} rows x {len(colors)} cols = {len(letters) * len(colors)} letters")
