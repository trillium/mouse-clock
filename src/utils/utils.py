import math
from typing import List, Tuple

def to_radians(angle: float) -> float:
    """Convert angle in degrees to radians."""
    return math.radians(angle)

def to_cartesian(angle: float) -> tuple[float, float]:
    """Convert an angle in degrees to Cartesian coordinates (x, y)."""
    angle_radians = to_radians(angle)
    return math.cos(angle_radians), math.sin(angle_radians)

def average_coordinates(points: List[tuple[float, float]]) -> tuple[float, float]:
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
    """Average a list of angles in degrees (360-degree)."""
    cartesian_points = [to_cartesian(angle) for angle in angles]
    avg_x, avg_y = average_coordinates(cartesian_points)
    return to_angle(avg_x, avg_y)

def get_letter_ordinal(letter: str) -> int:
    """Return the ordinal position of a letter (A=1, B=2, ...)."""
    return (ord(letter.upper()) - ord("A") + 1)

def letter_to_clock_angle(letter_ord: int) -> float:
    """
    Given a letter ordinal (A=1, B=2, ... L=12), return the corresponding clock angle in degrees.
    12 o'clock (A/1) is at -90 degrees, 3 o'clock (D/4) is 0 degrees, etc.
    """
    return (30 * letter_ord) % 360

def average_over_lengths(lengths: List[float]) -> float:
    """Return the average of a list, or 0 if the list is empty (avoids division by zero)."""
    if not lengths:
        return 0
    return sum(lengths) / len(lengths)

def get_radius_length(self, color_index: int, COLOR_LIST: list) -> float:
    """Calculate the radius length for a given color index."""
    return self.radius * (color_index + 1) / len(COLOR_LIST)

def average_clock_angles(number_list):
    if not number_list:
        return 0.0, 0.0
    radians = [math.radians(h * 30) for h in number_list]

    x = sum(math.cos(r) for r in radians) / len(radians)
    y = sum(math.sin(r) for r in radians) / len(radians)

    avg_angle_rad = math.atan2(y, x)
    avg_angle_deg = math.degrees(avg_angle_rad) % 360

    # Convert back to clock hour (optional)
    avg_hour = avg_angle_deg / 30
    return avg_hour, avg_angle_deg


def move_in_direction(clock_angle_deg, length, origin=(0, 0)):
    """
    Move `length` units in the direction of a clock-style angle (0° = 12 o'clock, clockwise).
    """
    angle_rad = math.radians((clock_angle_deg - 90) % 360)

    dx = length * math.cos(angle_rad)
    dy = length * math.sin(angle_rad)

    x0, y0 = origin
    return (x0 + dx, y0 + dy)