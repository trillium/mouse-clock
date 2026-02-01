"""
Basic shape drawing primitives for overlay systems.

Provides a consistent API for drawing lines, circles, rectangles, dots,
crosses, and text on Talon canvas objects.
"""

# Basic primitives
from .primitives import (
    draw_line,
    draw_dotted_line,
    draw_dashed_line,
    draw_circle,
    draw_rect,
    draw_dot,
    draw_cross,
    draw_text,
    LineStyle,
    LINE_STYLE_PATTERNS,
)

# Composite shapes
from .composite import (
    draw_ray,
    draw_concentric_circles,
    draw_concentric_rects,
    draw_clock_rays,
)

__all__ = [
    # primitives
    "draw_line",
    "draw_dotted_line",
    "draw_dashed_line",
    "draw_circle",
    "draw_rect",
    "draw_dot",
    "draw_cross",
    "draw_text",
    "LineStyle",
    "LINE_STYLE_PATTERNS",
    # composite
    "draw_ray",
    "draw_concentric_circles",
    "draw_concentric_rects",
    "draw_clock_rays",
]
