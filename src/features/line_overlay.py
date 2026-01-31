"""
Lettered Line Intersection Overlay.

Divides the screen into horizontal bands labeled with letters,
allowing voice-driven cursor positioning via line intersections.
"""

from typing import Tuple, List, Optional
from dataclasses import dataclass

from ..core.config import get_setting
from ..rendering.colors import get_color, COLOR_ORDER
from ..rendering.drawing import draw_line, draw_text, draw_dot, draw_cross


@dataclass
class LineOverlayConfig:
    """Configuration for line overlay."""
    num_bands: int = 5  # A through E
    line_color: str = "ff0000ff"  # Red
    line_thickness: float = 2
    label_color: str = "00ff00ff"  # Green
    label_size: float = 16
    margin: float = 20  # Pixels from edge for labels


# Letters for bands (configurable)
BAND_LETTERS = "ABCDEFGHIJ"


def get_band_count() -> int:
    """Get number of horizontal bands."""
    return get_setting("line_overlay_bands", 5)


def get_band_y_positions(screen_height: float, num_bands: int = None) -> List[Tuple[str, float]]:
    """
    Calculate Y positions for each lettered band.

    Args:
        screen_height: Height of screen in pixels
        num_bands: Number of bands (default from settings)

    Returns:
        List of (letter, y_position) tuples
    """
    if num_bands is None:
        num_bands = get_band_count()

    positions = []
    # Divide screen into equal bands
    band_height = screen_height / (num_bands + 1)

    for i in range(num_bands):
        letter = BAND_LETTERS[i]
        # Position at center of each band
        y = band_height * (i + 1)
        positions.append((letter, y))

    return positions


def get_y_for_letter(letter: str, screen_height: float) -> Optional[float]:
    """
    Get Y position for a specific letter.

    Args:
        letter: Band letter (A-E, etc.)
        screen_height: Height of screen

    Returns:
        Y coordinate or None if invalid letter
    """
    letter = letter.upper()
    positions = get_band_y_positions(screen_height)

    for band_letter, y in positions:
        if band_letter == letter:
            return y

    return None


def draw_horizontal_line(
    canvas,
    y: float,
    screen_width: float,
    color: str = None,
    thickness: float = None
):
    """
    Draw a horizontal line across the screen.

    Args:
        canvas: Talon canvas object
        y: Y coordinate for the line
        screen_width: Width of screen
        color: Line color (default from config)
        thickness: Line thickness (default from config)
    """
    if color is None:
        color = get_setting("line_overlay_color", "ff0000ff")
    if thickness is None:
        thickness = get_setting("line_overlay_thickness", 2)

    draw_line(canvas, (0, y), (screen_width, y), color, thickness)


def draw_band_labels(
    canvas,
    screen_height: float,
    margin: float = 20,
    color: str = None,
    font_size: float = 16
):
    """
    Draw letter labels for each band.

    Args:
        canvas: Talon canvas object
        screen_height: Height of screen
        margin: Pixels from left edge
        color: Label color
        font_size: Font size for labels
    """
    if color is None:
        color = get_setting("line_overlay_label_color", "00ff00ff")

    positions = get_band_y_positions(screen_height)

    for letter, y in positions:
        draw_text(canvas, (margin, y), letter, color, font_size, anchor="left")


def draw_all_lines(
    canvas,
    screen_width: float,
    screen_height: float,
    color: str = None,
    thickness: float = None,
    show_labels: bool = True
):
    """
    Draw all horizontal band lines.

    Args:
        canvas: Talon canvas object
        screen_width: Width of screen
        screen_height: Height of screen
        color: Line color
        thickness: Line thickness
        show_labels: Whether to draw letter labels
    """
    positions = get_band_y_positions(screen_height)

    for letter, y in positions:
        draw_horizontal_line(canvas, y, screen_width, color, thickness)

    if show_labels:
        draw_band_labels(canvas, screen_height)


def draw_single_line(
    canvas,
    letter: str,
    screen_width: float,
    screen_height: float,
    color: str = None,
    thickness: float = None
):
    """
    Draw a single horizontal line for a specific letter.

    Args:
        canvas: Talon canvas object
        letter: Band letter
        screen_width: Width of screen
        screen_height: Height of screen
        color: Line color
        thickness: Line thickness
    """
    y = get_y_for_letter(letter, screen_height)
    if y is not None:
        draw_horizontal_line(canvas, y, screen_width, color, thickness)


# =============================================================================
# Vertical Intersection Lines
# =============================================================================

# Colors for vertical lines (from COLOR_ORDER, skipping center)
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
