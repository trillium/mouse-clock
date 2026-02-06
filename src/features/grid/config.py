_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Grid overlay configuration.

Default colors, letters, and configuration getters.
Uses active configuration from core.config for colors, styles, and letters.
"""

from typing import List
from ...core.config import get_setting, get_mode_config
from ..shared.config import DEFAULT_TEXT_COLOR, DEFAULT_TEXT_BG_COLOR


def get_text_color() -> str:
    """Get the text color for grid labels."""
    return get_setting("grid_text_color", DEFAULT_TEXT_COLOR)


def get_text_bg_color() -> str:
    """Get the background color for grid labels."""
    return get_setting("grid_text_bg_color", DEFAULT_TEXT_BG_COLOR)


def get_grid_colors() -> List[str]:
    """Get the list of active colors for grid columns."""
    return get_mode_config("grid", "colors")


def get_grid_styles() -> List[str]:
    """Get the list of active line styles for the grid (legacy, uses horizontal)."""
    return get_mode_config("grid", "horizontal_styles")


def get_horizontal_styles() -> List[str]:
    """Get the list of active styles for horizontal (letter) lines."""
    return get_mode_config("grid", "horizontal_styles")


def get_vertical_styles() -> List[str]:
    """Get the list of active styles for vertical (color) lines."""
    return get_mode_config("grid", "vertical_styles")


def get_grid_letters() -> List[str]:
    """Get the list of active letters for grid rows."""
    return get_mode_config("grid", "letters")


def get_column_spacing() -> float:
    """Get spacing between color columns in pixels."""
    return get_setting("grid_column_spacing", 20)
