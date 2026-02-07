"""
Core mouse clock logic without Talon dependencies.

This module contains the MouseClockCore class for calculating mouse positions
based on clock face letters and color rings.
"""

import math
from typing import List, Tuple, Optional

from . import geometry
from . import config
from .logger import log_info, log_separator
from .animation import RadiusAnimator


class MouseClockCore:
    """
    Core mouse clock logic without Talon dependencies.

    This class handles the mathematical calculations for mouse positioning
    based on clock face inputs and color rings.
    """

    def __init__(self, center_x: float = 0, center_y: float = 0, radius: int = None):
        """
        Initialize the mouse clock core.

        Args:
            center_x: X coordinate of the clock center
            center_y: Y coordinate of the clock center
            radius: Outer radius of the clock (defaults to DEFAULT_RADIUS)
        """
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius if radius is not None else config.DEFAULT_RADIUS
        self.target_radius = self.radius

        # Animation controller
        self._animator = RadiusAnimator()

        # State
        self.history: List[Tuple[float, float]] = []
        self.last_command: Tuple[List[str], List[str]] = ([], [])
        self.last_letters: List[str] = []
        self.last_colors: List[str] = []
        self.original_command: Tuple[List[str], List[str]] = ([], [])

    def update_center(self, x: float, y: float):
        """Update the center position of the clock."""
        self.center_x = x
        self.center_y = y

    def calculate_edge_distance(self, angle_degrees: float, screen_rect: Tuple[float, float, float, float]) -> float:
        """
        Calculate distance from center to screen edge in given direction.

        Args:
            angle_degrees: Angle in degrees (clock-style, 0=12 o'clock)
            screen_rect: Tuple of (left, top, right, bottom) screen bounds

        Returns:
            Distance in pixels from center to screen edge in that direction
        """
        screen_left, screen_top, screen_right, screen_bottom = screen_rect

        # Convert clock angle to standard math angle (radians)
        angle_rad = math.radians((angle_degrees - 90) % 360)

        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)

        # Calculate distance to each edge
        distances = []

        if dx > 0:
            distances.append((screen_right - self.center_x) / dx)
        if dx < 0:
            distances.append((screen_left - self.center_x) / dx)
        if dy > 0:
            distances.append((screen_bottom - self.center_y) / dy)
        if dy < 0:
            distances.append((screen_top - self.center_y) / dy)

        # Return the minimum positive distance (the edge we'll hit first)
        valid_distances = [d for d in distances if d > 0]
        return min(valid_distances) if valid_distances else 0

    def calculate_mouse_position(
        self,
        letter_list: List[str],
        color_list: List[str],
        is_repeat: bool = False,
        screen_rect: Optional[Tuple[float, float, float, float]] = None,
        clock_active: bool = True
    ) -> Tuple[float, float]:
        """
        Calculate the averaged (x, y) position for the mouse based on letters and colors.

        Args:
            letter_list: List of letter inputs (a-l)
            color_list: List of color inputs
            is_repeat: If True, skip the incremental merging logic
            screen_rect: Optional tuple of (left, top, right, bottom) for edge calculations
            clock_active: Whether the clock visualization is currently active

        Returns:
            Tuple of (x, y) coordinates for the new mouse position
        """
        self.last_command = (letter_list, color_list)
        prev_letters = self.last_letters
        prev_colors = self.last_colors

        # Only do incremental merging if this is NOT a repeat command
        if not is_repeat:
            if len(letter_list) > 0 and len(color_list) == 0:
                if prev_letters:
                    letter_list = prev_letters + letter_list
                if prev_colors:
                    color_list = prev_colors
            elif len(color_list) > 0 and len(letter_list) == 0:
                if prev_colors:
                    color_list = prev_colors + color_list
                if prev_letters:
                    letter_list = prev_letters
            else:
                self.last_letters = []
                self.last_colors = []

        self.last_letters = letter_list
        self.last_colors = color_list

        log_separator()
        log_info(f"[calculate_mouse_position] Letters: {letter_list}, Colors: {color_list}")
        log_info(f"  Center: ({self.center_x}, {self.center_y}), Active: {clock_active}")

        # Convert letters to angles
        letter_positions = [geometry.letter_to_position(letter) for letter in letter_list]
        angles = [geometry.letter_to_clock_angle(pos) for pos in letter_positions]
        avg_hour, avg_deg = geometry.average_clock_angles(letter_positions)

        log_info(f"  Average angle: {avg_deg}°")

        # Process colors into distances
        color_index_list = self._process_colors(color_list, avg_deg, screen_rect, clock_active)

        average_radius = geometry.calculate_mean(color_index_list)
        log_info(f"  Average radius: {average_radius}")

        new_x, new_y = geometry.move_in_direction(avg_deg, average_radius, origin=(self.center_x, self.center_y))
        log_info(f"  Final position: ({new_x}, {new_y})")
        log_separator()

        return new_x, new_y

    def _process_colors(
        self,
        color_list: List[str],
        avg_deg: float,
        screen_rect: Optional[Tuple[float, float, float, float]],
        clock_active: bool
    ) -> List[float]:
        """Process color list into distance values."""
        num_rings = len(config.COLOR_LIST)
        color_index_list = []

        for color in color_list:
            if color == 'center':
                color_index_list.append(0)
            elif color == 'half':
                half_dist = self._calculate_half_distance(color_index_list, avg_deg, screen_rect, clock_active)
                color_index_list.append(half_dist)
            else:
                # Regular color from COLOR_POS
                radius_value = self.radius * config.COLOR_POS[color] / (num_rings - 1)
                color_index_list.append(radius_value)

        return color_index_list

    def _calculate_half_distance(
        self,
        color_index_list: List[float],
        avg_deg: float,
        screen_rect: Optional[Tuple[float, float, float, float]],
        clock_active: bool
    ) -> float:
        """Calculate 'half' distance - halfway between last color and screen edge."""
        if screen_rect is None:
            return self.radius / 2

        if not clock_active:
            edge_distance = self.calculate_edge_distance(avg_deg, screen_rect)
            return edge_distance / 2

        # Clock is on - use last color circle as reference
        if color_index_list:
            last_color_radius = color_index_list[-1]
        else:
            last_color_radius = self.radius

        edge_distance = self.calculate_edge_distance(avg_deg, screen_rect)
        return (last_color_radius + edge_distance) / 2

    def add_to_history(self, x: float, y: float):
        """Add a position to the movement history."""
        self.history.append((x, y))

    def pop_from_history(self) -> Optional[Tuple[float, float]]:
        """Remove and return the last position from history."""
        if self.history:
            return self.history.pop()
        return None

    def widen_radius(self):
        """Increase the target radius of the clock (animates smoothly)."""
        self._animator.update_timing()
        increment = self._animator.get_dynamic_increment()
        self.target_radius = self._animator.clamp_radius(self.target_radius + increment)

    def narrow_radius(self):
        """Decrease the target radius of the clock (animates smoothly)."""
        self._animator.update_timing()
        increment = self._animator.get_dynamic_increment()
        self.target_radius = self._animator.clamp_radius(self.target_radius - increment)

    def set_radius(self, value: int):
        """Set the radius to a specific value (with minimum limit)."""
        self.radius = max(config.MIN_RADIUS, value)
        self.target_radius = self.radius

    def update_radius_animation(self) -> bool:
        """
        Interpolate radius toward target with exponential acceleration.

        Returns:
            True if still animating, False if animation complete.
        """
        if abs(self.radius - self.target_radius) < 0.5:
            self.radius = self.target_radius
            return False

        lerp_factor = self._animator.get_lerp_factor()
        self.radius += (self.target_radius - self.radius) * lerp_factor
        return True

    def clear_state(self):
        """Clear the command state."""
        self.last_command = ([], [])
        self.last_letters = []
        self.last_colors = []
