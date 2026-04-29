"""
Clock letters targeting functions.

Calculate target positions from letter+color combinations.
"""

from typing import Tuple

from .config import get_clock_letters_colors, get_clock_letters_letters
from .layout import calculate_row_positions, calculate_column_positions
from ..shared.utils import safe_index


def get_row_y(
    screen_rect: Tuple[float, float, float, float],
    letter: str,
) -> float:
    """
    Get the y position for a letter's row.

    Args:
        screen_rect: (left, top, right, bottom) screen bounds
        letter: Target letter (a-z)

    Returns:
        Y coordinate of the row
    """
    left, top, right, bottom = screen_rect
    letters = get_clock_letters_letters()
    letter_idx = safe_index(letters, letter)
    row_positions = calculate_row_positions(top, bottom, len(letters))
    return row_positions[letter_idx] if letter_idx < len(row_positions) else top


def get_column_x(
    screen_rect: Tuple[float, float, float, float],
    color: str,
) -> float:
    """
    Get the x position for a color's column.

    Args:
        screen_rect: (left, top, right, bottom) screen bounds
        color: Target color name

    Returns:
        X coordinate of the column
    """
    left, top, right, bottom = screen_rect
    colors = get_clock_letters_colors()
    color_idx = safe_index(colors, color)
    col_positions = calculate_column_positions(left, right, len(colors))
    return col_positions[color_idx] if color_idx < len(col_positions) else left


def get_clock_letters_target(
    screen_rect: Tuple[float, float, float, float],
    letter: str,
    color: str,
    directions: list = None,
    target_dash: bool = False
) -> Tuple[float, float]:
    """
    Get the (x, y) position for a letter+color target.

    Args:
        screen_rect: (left, top, right, bottom) screen bounds
        letter: Target letter (a-z)
        color: Target color name
        directions: Optional list of offset directions (top, bottom, left, right)
                   Multiple directions combine (e.g., ["top", "left"] = top-left corner)
        target_dash: If True, target the dash after the specified color column

    Returns:
        (x, y) coordinates of the target
    """
    left, top, right, bottom = screen_rect

    y = get_row_y(screen_rect, letter)
    x = get_column_x(screen_rect, color)

    if target_dash:
        # Target the dash after this color column (midpoint to next column)
        colors = get_clock_letters_colors()
        color_idx = safe_index(colors, color)
        col_positions = calculate_column_positions(left, right, len(colors))
        if color_idx < len(col_positions) - 1:
            x = (col_positions[color_idx] + col_positions[color_idx + 1]) / 2

    # Apply directional offsets (can combine multiple)
    if directions:
        letters = get_clock_letters_letters()
        colors = get_clock_letters_colors()
        # Calculate cell spacing for offset
        row_spacing = (bottom - top) / (len(letters) + 1)
        col_spacing = (right - left) / (len(colors) + 1)
        # Offset by ~40% of cell size to get near edge but not at boundary
        offset_factor = 0.4

        for direction in directions:
            if direction == 'top':
                y -= row_spacing * offset_factor
            elif direction == 'bottom':
                y += row_spacing * offset_factor
            elif direction == 'left':
                x -= col_spacing * offset_factor
            elif direction == 'right':
                x += col_spacing * offset_factor

    return (x, y)
