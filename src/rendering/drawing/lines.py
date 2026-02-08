"""
Line drawing infrastructure with configurable patterns.

Provides line styles (solid, dotted, dashed, etc.) and the rendering
logic for patterned lines.
"""

import math
from typing import Tuple, Dict, Literal
from talon.skia import Paint


# =============================================================================
# LINE STYLE DEFINITIONS
# =============================================================================

# Simple patterns: (dash_length, gap_length)
# Complex patterns: handled by dedicated drawing functions

LineStyle = Literal[
    # Simple dash/gap patterns
    "solid", "line", "dash", "dot", "tick", "blip", "long",
]

# Simple dash/gap patterns: (dash_length, gap_length)
# (0, 0) means solid/continuous
SIMPLE_PATTERNS: Dict[str, Tuple[float, float]] = {
    "solid": (0, 0),      # solid continuous line
    "line": (0, 0),       # alias for solid
    "dash": (12, 6),      # — — —
    "dot": (2, 6),        # · · ·
    "tick": (4, 14),      # short marks, wide spacing
    "blip": (1, 8),       # tiny dots
    "long": (20, 6),      # longer dashes
}


# =============================================================================
# INTERNAL HELPERS
# =============================================================================

def _get_line_geometry(
    start: Tuple[float, float],
    end: Tuple[float, float]
) -> Tuple[float, float, float, float, float]:
    """
    Calculate line geometry: direction, length, and perpendicular.
    Returns: (dx, dy, length, perp_x, perp_y)
    """
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx * dx + dy * dy)
    if length == 0:
        return 0, 0, 0, 0, 0
    dx /= length
    dy /= length
    # Perpendicular direction (90 degrees)
    perp_x, perp_y = -dy, dx
    return dx, dy, length, perp_x, perp_y


def _draw_simple_pattern(
    canvas,
    start: Tuple[float, float],
    end: Tuple[float, float],
    dash_len: float,
    gap_len: float
):
    """Draw a line with a simple dash/gap pattern."""
    x1, y1 = start
    dx, dy, length, _, _ = _get_line_geometry(start, end)
    if length == 0:
        return

    total_len = dash_len + gap_len
    pos = 0.0
    while pos < length:
        seg_start = (x1 + dx * pos, y1 + dy * pos)
        seg_end_pos = min(pos + dash_len, length)
        seg_end = (x1 + dx * seg_end_pos, y1 + dy * seg_end_pos)
        canvas.draw_line(seg_start[0], seg_start[1], seg_end[0], seg_end[1])
        pos += total_len


# =============================================================================
# PUBLIC API
# =============================================================================

def draw_line(
    canvas,
    start: Tuple[float, float],
    end: Tuple[float, float],
    color: str,
    thickness: float = 2,
    line_style: LineStyle = "line",
):
    """
    Draw a line segment with the specified style.

    Args:
        canvas: Talon canvas object
        start: Start point (x, y)
        end: End point (x, y)
        color: 8-digit RGBA hex color
        thickness: Line width in pixels
        line_style: Style name (solid, line, dash, dot, tick, blip, long)
    """
    paint = canvas.paint
    paint.color = color
    paint.style = Paint.Style.STROKE
    paint.stroke_width = thickness

    # Handle simple dash/gap patterns
    if line_style in SIMPLE_PATTERNS:
        pattern = SIMPLE_PATTERNS[line_style]
        if pattern == (0, 0):  # solid
            canvas.draw_line(start[0], start[1], end[0], end[1])
        else:
            _draw_simple_pattern(canvas, start, end, pattern[0], pattern[1])
    else:
        # Fallback to solid line
        canvas.draw_line(start[0], start[1], end[0], end[1])


def draw_dotted_line(
    canvas,
    start: Tuple[float, float],
    end: Tuple[float, float],
    color: str,
    thickness: float = 2
):
    """Draw a dotted line (small dots with gaps)."""
    draw_line(canvas, start, end, color, thickness, line_style="dot")


def draw_dashed_line(
    canvas,
    start: Tuple[float, float],
    end: Tuple[float, float],
    color: str,
    thickness: float = 2
):
    """Draw a dashed line (longer dashes with gaps)."""
    draw_line(canvas, start, end, color, thickness, line_style="dash")
