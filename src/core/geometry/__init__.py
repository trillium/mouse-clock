"""
Geometric calculations for the mouse clock system.

This module provides pure mathematical functions for angle conversions,
averaging, and coordinate transformations used in mouse positioning.
"""

# Angle conversions
from .angles import (
    to_radians,
    to_cartesian,
    to_angle,
    normalize_angle,
    opposite_angle,
)

# Clock notation conversions
from .clock import (
    number_to_angle,
    letter_to_angle,
    angle_to_letter,
    letter_to_position,
    letter_to_clock_angle,
)

# Averaging utilities
from .averaging import (
    average_coordinates,
    average_angles,
    calculate_mean,
    average_clock_angles,
)

# Coordinate calculations
from .coordinates import (
    move_in_direction,
    distance_between,
    point_on_circle,
    clamp_to_bounds,
)

# Ray intersections
from .intersections import (
    ray_line_intersection,
    ray_circle_intersection,
    ray_rect_intersection,
)

__all__ = [
    # angles
    "to_radians",
    "to_cartesian",
    "to_angle",
    "normalize_angle",
    "opposite_angle",
    # clock
    "number_to_angle",
    "letter_to_angle",
    "angle_to_letter",
    "letter_to_position",
    "letter_to_clock_angle",
    # averaging
    "average_coordinates",
    "average_angles",
    "calculate_mean",
    "average_clock_angles",
    # coordinates
    "move_in_direction",
    "distance_between",
    "point_on_circle",
    "clamp_to_bounds",
    # intersections
    "ray_line_intersection",
    "ray_circle_intersection",
    "ray_rect_intersection",
]
