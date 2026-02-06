_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Averaging utilities for angles and coordinates.

Functions for computing means of angles (handling wraparound correctly)
and coordinate points.
"""

import math
from typing import List, Tuple

from .angles import to_cartesian, to_angle


def average_coordinates(points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Average a list of Cartesian coordinates (x, y)."""
    if not points:
        return 0.0, 0.0
    avg_x = sum(x for x, y in points) / len(points)
    avg_y = sum(y for x, y in points) / len(points)
    return avg_x, avg_y


def average_angles(angles: List[float]) -> float:
    """
    Average a list of angles in degrees (360-degree system).

    Uses Cartesian coordinate conversion to handle wraparound correctly
    (e.g., averaging 350° and 10° gives 0°, not 180°).
    """
    cartesian_points = [to_cartesian(angle) for angle in angles]
    avg_x, avg_y = average_coordinates(cartesian_points)
    return to_angle(avg_x, avg_y)


def calculate_mean(values: List[float]) -> float:
    """
    Return the arithmetic mean of a list of values.

    Args:
        values: List of numeric values

    Returns:
        Mean value, or 0 if the list is empty
    """
    if not values:
        return 0.0
    return sum(values) / len(values)


def average_clock_angles(number_list: List[int]) -> Tuple[float, float]:
    """
    Average clock hour positions (1-12) and return both hour and degree values.

    Args:
        number_list: List of hour positions (1-12)

    Returns:
        Tuple of (average_hour, average_degrees)

    Example:
        [3, 9] -> (6.0, 180.0)  # Average of 3 o'clock and 9 o'clock
    """
    if not number_list:
        return 0.0, 0.0

    radians = [math.radians(h * 30) for h in number_list]

    x = sum(math.cos(r) for r in radians) / len(radians)
    y = sum(math.sin(r) for r in radians) / len(radians)

    avg_angle_rad = math.atan2(y, x)
    avg_angle_deg = math.degrees(avg_angle_rad) % 360

    # Convert back to clock hour
    avg_hour = avg_angle_deg / 30
    return avg_hour, avg_angle_deg
