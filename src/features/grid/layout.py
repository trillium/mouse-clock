_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Grid overlay layout calculations.

Functions for calculating row and column positions.
"""

from typing import List

from ...core.config import get_setting
from .config import get_grid_letters
from .state import get_column_offset
from ..shared.layout import (
    calculate_row_positions,
    calculate_column_positions as _calculate_column_positions
)

# Re-export row positions directly (no grid-specific logic)
__all__ = ['get_visible_letters', 'calculate_row_positions', 'calculate_column_positions']


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


def calculate_column_positions(
    screen_left: float,
    screen_right: float,
    num_cols: int,
    center_x: float = None,
    offset_x: float = None
) -> List[float]:
    """
    Calculate X positions for each color column, distributed edge-to-edge.

    Args:
        screen_left: Left edge of screen
        screen_right: Right edge of screen
        num_cols: Number of columns to position
        center_x: Unused, kept for API compatibility
        offset_x: Horizontal offset to apply (defaults to global offset)

    Returns:
        List of X coordinates for each column
    """
    if offset_x is None:
        offset_x = get_column_offset()

    return _calculate_column_positions(
        screen_left, screen_right, num_cols,
        offset_x=offset_x,
        edge_to_edge=True
    )
