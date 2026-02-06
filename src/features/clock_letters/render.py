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

# Module-level alpha for fade animations
_current_alpha = 255


def _apply_alpha(color_hex: str) -> str:
    """Apply current fade alpha to a color."""
    if _current_alpha >= 255:
        return color_hex
    existing_alpha = int(color_hex[6:8], 16) if len(color_hex) >= 8 else 255
    new_alpha = (existing_alpha * _current_alpha) // 255
    return with_alpha(color_hex, new_alpha)


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
    print(f"[clock_letters] draw_clock_letters_overlay called, rect=({left}, {top}, {right}, {bottom}), alpha={alpha}")

    colors = get_clock_letters_colors()
    letters = get_clock_letters_letters()
    print(f"[clock_letters] colors={colors}, letters={letters}")

    if not colors or not letters:
        print("[clock_letters] WARNING: no colors or letters, returning early")
        return

    row_positions = calculate_row_positions(top, bottom, len(letters))
    col_positions = calculate_column_positions(left, right, len(colors))
    print(f"[clock_letters] row_positions={row_positions[:3]}..., col_positions={col_positions}")

    bg_color = _apply_alpha(get_text_bg_color())

    # Draw each letter at each color position
    for row_idx, letter in enumerate(letters):
        y = row_positions[row_idx]

        for col_idx, color_name in enumerate(colors):
            x = col_positions[col_idx]
            text_color = _apply_alpha(get_color(color_name))

            # Draw background box
            box_size = 24
            draw_rect(
                canvas,
                (x - box_size/2, y - box_size/2, box_size, box_size),
                bg_color,
                thickness=0,
                filled=True
            )

            # Draw the letter
            draw_text(
                canvas,
                (x, y + 6),  # +6 for vertical centering
                letter.upper(),
                text_color,
                font_size=18,
                anchor="center"
            )

    print(f"[clock_letters] drew {len(letters)} rows x {len(colors)} cols = {len(letters) * len(colors)} letters")
