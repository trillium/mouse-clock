_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Ring drawing functions for the mouse clock.

Functions for drawing concentric colored rings and clock position dots.
"""

from talon.skia import Paint

from ...core import config
from .utils import calculate_ring_radius, calculate_clock_position


def draw_concentric_rings(canvas, center_x: float, center_y: float, radius: float, color_list: list[str]):
    """
    Draw the concentric colored rings of the mouse clock.

    Args:
        canvas: Talon canvas object
        center_x: X coordinate of clock center
        center_y: Y coordinate of clock center
        radius: Outer radius of the clock
        color_list: List of color hex strings for the rings
    """
    paint = canvas.paint
    num_rings = len(color_list)

    for i in range(num_rings):
        paint.color = color_list[i]
        ring_radius = calculate_ring_radius(i, num_rings, radius)
        canvas.draw_circle(center_x, center_y, ring_radius)


def draw_clock_position_dots(
    canvas,
    center_x: float,
    center_y: float,
    radius: float,
    color_list: list[str],
    dot_radius: float = None
):
    """
    Draw colored dots at each of the 12 clock positions on different rings.

    Args:
        canvas: Talon canvas object
        center_x: X coordinate of clock center
        center_y: Y coordinate of clock center
        radius: Outer radius of the clock
        color_list: List of color hex strings for each ring of dots
        dot_radius: Size of each dot (defaults to DEFAULT_DOT_RADIUS)
    """
    if dot_radius is None:
        dot_radius = config.DEFAULT_DOT_RADIUS

    paint = canvas.paint
    paint.style = Paint.Style.FILL  # Use FILL instead of STROKE for solid dots

    num_rings = len(color_list)

    # For each color ring
    for ring_index in range(num_rings):
        paint.color = color_list[ring_index]
        ring_radius = calculate_ring_radius(ring_index, num_rings, radius)

        # Draw a dot at each of the 12 clock positions on this ring
        for position in range(1, 13):  # 1-12 for clock positions
            x, y = calculate_clock_position(position, ring_radius, center_x, center_y)
            canvas.draw_circle(x, y, dot_radius)
