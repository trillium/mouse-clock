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


