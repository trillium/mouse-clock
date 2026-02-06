_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Ray intersection calculations for the mouse clock system.

Functions for finding where rays intersect with lines, circles, and rectangles.
"""

import math
from typing import Tuple


def ray_line_intersection(
    ray_origin: Tuple[float, float],
    ray_angle_degrees: float,
    line_start: Tuple[float, float],
    line_end: Tuple[float, float]
) -> Tuple[float, float] | None:
    """
    Find where a ray intersects a line segment.

    Args:
        ray_origin: Starting point of the ray (x, y)
        ray_angle_degrees: Direction of ray in clock notation (0° = up)
        line_start: Start point of line segment (x, y)
        line_end: End point of line segment (x, y)

    Returns:
        Intersection point (x, y) or None if no intersection
    """
    ox, oy = ray_origin
    angle_rad = math.radians(ray_angle_degrees - 90)
    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)

    x1, y1 = line_start
    x2, y2 = line_end

    denom = dx * (y2 - y1) - dy * (x2 - x1)
    if abs(denom) < 1e-10:
        return None  # Parallel

    t = ((x1 - ox) * (y2 - y1) - (y1 - oy) * (x2 - x1)) / denom
    u = ((x1 - ox) * dy - (y1 - oy) * dx) / denom

    if t >= 0 and 0 <= u <= 1:
        return (ox + t * dx, oy + t * dy)
    return None


def ray_circle_intersection(
    origin: Tuple[float, float],
    angle_degrees: float,
    center: Tuple[float, float],
    radius: float
) -> Tuple[float, float] | None:
    """
    Find where a ray from origin intersects a circle.

    Args:
        origin: Starting point of the ray (x, y)
        angle_degrees: Direction in clock notation (0° = up)
        center: Center of the circle (x, y)
        radius: Radius of the circle

    Returns:
        Nearest intersection point (x, y) or None if no intersection
    """
    ox, oy = origin
    cx, cy = center
    angle_rad = math.radians(angle_degrees - 90)
    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)

    # Vector from origin to circle center
    fx, fy = ox - cx, oy - cy

    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - radius * radius

    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return None  # No intersection

    sqrt_disc = math.sqrt(discriminant)
    t1 = (-b - sqrt_disc) / (2 * a)
    t2 = (-b + sqrt_disc) / (2 * a)

    # Return nearest positive t (in front of ray)
    t = None
    if t1 >= 0:
        t = t1
    elif t2 >= 0:
        t = t2

    if t is None:
        return None

    return (ox + t * dx, oy + t * dy)


def ray_rect_intersection(
    origin: Tuple[float, float],
    angle_degrees: float,
    rect: Tuple[float, float, float, float]
) -> Tuple[float, float] | None:
    """
    Find where a ray intersects an axis-aligned rectangle.

    Args:
        origin: Starting point of the ray (x, y)
        angle_degrees: Direction in clock notation (0° = up)
        rect: Rectangle as (x, y, width, height)

    Returns:
        Nearest intersection point (x, y) or None if no intersection
    """
    rx, ry, rw, rh = rect

    # Define the four edges of the rectangle
    edges = [
        ((rx, ry), (rx + rw, ry)),           # Top
        ((rx + rw, ry), (rx + rw, ry + rh)), # Right
        ((rx, ry + rh), (rx + rw, ry + rh)), # Bottom
        ((rx, ry), (rx, ry + rh)),           # Left
    ]

    nearest = None
    min_dist = float('inf')
    ox, oy = origin

    for start, end in edges:
        hit = ray_line_intersection(origin, angle_degrees, start, end)
        if hit:
            dist = (hit[0] - ox) ** 2 + (hit[1] - oy) ** 2
            if dist < min_dist:
                min_dist = dist
                nearest = hit

    return nearest
