"""
Clock letters layout calculations.

Functions for calculating letter positions in the grid.
Rows = letters, Columns = colors.
"""

from typing import List


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
        num_rows: Number of rows (letters)

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
    num_cols: int
) -> List[float]:
    """
    Calculate X positions for each color column.

    First column (red) at left edge, last column (teal) at right edge.

    Args:
        screen_left: Left edge of screen
        screen_right: Right edge of screen
        num_cols: Number of columns (colors)

    Returns:
        List of X coordinates for each column
    """
    if num_cols <= 1:
        return [(screen_left + screen_right) / 2]

    spacing = (screen_right - screen_left) / (num_cols - 1)
    return [screen_left + spacing * i for i in range(num_cols)]
