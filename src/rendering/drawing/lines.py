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

# Pattern format: (dash_length, gap_length)
# - dash_length: how many pixels to draw
# - gap_length: how many pixels to skip
# - (0, 0) means solid/continuous

LINE_STYLE_PATTERNS: Dict[str, Tuple[float, float]] = {
    "solid": (0, 0),
    "dotted": (2, 6),
    "dashed": (12, 6),
}

# Type for valid line styles - keep in sync with LINE_STYLE_PATTERNS keys
LineStyle = Literal["solid", "dotted", "dashed"]


# =============================================================================
# INTERNAL HELPERS
# =============================================================================

def _draw_patterned_line(
    canvas,
    start: Tuple[float, float],
    end: Tuple[float, float],
    dash_len: float,
    gap_len: float
):
    """
    Draw a line with a dash/gap pattern.

    Walks along the line from start to end, drawing segments of dash_len
    pixels then skipping gap_len pixels.
    """
    x1, y1 = start
    x2, y2 = end
    total_len = dash_len + gap_len

    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx * dx + dy * dy)
    if length == 0:
        return

    # Normalize direction
    dx /= length
    dy /= length

    # Draw dashes
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
    line_style: LineStyle = "solid",
):
    """
    Draw a line segment with the specified style.

    Args:
        canvas: Talon canvas object
        start: Start point (x, y)
        end: End point (x, y)
        color: 8-digit RGBA hex color
        thickness: Line width in pixels
        line_style: "solid", "dotted", or "dashed"
    """
    paint = canvas.paint
    paint.color = color
    paint.style = Paint.Style.STROKE
    paint.stroke_width = thickness

    if line_style in LINE_STYLE_PATTERNS and line_style != "solid":
        pattern = LINE_STYLE_PATTERNS[line_style]
        _draw_patterned_line(canvas, start, end, pattern[0], pattern[1])
    else:
        canvas.draw_line(start[0], start[1], end[0], end[1])


def draw_dotted_line(
    canvas,
    start: Tuple[float, float],
    end: Tuple[float, float],
    color: str,
    thickness: float = 2
):
    """Draw a dotted line (small dots with gaps)."""
    draw_line(canvas, start, end, color, thickness, line_style="dotted")


def draw_dashed_line(
    canvas,
    start: Tuple[float, float],
    end: Tuple[float, float],
    color: str,
    thickness: float = 2
):
    """Draw a dashed line (longer dashes with gaps)."""
    draw_line(canvas, start, end, color, thickness, line_style="dashed")
