"""
Core mouse clock logic without Talon dependencies.

This module contains the business logic for calculating mouse positions based on
clock face letters and color rings, managing history, and handling radius adjustments.
"""

import math
from typing import List, Tuple, Optional

from . import geometry
from . import config
from .logger import log_debug, log_info, log_separator


def flip_letter_to_opposite(letter: str) -> str:
    """
    Flip a clock letter to its opposite position (180 degrees).

    Clock positions:
    A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9, J=10, K=11, L=12

    Opposites (add 6 positions, wrap around):
    A↔G, B↔H, C↔I, D↔J, E↔K, F↔L

    Args:
        letter: A clock letter (a-l, case insensitive)

    Returns:
        The opposite clock letter
    """
    letter_index = config.CLOCK_LETTERS.index(letter.lower())
    opposite_index = (letter_index + 6) % 12
    return config.CLOCK_LETTERS[opposite_index]


def parse_voice_inputs(words: List[str]) -> dict:
    """
    Parse voice input words into letters, colors, and apply ordinal multipliers.

    Ordinals following a letter or color will multiply that item.

    Args:
        words: List of voice command words

    Returns:
        Dictionary with keys 'letters', 'colors', 'unknowns'

    Example:
        ["red", "3", "a", "pink"] ->
        {"letters": ["a"], "colors": ["red", "red", "red", "pink"], "unknowns": []}
    """
    letters_list = []
    colors_list = []
    unknowns_list = []

    i = 0
    while i < len(words):
        val = str(words[i]).lower()

        # Check if this is a numeric string (ordinals come through as "1", "2", "3" etc)
        is_ordinal = False
        multiplier = 0
        try:
            multiplier = int(val)
            if 1 <= multiplier <= 99:  # Valid ordinal range
                is_ordinal = True
        except ValueError:
            is_ordinal = False

        if is_ordinal:
            # This is an ordinal - it should apply to the previous item
            # Repeat the last added letter or color that many times
            if letters_list:
                # Repeat the last letter (multiplier - 1) more times
                last_letter = letters_list[-1]
                for _ in range(multiplier - 1):
                    letters_list.append(last_letter)
            elif colors_list:
                # Repeat the last color (multiplier - 1) more times
                last_color = colors_list[-1]
                for _ in range(multiplier - 1):
                    colors_list.append(last_color)

        elif val in config.CLOCK_LETTERS:
            letters_list.append(val)
        elif val == "mouse":
            # "mouse" means center point
            colors_list.append("center")
        elif val == "half":
            # "half" means halfway to screen edge from last color
            colors_list.append("half")
        elif val in config.COLOR_MAP:
            colors_list.append(val)
        else:
            unknowns_list.append(val)

        i += 1

    return {
        "letters": letters_list,
        "colors": colors_list,
        "unknowns": unknowns_list
    }


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
            dist_right = (screen_right - self.center_x) / dx
            distances.append(dist_right)

        if dx < 0:
            dist_left = (screen_left - self.center_x) / dx
            distances.append(dist_left)

        if dy > 0:
            dist_bottom = (screen_bottom - self.center_y) / dy
            distances.append(dist_bottom)

        if dy < 0:
            dist_top = (screen_top - self.center_y) / dy
            distances.append(dist_top)

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
        log_info(f"[calculate_mouse_position] Starting calculation")
        log_info(f"  Letters: {letter_list}, Colors: {color_list}")
        log_info(f"  Clock active: {clock_active}, Is repeat: {is_repeat}")
        log_info(f"  Center: ({self.center_x}, {self.center_y})")
        if screen_rect:
            log_info(f"  Screen bounds: left={screen_rect[0]}, top={screen_rect[1]}, right={screen_rect[2]}, bottom={screen_rect[3]}")

        # Convert letters to angles
        letter_positions = [geometry.letter_to_position(letter) for letter in letter_list]
        angles = [geometry.letter_to_clock_angle(pos) for pos in letter_positions]
        avg_angle = geometry.average_angles(angles)
        avg_hour, avg_deg = geometry.average_clock_angles(letter_positions)

        log_info(f"  Letter positions: {letter_positions}")
        log_info(f"  Angles: {angles}")
        log_info(f"  Average angle: {avg_deg}°")

        # Use the full number of color rings, including center
        num_rings = len(config.COLOR_LIST)

        # Process colors - handle "half" specially
        color_index_list = []
        for color in color_list:
            if color == 'center':
                log_info(f"  Processing color 'center': distance=0")
                color_index_list.append(0)
            elif color == 'half':
                log_info(f"  Processing color 'half':")
                # Calculate halfway between last color and screen edge
                if screen_rect is None:
                    # No screen bounds provided, use a default distance
                    half_distance = self.radius / 2
                    log_info(f"    No screen bounds - using radius/2: {half_distance}")
                    color_index_list.append(half_distance)
                elif not clock_active:
                    # Clock is off - current mouse position is the reference
                    edge_distance = self.calculate_edge_distance(avg_deg, screen_rect)
                    half_distance = edge_distance / 2
                    log_info(f"    Clock OFF - edge_distance: {edge_distance}, half_distance: {half_distance}")
                    color_index_list.append(half_distance)
                else:
                    # Clock is on - use last color circle as reference
                    if color_index_list:
                        last_color_radius = color_index_list[-1]
                    else:
                        # Default to outermost ring if no previous color
                        last_color_radius = self.radius

                    edge_distance = self.calculate_edge_distance(avg_deg, screen_rect)
                    half_distance = (last_color_radius + edge_distance) / 2
                    log_info(f"    Clock ON - last_color_radius: {last_color_radius}, edge_distance: {edge_distance}, half_distance: {half_distance}")
                    color_index_list.append(half_distance)
            else:
                # Regular color from COLOR_POS
                radius_value = self.radius * config.COLOR_POS[color] / (num_rings - 1)
                log_info(f"  Processing color '{color}': distance={radius_value}")
                color_index_list.append(radius_value)

        average_radius = geometry.calculate_mean(color_index_list)
        log_info(f"  Average radius: {average_radius}")

        new_x, new_y = geometry.move_in_direction(avg_deg, average_radius, origin=(self.center_x, self.center_y))
        log_info(f"  Final position: ({new_x}, {new_y})")
        log_separator()

        return new_x, new_y

    def add_to_history(self, x: float, y: float):
        """Add a position to the movement history."""
        self.history.append((x, y))

    def pop_from_history(self) -> Optional[Tuple[float, float]]:
        """Remove and return the last position from history."""
        if self.history:
            return self.history.pop()
        return None

    def widen_radius(self):
        """Increase the radius of the clock."""
        self.radius += config.RADIUS_INCREMENT

    def narrow_radius(self):
        """Decrease the radius of the clock (with minimum limit)."""
        self.radius = max(config.MIN_RADIUS, self.radius - config.RADIUS_INCREMENT)

    def set_radius(self, value: int):
        """Set the radius to a specific value (with minimum limit)."""
        self.radius = max(config.MIN_RADIUS, value)

    def clear_state(self):
        """Clear the command state."""
        self.last_command = ([], [])
        self.last_letters = []
        self.last_colors = []
