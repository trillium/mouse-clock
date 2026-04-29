"""
Dense grid overlay configuration.

Gets active letters and colors from mode config.
"""

from typing import List
from ...core.config import get_mode_config, get_setting
from ...core.constants import DEFAULT_TEXT_BG_COLOR


def get_dense_grid_colors() -> List[str]:
    """Get the list of active colors (rows)."""
    return get_mode_config("dense_grid", "colors")


def get_dense_grid_letters() -> List[str]:
    """Get the list of active letters (columns)."""
    return get_mode_config("dense_grid", "letters")


def get_dense_grid_spacing_x() -> int:
    """Get horizontal spacing between letters (pixels)."""
    return get_setting("dense_grid_spacing_x", 14)


def get_dense_grid_spacing_y() -> int:
    """Get vertical spacing between color rows (pixels)."""
    return get_setting("dense_grid_spacing_y", 14)


def get_text_bg_color() -> str:
    """Get the background color for dense grid."""
    return get_setting("dense_grid_text_bg_color", DEFAULT_TEXT_BG_COLOR)
