"""
Grid overlay layout calculations.

Functions for calculating row and column positions.
"""

from typing import List

from ...core.config import get_setting
from .config import get_grid_letters
from .state import get_column_offset


def get_visible_letters(screen_height: float, row_spacing: float) -> List[str]:
    """
    Get letters that fit on screen given spacing.

    Args:
        screen_height: Available height in pixels
        row_spacing: Pixels between rows

    Returns:
        List of letters that fit
    """
    letters = get_grid_letters()
    max_rows = int(screen_height / row_spacing)
    return letters[:min(max_rows, len(letters))]


def calculate_row_positions(
    screen_top: float,
    screen_bottom: float,
    num_rows: int
) -> List[float]:
    """
    Calculate Y positions for each letter row.

    Args:
        screen_top: Top of screen
        screen_bottom: Bottom of screen
        num_rows: Number of rows to position

    Returns:
        List of Y coordinates for each row
    """
    if num_rows <= 1:
        return [(screen_top + screen_bottom) / 2]

    spacing = (screen_bottom - screen_top) / (num_rows + 1)
    return [screen_top + spacing * (i + 1) for i in range(num_rows)]


def calculate_column_positions(
    screen_left: float,
    screen_right: float,
    num_cols: int,
    center_x: float = None,
    offset_x: float = None
) -> List[float]:
    """
    Calculate X positions for each color column, distributed evenly across screen.

    Args:
        screen_left: Left edge of screen
        screen_right: Right edge of screen
        num_cols: Number of columns to position
        center_x: Unused, kept for API compatibility
        offset_x: Horizontal offset to apply (defaults to global offset)

    Returns:
        List of X coordinates for each column
    """
    if num_cols <= 1:
        return [(screen_left + screen_right) / 2]

    if offset_x is None:
        offset_x = get_column_offset()

    # Distribute evenly across screen width (like rows do for height)
    spacing = (screen_right - screen_left) / (num_cols + 1)
    return [screen_left + spacing * (i + 1) + offset_x for i in range(num_cols)]
