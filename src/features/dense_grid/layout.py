"""
Dense grid layout calculations.

Columns = letters (A-Z), Rows = colors.
Edge-to-edge in both dimensions for maximum density.
"""

from ..shared.layout import calculate_row_positions as _calculate_row_positions
from ..shared.layout import calculate_column_positions as _calculate_column_positions

__all__ = ['calculate_row_positions', 'calculate_column_positions']


def calculate_row_positions(
    screen_top: float,
    screen_bottom: float,
    num_rows: int
):
    """Calculate Y positions for each color row, edge-to-edge."""
    return _calculate_row_positions(screen_top, screen_bottom, num_rows)


def calculate_column_positions(
    screen_left: float,
    screen_right: float,
    num_cols: int
):
    """Calculate X positions for each letter column, edge-to-edge."""
    return _calculate_column_positions(
        screen_left, screen_right, num_cols,
        edge_to_edge=True
    )
