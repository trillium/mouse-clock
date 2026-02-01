"""
Composite line overlay functions.

Higher-level functions that combine horizontal and vertical lines.
"""

from ...rendering.drawing import draw_cross
from .horizontal import get_y_for_letter, draw_horizontal_line
from .vertical import get_vertical_x_positions, draw_all_verticals


def draw_intersection_markers(
    canvas,
    horizontal_y: float,
    screen_width: float,
    marker_size: float = 5
):
    """
    Draw markers at intersection points between horizontal and verticals.

    Args:
        canvas: Talon canvas object
        horizontal_y: Y coordinate of horizontal line
        screen_width: Width of screen
        marker_size: Size of intersection markers
    """
    positions = get_vertical_x_positions(screen_width)

    for _, x, color_hex in positions:
        draw_cross(canvas, (x, horizontal_y), marker_size, color_hex, 2, style="plus")


def draw_line_with_verticals(
    canvas,
    letter: str,
    screen_width: float,
    screen_height: float,
    show_markers: bool = True
):
    """
    Draw horizontal line with vertical intersection guides.

    Args:
        canvas: Talon canvas object
        letter: Horizontal band letter
        screen_width: Width of screen
        screen_height: Height of screen
        show_markers: Whether to show intersection markers
    """
    y = get_y_for_letter(letter, screen_height)
    if y is None:
        return

    # Draw horizontal line
    draw_horizontal_line(canvas, y, screen_width)

    # Draw vertical lines
    draw_all_verticals(canvas, screen_width, screen_height)

    # Draw intersection markers
    if show_markers:
        draw_intersection_markers(canvas, y, screen_width)
