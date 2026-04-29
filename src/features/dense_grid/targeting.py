"""
Dense grid targeting functions.

Calculate target positions from letter+color combinations.
Grid is centered on the mouse with fixed pixel spacing.
Columns = letters (X), Rows = colors (Y).
"""

from typing import Tuple

from .config import get_dense_grid_colors, get_dense_grid_letters, get_dense_grid_spacing_x, get_dense_grid_spacing_y
from ..shared.utils import safe_index


def get_dense_grid_target(
    center: Tuple[float, float],
    letter: str,
    color: str,
    directions: list = None,
) -> Tuple[float, float]:
    """
    Get the (x, y) position for a letter+color target in the dense grid.

    Args:
        center: (center_x, center_y) — mouse position the grid is centered on
        letter: Target letter (a-z)
        color: Target color name
        directions: Optional list of offset directions

    Returns:
        (x, y) coordinates of the target
    """
    center_x, center_y = center

    colors = get_dense_grid_colors()
    letters = get_dense_grid_letters()

    letter_idx = safe_index(letters, letter)
    color_idx = safe_index(colors, color)

    num_cols = len(letters)
    num_rows = len(colors)

    spacing_x = get_dense_grid_spacing_x()
    spacing_y = get_dense_grid_spacing_y()

    # Grid top-left, centered on mouse
    grid_width = (num_cols - 1) * spacing_x
    grid_height = (num_rows - 1) * spacing_y
    grid_left = center_x - grid_width / 2
    grid_top = center_y - grid_height / 2

    x = grid_left + letter_idx * spacing_x
    y = grid_top + color_idx * spacing_y

    if directions:
        offset_factor = 0.4
        for direction in directions:
            if direction == 'top':
                y -= spacing_y * offset_factor
            elif direction == 'bottom':
                y += spacing_y * offset_factor
            elif direction == 'left':
                x -= spacing_x * offset_factor
            elif direction == 'right':
                x += spacing_x * offset_factor

    return (x, y)
