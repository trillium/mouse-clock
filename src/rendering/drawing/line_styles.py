"""Structural line style drawing functions for the line drawing API."""

import math
from typing import Tuple, Dict, Callable
from talon.skia import Paint
from .lines import _get_line_geometry, _draw_simple_pattern, _draw_morse

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
    """Draw linked circles."""
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
    """Draw a zigzag line."""
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
    """Draw railroad/ladder style."""
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
    _draw_simple_pattern(canvas, start, end, 6, 6)

def _draw_bead(canvas, start: Tuple[float, float], end: Tuple[float, float], thickness: float):
    """Draw beads connected by thin lines."""
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
