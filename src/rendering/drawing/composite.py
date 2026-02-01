"""
Composite shape drawing utilities.

Higher-level drawing functions that combine basic primitives
for clock rays, concentric shapes, etc.
"""

import math
from typing import Tuple, List

from .primitives import draw_line, draw_circle, draw_rect


def draw_ray(
    canvas,
    origin: Tuple[float, float],
    angle_degrees: float,
    length: float,
    color: str,
    thickness: float = 2,
    dashed: bool = False
):
    """
    Draw a ray from origin at specified angle.

    Args:
        canvas: Talon canvas object
        origin: Start point (x, y)
        angle_degrees: Direction in clock notation (0° = up)
        length: Length of ray in pixels
        color: 8-digit RGBA hex color
        thickness: Line width
        dashed: Whether to draw dashed
    """
    ox, oy = origin
    # Convert clock angle to math angle
    angle_rad = math.radians(angle_degrees - 90)
    ex = ox + length * math.cos(angle_rad)
    ey = oy + length * math.sin(angle_rad)
    draw_line(canvas, origin, (ex, ey), color, thickness, dashed)


def draw_concentric_circles(
    canvas,
    center: Tuple[float, float],
    radii: List[float],
    colors: List[str],
    thickness: float = 2
):
    """
    Draw multiple circles with different colors.

    Args:
        canvas: Talon canvas object
        center: Center point (x, y)
        radii: List of radii (smallest to largest)
        colors: List of colors (one per radius)
        thickness: Line width
    """
    for radius, color in zip(radii, colors):
        if radius > 0:
            draw_circle(canvas, center, radius, color, thickness)


def draw_concentric_rects(
    canvas,
    center: Tuple[float, float],
    sizes: List[Tuple[float, float]],
    colors: List[str],
    thickness: float = 2
):
    """
    Draw multiple rectangles with different colors, centered.

    Args:
        canvas: Talon canvas object
        center: Center point (x, y)
        sizes: List of (width, height) tuples
        colors: List of colors (one per size)
        thickness: Line width
    """
    cx, cy = center
    for (w, h), color in zip(sizes, colors):
        rect = (cx - w / 2, cy - h / 2, w, h)
        draw_rect(canvas, rect, color, thickness)


def draw_clock_rays(
    canvas,
    center: Tuple[float, float],
    length: float,
    color: str,
    thickness: float = 2,
    dashed: bool = False
):
    """
    Draw all 12 clock-hour directional rays.

    Args:
        canvas: Talon canvas object
        center: Center point (x, y)
        length: Length of each ray
        color: 8-digit RGBA hex color
        thickness: Line width
        dashed: Whether to draw dashed
    """
    for hour in range(1, 13):
        angle = hour * 30  # 30° per hour
        draw_ray(canvas, center, angle, length, color, thickness, dashed)
