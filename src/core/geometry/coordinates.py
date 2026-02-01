"""
Coordinate calculation utilities for the mouse clock system.

Functions for moving in directions, calculating distances,
and working with points on circles.
"""

import math
from typing import Tuple


def move_in_direction(clock_angle_degrees: float, distance: float, origin: Tuple[float, float] = (0, 0)) -> Tuple[float, float]:
    """
    Calculate a point at a given distance in a clock-style direction.

    Args:
        clock_angle_degrees: Angle in clock notation (0° = 12 o'clock, clockwise)
        distance: Distance to move in pixels
        origin: Starting point (x, y), defaults to (0, 0)

    Returns:
        Tuple of (x, y) coordinates of the new point

    Example:
        move_in_direction(0, 100, (0, 0))    # Move 100 pixels up
        move_in_direction(90, 50, (10, 10))  # Move 50 pixels right from (10, 10)
    """
    # Convert clock angle (0° = up) to math angle (0° = right)
    angle_rad = math.radians((clock_angle_degrees - 90) % 360)

    dx = distance * math.cos(angle_rad)
    dy = distance * math.sin(angle_rad)

    x0, y0 = origin
    return (x0 + dx, y0 + dy)


def distance_between(point_a: Tuple[float, float], point_b: Tuple[float, float]) -> float:
    """
    Calculate the Euclidean distance between two points.

    Args:
        point_a: First point (x, y)
        point_b: Second point (x, y)

    Returns:
        Distance between the two points

    Examples:
        distance_between((0, 0), (3, 4)) -> 5.0
        distance_between((1, 1), (1, 1)) -> 0.0
    """
    x1, y1 = point_a
    x2, y2 = point_b
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def point_on_circle(center: Tuple[float, float], radius: float, angle_degrees: float) -> Tuple[float, float]:
    """
    Calculate a point on a circle's perimeter at a given angle.

    Uses clock-style angle notation where 0° is up (12 o'clock) and
    angles increase clockwise.

    Args:
        center: Center point of the circle (x, y)
        radius: Radius of the circle
        angle_degrees: Angle in clock notation (0° = up, 90° = right)

    Returns:
        Point (x, y) on the circle perimeter

    Examples:
        point_on_circle((100, 100), 50, 0)   -> (100, 50)  # Top
        point_on_circle((100, 100), 50, 90)  -> (150, 100) # Right
        point_on_circle((100, 100), 50, 180) -> (100, 150) # Bottom
    """
    # Convert clock angle to math angle (0° = up becomes -90° in standard math)
    # In screen coordinates, Y increases downward
    angle_rad = math.radians(angle_degrees - 90)

    cx, cy = center
    x = cx + radius * math.cos(angle_rad)
    y = cy + radius * math.sin(angle_rad)
    return (x, y)


def clamp_to_bounds(point: Tuple[float, float], rect: Tuple[float, float, float, float]) -> Tuple[float, float]:
    """
    Constrain a point to stay within a rectangle.

    Args:
        point: Point to clamp (x, y)
        rect: Rectangle bounds as (x, y, width, height)

    Returns:
        Clamped point (x, y) that lies within the rectangle

    Examples:
        clamp_to_bounds((150, 50), (0, 0, 100, 100)) -> (100, 50)
        clamp_to_bounds((-10, 50), (0, 0, 100, 100)) -> (0, 50)
        clamp_to_bounds((50, 50), (0, 0, 100, 100)) -> (50, 50)
    """
    x, y = point
    rx, ry, rw, rh = rect

    clamped_x = max(rx, min(x, rx + rw))
    clamped_y = max(ry, min(y, ry + rh))

    return (clamped_x, clamped_y)
