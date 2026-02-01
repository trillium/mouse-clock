"""
Line drawing infrastructure with configurable patterns.

Provides line styles (solid, dotted, dashed, etc.) and the rendering
logic for patterned lines.
"""

import math
from typing import Tuple, Dict, Literal, List, Union, Callable
from talon.skia import Paint, Rect


# =============================================================================
# LINE STYLE DEFINITIONS
# =============================================================================

# Simple patterns: (dash_length, gap_length)
# Complex patterns: handled by dedicated drawing functions

LineStyle = Literal[
    # Simple dash/gap patterns
    "line", "dash", "dot", "tick", "blip", "long",
    # Multi-segment pattern
    "morse",
    # Structural styles
    "twin", "chain", "wave", "zig", "barb", "rail",
    "cross", "link", "bead", "spike", "hash", "saw",
]

# Simple dash/gap patterns: (dash_length, gap_length)
# (0, 0) means solid/continuous
SIMPLE_PATTERNS: Dict[str, Tuple[float, float]] = {
    "line": (0, 0),       # solid
    "dash": (12, 6),      # — — —
    "dot": (2, 6),        # · · ·
    "tick": (4, 14),      # short marks, wide spacing
    "blip": (1, 8),       # tiny dots
    "long": (20, 6),      # longer dashes
}

# Morse pattern: dash dash dot (multi-segment)
MORSE_PATTERN: List[Tuple[float, float]] = [
    (12, 4),  # dash
    (12, 4),  # dash
    (2, 10),  # dot + extra gap before repeat
]

# Legacy aliases for backwards compatibility
LINE_STYLE_PATTERNS = SIMPLE_PATTERNS


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


def _draw_morse(canvas, start: Tuple[float, float], end: Tuple[float, float]):
    """Draw morse pattern: dash dash dot."""
    x1, y1 = start
    dx, dy, length, _, _ = _get_line_geometry(start, end)
    if length == 0:
        return

    pos = 0.0
    pattern_idx = 0
    while pos < length:
        dash_len, gap_len = MORSE_PATTERN[pattern_idx]
        seg_start = (x1 + dx * pos, y1 + dy * pos)
        seg_end_pos = min(pos + dash_len, length)
        seg_end = (x1 + dx * seg_end_pos, y1 + dy * seg_end_pos)
        canvas.draw_line(seg_start[0], seg_start[1], seg_end[0], seg_end[1])
        pos += dash_len + gap_len
        pattern_idx = (pattern_idx + 1) % len(MORSE_PATTERN)


def _draw_twin(canvas, start: Tuple[float, float], end: Tuple[float, float], thickness: float):
    """Draw two parallel lines."""
    x1, y1 = start
    x2, y2 = end
    _, _, length, perp_x, perp_y = _get_line_geometry(start, end)
    if length == 0:
        return

    offset = thickness * 1.5
    # Draw two parallel lines
    canvas.draw_line(x1 + perp_x * offset, y1 + perp_y * offset,
                     x2 + perp_x * offset, y2 + perp_y * offset)
    canvas.draw_line(x1 - perp_x * offset, y1 - perp_y * offset,
                     x2 - perp_x * offset, y2 - perp_y * offset)


def _draw_chain(canvas, start: Tuple[float, float], end: Tuple[float, float], thickness: float):
    """Draw linked circles ○─○─○."""
    x1, y1 = start
    dx, dy, length, _, _ = _get_line_geometry(start, end)
    if length == 0:
        return

    radius = thickness * 2
    spacing = radius * 3
    pos = radius
    while pos < length:
        cx = x1 + dx * pos
        cy = y1 + dy * pos
        canvas.draw_circle(cx, cy, radius)
        pos += spacing


def _draw_wave(canvas, start: Tuple[float, float], end: Tuple[float, float], thickness: float):
    """Draw a sine wave line."""
    x1, y1 = start
    dx, dy, length, perp_x, perp_y = _get_line_geometry(start, end)
    if length == 0:
        return

    amplitude = thickness * 3
    wavelength = 20.0
    step = 2.0

    pos = 0.0
    prev_x, prev_y = x1, y1
    while pos <= length:
        wave_offset = math.sin(pos / wavelength * 2 * math.pi) * amplitude
        curr_x = x1 + dx * pos + perp_x * wave_offset
        curr_y = y1 + dy * pos + perp_y * wave_offset
        if pos > 0:
            canvas.draw_line(prev_x, prev_y, curr_x, curr_y)
        prev_x, prev_y = curr_x, curr_y
        pos += step


def _draw_zig(canvas, start: Tuple[float, float], end: Tuple[float, float], thickness: float):
    """Draw a zigzag /\/\/\ line."""
    x1, y1 = start
    dx, dy, length, perp_x, perp_y = _get_line_geometry(start, end)
    if length == 0:
        return

    amplitude = thickness * 3
    segment_len = 10.0

    pos = 0.0
    direction = 1
    prev_x = x1 + perp_x * amplitude * direction
    prev_y = y1 + perp_y * amplitude * direction

    while pos <= length:
        direction *= -1
        offset = amplitude * direction
        curr_x = x1 + dx * pos + perp_x * offset
        curr_y = y1 + dy * pos + perp_y * offset
        canvas.draw_line(prev_x, prev_y, curr_x, curr_y)
        prev_x, prev_y = curr_x, curr_y
        pos += segment_len


def _draw_barb(canvas, start: Tuple[float, float], end: Tuple[float, float], thickness: float):
    """Draw line with angled ticks/barbs."""
    x1, y1 = start
    x2, y2 = end
    dx, dy, length, perp_x, perp_y = _get_line_geometry(start, end)
    if length == 0:
        return

    # Draw main line
    canvas.draw_line(x1, y1, x2, y2)

    # Draw barbs
    barb_len = thickness * 4
    barb_spacing = 12.0
    pos = barb_spacing
    while pos < length:
        bx = x1 + dx * pos
        by = y1 + dy * pos
        # Barb goes back and to the side
        barb_end_x = bx - dx * barb_len * 0.5 + perp_x * barb_len
        barb_end_y = by - dy * barb_len * 0.5 + perp_y * barb_len
        canvas.draw_line(bx, by, barb_end_x, barb_end_y)
        pos += barb_spacing


def _draw_rail(canvas, start: Tuple[float, float], end: Tuple[float, float], thickness: float):
    """Draw railroad/ladder style ╫╫╫."""
    x1, y1 = start
    x2, y2 = end
    dx, dy, length, perp_x, perp_y = _get_line_geometry(start, end)
    if length == 0:
        return

    rail_offset = thickness * 2
    tie_spacing = 10.0
    tie_len = rail_offset * 2

    # Draw two parallel rails
    canvas.draw_line(x1 + perp_x * rail_offset, y1 + perp_y * rail_offset,
                     x2 + perp_x * rail_offset, y2 + perp_y * rail_offset)
    canvas.draw_line(x1 - perp_x * rail_offset, y1 - perp_y * rail_offset,
                     x2 - perp_x * rail_offset, y2 - perp_y * rail_offset)

    # Draw cross ties
    pos = 0.0
    while pos <= length:
        tx = x1 + dx * pos
        ty = y1 + dy * pos
        canvas.draw_line(tx - perp_x * tie_len/2, ty - perp_y * tie_len/2,
                         tx + perp_x * tie_len/2, ty + perp_y * tie_len/2)
        pos += tie_spacing


def _draw_cross(canvas, start: Tuple[float, float], end: Tuple[float, float], thickness: float):
    """Draw X marks along the line."""
    x1, y1 = start
    dx, dy, length, perp_x, perp_y = _get_line_geometry(start, end)
    if length == 0:
        return

    cross_size = thickness * 2
    spacing = cross_size * 4
    pos = cross_size
    while pos < length:
        cx = x1 + dx * pos
        cy = y1 + dy * pos
        # Draw X
        canvas.draw_line(cx - cross_size, cy - cross_size, cx + cross_size, cy + cross_size)
        canvas.draw_line(cx - cross_size, cy + cross_size, cx + cross_size, cy - cross_size)
        pos += spacing


def _draw_link(canvas, start: Tuple[float, float], end: Tuple[float, float], thickness: float):
    """Draw interlocking loops - DISABLED, drawing simple dashed line instead."""
    # TODO: Fix link style rendering - currently too wide
    # For now, just draw a simple pattern as placeholder
    _draw_simple_pattern(canvas, start, end, 6, 6)  # Simple dash pattern


def _draw_bead(canvas, start: Tuple[float, float], end: Tuple[float, float], thickness: float):
    """Draw beads connected by thin lines ●─●─●."""
    x1, y1 = start
    x2, y2 = end
    dx, dy, length, _, _ = _get_line_geometry(start, end)
    if length == 0:
        return

    bead_radius = thickness * 1.5
    spacing = bead_radius * 5

    # Draw thin connecting line
    old_width = canvas.paint.stroke_width
    canvas.paint.stroke_width = thickness * 0.5
    canvas.draw_line(x1, y1, x2, y2)
    canvas.paint.stroke_width = old_width

    # Draw beads
    canvas.paint.style = Paint.Style.FILL
    pos = bead_radius
    while pos < length:
        bx = x1 + dx * pos
        by = y1 + dy * pos
        canvas.draw_circle(bx, by, bead_radius)
        pos += spacing
    canvas.paint.style = Paint.Style.STROKE


def _draw_spike(canvas, start: Tuple[float, float], end: Tuple[float, float], thickness: float):
    """Draw flat line with periodic spikes (heartbeat)."""
    x1, y1 = start
    x2, y2 = end
    dx, dy, length, perp_x, perp_y = _get_line_geometry(start, end)
    if length == 0:
        return

    spike_height = thickness * 6
    spike_spacing = 30.0
    spike_width = 4.0

    pos = 0.0
    prev_x, prev_y = x1, y1
    while pos <= length:
        next_spike = ((pos // spike_spacing) + 1) * spike_spacing
        if next_spike <= length and pos < next_spike <= pos + spike_width * 3:
            # Draw spike
            mid = next_spike
            curr_x = x1 + dx * (mid - spike_width)
            curr_y = y1 + dy * (mid - spike_width)
            canvas.draw_line(prev_x, prev_y, curr_x, curr_y)

            peak_x = x1 + dx * mid + perp_x * spike_height
            peak_y = y1 + dy * mid + perp_y * spike_height
            canvas.draw_line(curr_x, curr_y, peak_x, peak_y)

            curr_x = x1 + dx * (mid + spike_width)
            curr_y = y1 + dy * (mid + spike_width)
            canvas.draw_line(peak_x, peak_y, curr_x, curr_y)

            prev_x, prev_y = curr_x, curr_y
            pos = mid + spike_width
        else:
            pos += 2

    # Draw remaining line to end
    canvas.draw_line(prev_x, prev_y, x2, y2)


def _draw_hash(canvas, start: Tuple[float, float], end: Tuple[float, float], thickness: float):
    """Draw # marks along the line."""
    x1, y1 = start
    dx, dy, length, perp_x, perp_y = _get_line_geometry(start, end)
    if length == 0:
        return

    size = thickness * 3
    spacing = size * 4
    pos = size
    while pos < length:
        cx = x1 + dx * pos
        cy = y1 + dy * pos
        # Draw # (two horizontal, two vertical relative to line direction)
        offset = size * 0.4
        # Parallel lines
        for d in [-offset, offset]:
            lx = cx + perp_x * d
            ly = cy + perp_y * d
            canvas.draw_line(lx - dx * size, ly - dy * size,
                             lx + dx * size, ly + dy * size)
        # Perpendicular lines
        for d in [-offset, offset]:
            lx = cx + dx * d
            ly = cy + dy * d
            canvas.draw_line(lx - perp_x * size, ly - perp_y * size,
                             lx + perp_x * size, ly + perp_y * size)
        pos += spacing


def _draw_saw(canvas, start: Tuple[float, float], end: Tuple[float, float], thickness: float):
    """Draw asymmetric sawtooth pattern."""
    x1, y1 = start
    dx, dy, length, perp_x, perp_y = _get_line_geometry(start, end)
    if length == 0:
        return

    tooth_height = thickness * 4
    tooth_width = 12.0

    pos = 0.0
    prev_x, prev_y = x1, y1
    while pos < length:
        # Gradual rise
        rise_end = min(pos + tooth_width * 0.8, length)
        rise_x = x1 + dx * rise_end + perp_x * tooth_height
        rise_y = y1 + dy * rise_end + perp_y * tooth_height
        canvas.draw_line(prev_x, prev_y, rise_x, rise_y)

        # Sharp drop
        drop_end = min(pos + tooth_width, length)
        drop_x = x1 + dx * drop_end
        drop_y = y1 + dy * drop_end
        canvas.draw_line(rise_x, rise_y, drop_x, drop_y)

        prev_x, prev_y = drop_x, drop_y
        pos += tooth_width


# =============================================================================
# PUBLIC API
# =============================================================================

# Mapping of structural styles to their drawing functions
STRUCTURAL_STYLES: Dict[str, Callable] = {
    "morse": lambda c, s, e, _: _draw_morse(c, s, e),
    "twin": _draw_twin,
    "chain": _draw_chain,
    "wave": _draw_wave,
    "zig": _draw_zig,
    "barb": _draw_barb,
    "rail": _draw_rail,
    "cross": _draw_cross,
    "link": _draw_link,
    "bead": _draw_bead,
    "spike": _draw_spike,
    "hash": _draw_hash,
    "saw": _draw_saw,
}


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
        line_style: Style name (line, dash, dot, tick, blip, long, morse,
                    twin, chain, wave, zig, barb, rail, cross, link,
                    bead, spike, hash, saw)
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
    # Handle structural styles
    elif line_style in STRUCTURAL_STYLES:
        STRUCTURAL_STYLES[line_style](canvas, start, end, thickness)
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
