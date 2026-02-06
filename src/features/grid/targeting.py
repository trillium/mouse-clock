"""
Grid targeting functions.

Calculate target positions from letter+color+style combinations.
"""

from typing import Tuple, Optional

from .config import get_grid_colors, get_grid_letters, get_horizontal_styles, get_vertical_styles
from .layout import calculate_row_positions, calculate_column_positions


def get_grid_target(
    screen_rect: Tuple[float, float, float, float],
    letter: str,
    color: str,
    h_style: Optional[str] = None,
    v_style: Optional[str] = None,
    swap_axes: bool = False
) -> Tuple[float, float]:
    """
    Get the (x, y) position for a letter+color+style target.

    Args:
        screen_rect: (left, top, right, bottom) screen bounds
        letter: Target letter (a-l)
        color: Target color name
        h_style: Horizontal line style (for letter row), defaults to first style
        v_style: Vertical line style (for color column), defaults to first style
        swap_axes: If True, colors on Y and letters on X

    Returns:
        (x, y) coordinates of the intersection
    """
    left, top, right, bottom = screen_rect

    colors = get_grid_colors()
    letters = get_grid_letters()
    h_styles = get_horizontal_styles()
    v_styles = get_vertical_styles()

    # Find indices
    letter_lower = letter.lower()
    color_lower = color.lower()

    try:
        letter_idx = letters.index(letter_lower)
    except ValueError:
        letter_idx = 0

    try:
        color_idx = colors.index(color_lower)
    except ValueError:
        color_idx = 0

    # Find style indices (default to "solid")
    h_style_idx = 0
    h_style_to_find = (h_style or "solid").lower()
    try:
        h_style_idx = h_styles.index(h_style_to_find)
    except ValueError:
        h_style_idx = 0

    v_style_idx = 0
    v_style_to_find = (v_style or "solid").lower()
    try:
        v_style_idx = v_styles.index(v_style_to_find)
    except ValueError:
        v_style_idx = 0

    # Calculate row index: letter * num_h_styles + h_style_idx
    # Calculate col index: color * num_v_styles + v_style_idx
    num_h_styles = len(h_styles)
    num_v_styles = len(v_styles)

    if swap_axes:
        # Colors on Y, Letters on X
        num_rows = len(colors) * num_h_styles
        num_cols = len(letters) * num_v_styles
        row_idx = color_idx * num_h_styles + h_style_idx
        col_idx = letter_idx * num_v_styles + v_style_idx
    else:
        # Letters on Y, Colors on X (default)
        num_rows = len(letters) * num_h_styles
        num_cols = len(colors) * num_v_styles
        row_idx = letter_idx * num_h_styles + h_style_idx
        col_idx = color_idx * num_v_styles + v_style_idx

    row_positions = calculate_row_positions(top, bottom, num_rows)
    col_positions = calculate_column_positions(left, right, num_cols)

    x = col_positions[col_idx] if col_idx < len(col_positions) else left
    y = row_positions[row_idx] if row_idx < len(row_positions) else top

    return (x, y)
