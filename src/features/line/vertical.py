"""
Vertical line overlay components.

Draws color-coded vertical lines for intersection targeting.
"""

from typing import List, Tuple, Optional

from ...core.config import get_setting
from ...rendering.drawing import draw_line


# Colors for vertical lines
VERTICAL_COLORS = [
    "ff0000ff",  # red
    "0000ffff",  # blue
    "00ff00ff",  # green
    "ffd700ff",  # yellow
    "800080ff",  # purple
    "ff00ffff",  # pink
]


def get_vertical_count() -> int:
    """Get number of vertical lines."""
    return get_setting("line_overlay_verticals", 6)


def get_vertical_x_positions(screen_width: float, num_verticals: int = None) -> List[Tuple[str, float, str]]:
    """
    Calculate X positions for color-coded vertical lines.

    Args:
        screen_width: Width of screen in pixels
        num_verticals: Number of vertical lines

    Returns:
        List of (color_name, x_position, color_hex) tuples
    """
    if num_verticals is None:
        num_verticals = get_vertical_count()

    positions = []
    segment_width = screen_width / (num_verticals + 1)

    color_names = ["red", "blue", "green", "yellow", "purple", "pink"]

    for i in range(num_verticals):
        color_name = color_names[i % len(color_names)]
        color_hex = VERTICAL_COLORS[i % len(VERTICAL_COLORS)]
        x = segment_width * (i + 1)
        positions.append((color_name, x, color_hex))

    return positions


def get_x_for_color(color_name: str, screen_width: float) -> Optional[float]:
    """
    Get X position for a specific color vertical.

    Args:
        color_name: Color name (red, blue, etc.)
        screen_width: Width of screen

    Returns:
        X coordinate or None if invalid color
    """
    positions = get_vertical_x_positions(screen_width)

    for name, x, _ in positions:
        if name == color_name.lower():
            return x

    return None


def draw_vertical_line(
    canvas,
    x: float,
    screen_height: float,
    color: str,
    thickness: float = None
):
    """
    Draw a vertical line from top to bottom.

    Args:
        canvas: Talon canvas object
        x: X coordinate for the line
        screen_height: Height of screen
        color: Line color hex
        thickness: Line thickness
    """
    if thickness is None:
        thickness = get_setting("line_overlay_thickness", 2)

    draw_line(canvas, (x, 0), (x, screen_height), color, thickness)


def draw_all_verticals(
    canvas,
    screen_width: float,
    screen_height: float,
    thickness: float = None
):
    """
    Draw all color-coded vertical lines.

    Args:
        canvas: Talon canvas object
        screen_width: Width of screen
        screen_height: Height of screen
        thickness: Line thickness
    """
    positions = get_vertical_x_positions(screen_width)

    for _, x, color_hex in positions:
        draw_vertical_line(canvas, x, screen_height, color_hex, thickness)
