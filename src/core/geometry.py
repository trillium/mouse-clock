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


def number_to_angle(hour: int) -> float:
    """
    Convert a clock hour (1-12) to degrees.

    Clock hours map to angles: 1=30°, 2=60°, 3=90°, ..., 12=0°/360°.

    Args:
        hour: Clock hour from 1 to 12

    Returns:
        Angle in degrees

    Examples:
        number_to_angle(1) -> 30
        number_to_angle(3) -> 90
        number_to_angle(12) -> 0
    """
    return (hour * 30) % 360


def letter_to_angle(letter: str) -> float:
    """
    Convert a clock letter (A-L) to degrees.

    Clock letters map to angles: A=30°, B=60°, C=90°, ..., L=0°/360°.

    Args:
        letter: Clock letter A-L (case insensitive)

    Returns:
        Angle in degrees

    Examples:
        letter_to_angle('A') -> 30
        letter_to_angle('C') -> 90
        letter_to_angle('L') -> 0
    """
    position = ord(letter.upper()) - ord("A") + 1
    return (position * 30) % 360


def angle_to_letter(degrees: float) -> str:
    """
    Return the nearest clock letter for any angle.

    Maps angles to the nearest of 12 clock positions (A-L).

    Args:
        degrees: Angle in degrees

    Returns:
        Nearest clock letter (A-L)

    Examples:
        angle_to_letter(30) -> 'A'
        angle_to_letter(45) -> 'B' (rounds to nearest)
        angle_to_letter(0) -> 'L'
        angle_to_letter(350) -> 'L'
    """
    normalized = normalize_angle(degrees)
    # Each letter spans 30 degrees, centered on its position
    # A is centered at 30°, B at 60°, etc.
    # Round to nearest 30-degree increment
    position = round(normalized / 30)
    if position == 0 or position == 12:
        return "L"
    return chr(ord("A") + position - 1)


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
