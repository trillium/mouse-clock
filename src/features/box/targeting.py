"""
Concentric box targeting functions.

Calculate target positions from color + direction combinations.
"""

from typing import Tuple

from ...core.geometry import number_to_angle, ray_rect_intersection
from .config import calculate_box_sizes


def get_size_for_color(color_name: str) -> Tuple[float, float]:
    """
    Get the size of the box for a given color.

    Args:
        color_name: Color name (center, red, blue, etc.)

    Returns:
        (width, height) of that color's box
    """
    color_names = ["center", "red", "blue", "green", "yellow", "purple", "pink"]

    try:
        index = color_names.index(color_name.lower())
    except ValueError:
        return None

    sizes = calculate_box_sizes()
    if index < len(sizes):
        return sizes[index]

    return None


def get_target_position(
    center: Tuple[float, float],
    color_name: str,
    direction: int
) -> Tuple[float, float]:
    """
    Compute intersection point for targeting.

    Args:
        center: Center point (x, y)
        color_name: Color name of target box (center, red, blue, etc.)
        direction: Clock hour (1-12) or letter position

    Returns:
        (x, y) intersection point or center if not found
    """
    # Get the box index for this color
    color_names = ["center", "red", "blue", "green", "yellow", "purple", "pink"]

    try:
        box_index = color_names.index(color_name.lower())
    except ValueError:
        return center

    # Get the box size
    sizes = calculate_box_sizes()
    if box_index >= len(sizes):
        return center

    w, h = sizes[box_index]
    cx, cy = center

    # Get angle for direction
    angle = number_to_angle(direction)

    # Compute rect for this box
    rect = (cx - w / 2, cy - h / 2, w, h)

    # Find intersection
    intersection = ray_rect_intersection((cx, cy), angle, rect)

    if intersection:
        return intersection

    return center


def get_target_from_letter(
    center: Tuple[float, float],
    color_name: str,
    letter: str
) -> Tuple[float, float]:
    """
    Compute intersection for color + letter targeting.

    Args:
        center: Center point (x, y)
        color_name: Color name of target box
        letter: Clock letter (A-L)

    Returns:
        (x, y) intersection point
    """
    # Convert letter to clock position
    letter_upper = letter.upper()
    if letter_upper < 'A' or letter_upper > 'L':
        return center

    # A=1, B=2, ..., L=12
    position = ord(letter_upper) - ord('A') + 1
    if position > 12:
        position = 12

    return get_target_position(center, color_name, position)
