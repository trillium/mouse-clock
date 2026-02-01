"""
Grid Overlay for MouseClock.

Renders a letter/color grid for precise targeting:
- Y-axis: Letters (A-Z) with horizontal lines
- X-axis: Colors with vertical lines
- Intersections provide target points
"""

# Configuration
from .config import (
    DEFAULT_GRID_COLORS,
    GRID_LETTERS,
    DEFAULT_TEXT_COLOR,
    DEFAULT_TEXT_BG_COLOR,
    get_text_color,
    get_text_bg_color,
    get_grid_colors,
    get_column_spacing,
)

# State management
from .state import (
    get_column_offset,
    get_target_offset,
    set_column_offset,
    shift_columns_left,
    shift_columns_right,
    reset_column_offset,
    reset_grid_state,
    end_hiss_session,
    end_shush_session,
    grid_hiss,
    grid_shush,
    get_hiss_direction,
    get_shush_mode,
    update_offset_animation,
)

# Layout calculations
from .layout import (
    get_visible_letters,
    calculate_row_positions,
    calculate_column_positions,
)

# Rendering
from .render import (
    draw_grid_overlay,
)

# Targeting
from .targeting import (
    get_grid_target,
)

__all__ = [
    # config
    "DEFAULT_GRID_COLORS",
    "GRID_LETTERS",
    "DEFAULT_TEXT_COLOR",
    "DEFAULT_TEXT_BG_COLOR",
    "get_text_color",
    "get_text_bg_color",
    "get_grid_colors",
    "get_column_spacing",
    # state
    "get_column_offset",
    "get_target_offset",
    "set_column_offset",
    "shift_columns_left",
    "shift_columns_right",
    "reset_column_offset",
    "reset_grid_state",
    "end_hiss_session",
    "end_shush_session",
    "grid_hiss",
    "grid_shush",
    "get_hiss_direction",
    "get_shush_mode",
    "update_offset_animation",
    # layout
    "get_visible_letters",
    "calculate_row_positions",
    "calculate_column_positions",
    # render
    "draw_grid_overlay",
    # targeting
    "get_grid_target",
]
