"""
Geometric calculations for the mouse clock system.

This module provides pure mathematical functions for angle conversions,
averaging, and coordinate transformations used in mouse positioning.
"""

import math
from typing import List, Tuple


def to_radians(angle: float) -> float:
    """Convert angle in degrees to radians."""
    return math.radians(angle)


def to_cartesian(angle: float) -> Tuple[float, float]:
    """Convert an angle in degrees to Cartesian coordinates (x, y)."""
    angle_radians = to_radians(angle)
    return math.cos(angle_radians), math.sin(angle_radians)


def average_coordinates(points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Average a list of Cartesian coordinates (x, y)."""
    if not points:
        return 0.0, 0.0
    avg_x = sum(x for x, y in points) / len(points)
    avg_y = sum(y for x, y in points) / len(points)
    return avg_x, avg_y


def to_angle(x: float, y: float) -> float:
    """Convert Cartesian coordinates (x, y) back to an angle in degrees."""
    angle_radians = math.atan2(y, x)
    return math.degrees(angle_radians)


def average_angles(angles: List[float]) -> float:
    """
    Average a list of angles in degrees (360-degree system).

    Uses Cartesian coordinate conversion to handle wraparound correctly
    (e.g., averaging 350° and 10° gives 0°, not 180°).
    """
    cartesian_points = [to_cartesian(angle) for angle in angles]
    avg_x, avg_y = average_coordinates(cartesian_points)
    return to_angle(avg_x, avg_y)


def letter_to_position(letter: str) -> int:
    """
    Return the position of a letter in the alphabet (1-indexed).

    Args:
        letter: A letter A-Z (case insensitive)

    Returns:
        Position number (A=1, B=2, ..., Z=26)
    """
    return ord(letter.upper()) - ord("A") + 1


def letter_to_clock_angle(letter_position: int) -> float:
    """
    Given a letter position (1-12 for A-L), return the corresponding clock angle in degrees.

    Args:
        letter_position: Position of letter (1=A at 12 o'clock, 2=B, ..., 12=L)

    Returns:
        Angle in degrees (0° = 3 o'clock, 90° = 6 o'clock, -90° = 12 o'clock)

    Examples:
        1 (A) at 12 o'clock -> 30° (after modulo)
        4 (D) at 3 o'clock  -> 120° (after modulo)
    """
    return (30 * letter_position) % 360


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
