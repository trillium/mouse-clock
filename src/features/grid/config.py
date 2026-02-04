"""
Grid overlay configuration.

Default colors, letters, and configuration getters.
Uses active configuration from core.config for colors, styles, and letters.
"""

from typing import List
from ...core.config import get_setting, get_active_colors, get_active_styles, get_active_letters


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
    """Get the list of active colors for grid columns."""
    return get_active_colors()


def get_grid_styles() -> List[str]:
    """Get the list of active line styles for the grid."""
    return get_active_styles()


def get_grid_letters() -> List[str]:
    """Get the list of active letters for grid rows."""
    return get_active_letters()


def get_column_spacing() -> float:
    """Get spacing between color columns in pixels."""
    return get_setting("grid_column_spacing", 20)
