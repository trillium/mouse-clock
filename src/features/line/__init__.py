"""
Lettered Line Intersection Overlay.

Divides the screen into horizontal bands labeled with letters,
allowing voice-driven cursor positioning via line intersections.
"""

# Horizontal components
from .horizontal import (
    LineOverlayConfig,
    BAND_LETTERS,
    get_band_count,
    get_band_y_positions,
    get_y_for_letter,
    draw_horizontal_line,
    draw_band_labels,
    draw_all_lines,
    draw_single_line,
)

# Vertical components
from .vertical import (
    VERTICAL_COLORS,
    get_vertical_count,
    get_vertical_x_positions,
    get_x_for_color,
    draw_vertical_line,
    draw_all_verticals,
)

# Composite functions
from .composite import (
    draw_intersection_markers,
    draw_line_with_verticals,
)

__all__ = [
    # horizontal
    "LineOverlayConfig",
    "BAND_LETTERS",
    "get_band_count",
    "get_band_y_positions",
    "get_y_for_letter",
    "draw_horizontal_line",
    "draw_band_labels",
    "draw_all_lines",
    "draw_single_line",
    # vertical
    "VERTICAL_COLORS",
    "get_vertical_count",
    "get_vertical_x_positions",
    "get_x_for_color",
    "draw_vertical_line",
    "draw_all_verticals",
    # composite
    "draw_intersection_markers",
    "draw_line_with_verticals",
]
