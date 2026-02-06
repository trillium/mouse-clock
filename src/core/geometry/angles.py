_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Angle conversion utilities for the mouse clock system.

Pure mathematical functions for converting between degrees, radians,
and Cartesian coordinates.
"""

import math
from typing import Tuple


def to_radians(angle: float) -> float:
    """Convert angle in degrees to radians."""
    return math.radians(angle)


def to_cartesian(angle: float) -> Tuple[float, float]:
    """Convert an angle in degrees to Cartesian coordinates (x, y)."""
    angle_radians = to_radians(angle)
    return math.cos(angle_radians), math.sin(angle_radians)


def to_angle(x: float, y: float) -> float:
    """Convert Cartesian coordinates (x, y) back to an angle in degrees."""
    angle_radians = math.atan2(y, x)
    return math.degrees(angle_radians)


def normalize_angle(degrees: float) -> float:
    """
    Normalize an angle to the 0-360 range.

    Args:
        degrees: Any angle in degrees (can be negative or > 360)

    Returns:
        Angle normalized to 0-360 range

    Examples:
        normalize_angle(450) -> 90
        normalize_angle(-30) -> 330
        normalize_angle(360) -> 0
    """
    result = degrees % 360
    return 0.0 if result == 360 else result


def opposite_angle(degrees: float) -> float:
    """
    Return the opposite direction (angle + 180°, normalized).

    Args:
        degrees: Angle in degrees

    Returns:
        Opposite angle, normalized to 0-360 range

    Examples:
        opposite_angle(0) -> 180
        opposite_angle(270) -> 90
        opposite_angle(350) -> 170
    """
    return normalize_angle(degrees + 180)
