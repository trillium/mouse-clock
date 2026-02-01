"""
Grid targeting functions.

Calculate target positions from letter+color combinations.
"""

from typing import Tuple

from ...core.config import get_setting
from .config import get_grid_colors
from .layout import get_visible_letters, calculate_row_positions, calculate_column_positions


def get_grid_target(
    screen_rect: Tuple[float, float, float, float],
    letter: str,
    color: str,
    swap_axes: bool = False
) -> Tuple[float, float]:
    """
    Get the (x, y) position for a letter+color target.

    Args:
        screen_rect: (left, top, right, bottom) screen bounds
        letter: Target letter (A-Z)
        color: Target color name
        swap_axes: If True, colors on Y and letters on X

    Returns:
        (x, y) coordinates of the intersection
    """
    left, top, right, bottom = screen_rect

    colors = get_grid_colors()
    row_spacing = get_setting("grid_row_spacing", 40)
    screen_height = bottom - top
    letters = get_visible_letters(screen_height, row_spacing)

    # Find indices
    letter_upper = letter.upper()
    color_lower = color.lower()

    try:
        letter_idx = letters.index(letter_upper)
    except ValueError:
        letter_idx = 0

    try:
        color_idx = colors.index(color_lower)
    except ValueError:
        color_idx = 0

    if swap_axes:
        row_positions = calculate_row_positions(top, bottom, len(colors))
        col_positions = calculate_column_positions(left, right, len(letters))
        x = col_positions[letter_idx] if letter_idx < len(col_positions) else left
        y = row_positions[color_idx] if color_idx < len(row_positions) else top
    else:
        row_positions = calculate_row_positions(top, bottom, len(letters))
        col_positions = calculate_column_positions(left, right, len(colors))
        x = col_positions[color_idx] if color_idx < len(col_positions) else left
        y = row_positions[letter_idx] if letter_idx < len(row_positions) else top

    return (x, y)
