"""
Canvas drawing and rendering utilities for the mouse clock.

This module handles all visual rendering of the mouse clock, including
concentric rings, dots, clock letters, and edge-distance visualization.
"""

import math
from talon.skia import Paint
from talon import ui

from ..core import config


def get_screen_dimensions(center_x: float, center_y: float) -> tuple[int, int]:
    """
    Get the screen dimensions for the screen containing the given point.

    Args:
        center_x: X coordinate of the point
        center_y: Y coordinate of the point

    Returns:
        Tuple of (width, height) for the screen containing the point
    """
    from talon.types.point import Point2d

    screens = ui.screens()
    point = Point2d(center_x, center_y)

    for screen in screens:
        if screen.rect.contains(point):
            return screen.rect.width, screen.rect.height

    # Fallback to first screen if point not found
    if screens:
        return screens[0].rect.width, screens[0].rect.height

    # Ultimate fallback
    return config.DEFAULT_SCREEN_WIDTH, config.DEFAULT_SCREEN_HEIGHT


def setup_paint(canvas, color: str, stroke_width: int = None):
    """
    Configure canvas paint settings.

    Args:
        canvas: Talon canvas object
        color: Color hex string to set
        stroke_width: Width of stroke lines (defaults to DEFAULT_STROKE_WIDTH)

    Returns:
        Configured paint object
    """
    if stroke_width is None:
        stroke_width = config.DEFAULT_STROKE_WIDTH

    paint = canvas.paint
    paint.color = color
    paint.style = Paint.Style.STROKE
    paint.stroke_width = stroke_width
    return paint


def calculate_ring_radius(ring_index: int, total_rings: int, outer_radius: float) -> float:
    """
    Calculate the radius for a specific ring in the concentric circle pattern.

    Args:
        ring_index: Index of the ring (0 = center)
        total_rings: Total number of rings
        outer_radius: Radius of the outermost ring

    Returns:
        Radius for the specified ring
    """
    if ring_index == 0:
        return 0
    return outer_radius * ring_index / (total_rings - 1)


def calculate_clock_position(letter_index: int, radius: float, center_x: float, center_y: float) -> tuple[float, float]:
    """
    Calculate the (x, y) position for a clock letter.

    Args:
        letter_index: Index of the letter (1-12, where 1 = A at 12 o'clock)
        radius: Radius at which to place the letter
        center_x: X coordinate of clock center
        center_y: Y coordinate of clock center

    Returns:
        Tuple of (x, y) coordinates
    """
    # 30 degrees per hour, starting at -90 (12 o'clock position)
    angle = math.radians(30 * letter_index - 90)
    x = center_x + radius * math.cos(angle)
    y = center_y + radius * math.sin(angle)
    return x, y


def draw_concentric_rings(canvas, center_x: float, center_y: float, radius: float, color_list: list[str]):
    """
    Draw the concentric colored rings of the mouse clock.

    Args:
        canvas: Talon canvas object
        center_x: X coordinate of clock center
        center_y: Y coordinate of clock center
        radius: Outer radius of the clock
        color_list: List of color hex strings for the rings
    """
    paint = canvas.paint
    num_rings = len(color_list)

    for i in range(num_rings):
        paint.color = color_list[i]
        ring_radius = calculate_ring_radius(i, num_rings, radius)
        canvas.draw_circle(center_x, center_y, ring_radius)


def draw_clock_position_dots(
    canvas,
    center_x: float,
    center_y: float,
    radius: float,
    color_list: list[str],
    dot_radius: float = None
):
    """
    Draw colored dots at each of the 12 clock positions on different rings.

    Args:
        canvas: Talon canvas object
        center_x: X coordinate of clock center
        center_y: Y coordinate of clock center
        radius: Outer radius of the clock
        color_list: List of color hex strings for each ring of dots
        dot_radius: Size of each dot (defaults to DEFAULT_DOT_RADIUS)
    """
    if dot_radius is None:
        dot_radius = config.DEFAULT_DOT_RADIUS

    paint = canvas.paint
    paint.style = Paint.Style.FILL  # Use FILL instead of STROKE for solid dots

    num_rings = len(color_list)

    # For each color ring
    for ring_index in range(num_rings):
        paint.color = color_list[ring_index]
        ring_radius = calculate_ring_radius(ring_index, num_rings, radius)

        # Draw a dot at each of the 12 clock positions on this ring
        for position in range(1, 13):  # 1-12 for clock positions
            x, y = calculate_clock_position(position, ring_radius, center_x, center_y)
            canvas.draw_circle(x, y, dot_radius)


def calculate_edge_distance(
    ring_index: int,
    total_rings: int,
    screen_dimension: float,
    current_position: float
) -> float:
    """
    Calculate distance from edge for a specific ring.

    Args:
        ring_index: Index of the ring (0 = at current position)
        total_rings: Total number of rings
        screen_dimension: Total screen dimension (width or height)
        current_position: Current mouse position in that dimension

    Returns:
        Distance from current position towards the edge
    """
    if ring_index == 0:
        return 0

    # Distance available to the edge
    distance_to_edge = screen_dimension - current_position

    # Divide the distance into equal segments
    return (distance_to_edge / total_rings) * ring_index


def draw_edge_distance_dots(
    canvas,
    center_x: float,
    center_y: float,
    screen_width: float,
    screen_height: float,
    color_list: list[str],
    dot_radius: float = None
):
    """
    Draw colored dots at clock positions, with colors representing distance from screen edge.

    Args:
        canvas: Talon canvas object
        center_x: X coordinate of clock center (current mouse position)
        center_y: Y coordinate of clock center (current mouse position)
        screen_width: Width of the screen
        screen_height: Height of the screen
        color_list: List of color hex strings for each distance ring
        dot_radius: Size of each dot (defaults to DEFAULT_DOT_RADIUS)
    """
    if dot_radius is None:
        dot_radius = config.DEFAULT_DOT_RADIUS

    paint = canvas.paint
    paint.style = Paint.Style.FILL

    num_rings = len(color_list)

    # For each color ring
    for ring_index in range(num_rings):
        paint.color = color_list[ring_index]

        # Draw a dot at each of the 12 clock positions
        for position in range(1, 13):  # 1-12 for clock positions
            angle = math.radians(30 * position - 90)

            # Calculate which edge we're heading towards
            dx = math.cos(angle)
            dy = math.sin(angle)

            # Determine the limiting dimension based on direction
            if abs(dx) > abs(dy):
                # Primarily horizontal movement
                if dx > 0:  # Moving right
                    edge_distance = screen_width - center_x
                else:  # Moving left
                    edge_distance = center_x
            else:
                # Primarily vertical movement
                if dy > 0:  # Moving down
                    edge_distance = screen_height - center_y
                else:  # Moving up
                    edge_distance = center_y

            # Calculate distance for this ring
            distance = (edge_distance / num_rings) * ring_index

            # Calculate final position
            x = center_x + distance * dx
            y = center_y + distance * dy

            canvas.draw_circle(x, y, dot_radius)


def draw_clock_letters(canvas, center_x: float, center_y: float, radius: float, text_color: str):
    """
    Draw the clock position letters (A-L) around the outer ring.

    Args:
        canvas: Talon canvas object
        center_x: X coordinate of clock center
        center_y: Y coordinate of clock center
        radius: Radius at which to place letters
        text_color: Color hex string for the letter text
    """
    paint = canvas.paint
    paint.color = text_color

    for i, letter in enumerate(config.CLOCK_LETTERS.upper(), start=1):
        x, y = calculate_clock_position(i, radius, center_x, center_y)
        canvas.draw_text(letter, x, y)


def draw_mouse_clock(
    canvas,
    center_x: float,
    center_y: float,
    radius: float,
    color_list: list[str],
    active_color: str,
    text_color: str,
    style: str = "rings",
    dot_radius: float = None,
    screen_width: float = None,
    screen_height: float = None
):
    """
    Draw the mouse clock visualization with concentric circles and clock position letters.

    Args:
        canvas: Talon canvas object
        center_x: X coordinate of clock center
        center_y: Y coordinate of clock center
        radius: Outer radius of the clock
        color_list: List of color hex strings for the concentric rings
        active_color: Color hex string for active elements
        text_color: Color hex string for letter labels
        style: Drawing style - "rings", "dots", or "edge"
        dot_radius: Radius of dots when style="dots" or "edge" (defaults to DEFAULT_DOT_RADIUS)
        screen_width: Screen width (optional, auto-detected if not provided)
        screen_height: Screen height (optional, auto-detected if not provided)
    """
    if dot_radius is None:
        dot_radius = config.DEFAULT_DOT_RADIUS

    setup_paint(canvas, active_color)

    if style == "edge":
        # Auto-detect screen dimensions if not provided
        if screen_width is None or screen_height is None:
            screen_width, screen_height = get_screen_dimensions(center_x, center_y)
        draw_edge_distance_dots(canvas, center_x, center_y, screen_width, screen_height, color_list, dot_radius)
    elif style == "dots":
        draw_clock_position_dots(canvas, center_x, center_y, radius, color_list, dot_radius)
    else:  # Default to "rings"
        draw_concentric_rings(canvas, center_x, center_y, radius, color_list)

    draw_clock_letters(canvas, center_x, center_y, radius, text_color)
