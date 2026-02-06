"""
Shared utilities for feature modules.

Common functions extracted from grid, clock_letters, and box features.
"""

from .layout import calculate_row_positions, calculate_column_positions
from .alpha import apply_alpha, set_alpha, get_alpha
from .utils import safe_index, safe_index_or_none
from .config import DEFAULT_TEXT_COLOR, DEFAULT_TEXT_BG_COLOR
