"""
Grid overlay configuration.

Default colors, letters, and configuration getters.
"""

from typing import List
from ...core.config import get_setting


# Default colors for columns (can be configured)
DEFAULT_GRID_COLORS = ["red", "blue", "green", "yellow", "purple"]

# Letters for rows
GRID_LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# Default text styling
DEFAULT_TEXT_COLOR = "00ff00ff"      # Bright green
DEFAULT_TEXT_BG_COLOR = "000000aa"   # Semi-transparent black


def get_text_color() -> str:
    """Get the text color for grid labels."""
    return get_setting("grid_text_color", DEFAULT_TEXT_COLOR)


def get_text_bg_color() -> str:
    """Get the background color for grid labels."""
    return get_setting("grid_text_bg_color", DEFAULT_TEXT_BG_COLOR)


def get_grid_colors() -> List[str]:
    """Get the list of colors for grid columns."""
    return get_setting("grid_colors", DEFAULT_GRID_COLORS)


def get_column_spacing() -> float:
    """Get spacing between color columns in pixels."""
    return get_setting("grid_column_spacing", 20)
