"""
Horizontal line overlay components.

Draws horizontal bands with letter labels for voice-driven positioning.
"""

from typing import Tuple, List, Optional
from dataclasses import dataclass

from ...core.config import get_setting
from ...rendering.drawing import draw_line, draw_text


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
