"""
Concentric Box Targeting Overlay.

Renders axis-aligned rectangular boxes centered at cursor,
each with distinct color for targeting via voice commands.
"""

from typing import List, Tuple
from ..core.config import get_setting
from ..rendering.colors import COLOR_ORDER, get_color
from ..rendering.drawing import draw_rect


def get_box_count() -> int:
    """Get number of concentric boxes."""
    return get_setting("box_overlay_count", 5)


def get_box_spacing() -> float:
    """Get spacing between boxes in pixels."""
    return get_setting("box_overlay_spacing", 50)


def get_progression_mode() -> str:
    """Get size progression mode: 'linear' or 'geometric'."""
    return get_setting("box_overlay_progression", "linear")


def calculate_box_sizes(
    num_boxes: int = None,
    base_size: float = None,
    spacing: float = None,
    mode: str = None
) -> List[Tuple[float, float]]:
    """
    Calculate sizes for each concentric box.

    Args:
        num_boxes: Number of boxes
        base_size: Size of innermost box
        spacing: Spacing between boxes
        mode: 'linear' or 'geometric'

    Returns:
        List of (width, height) tuples, innermost first
    """
    if num_boxes is None:
        num_boxes = get_box_count()
    if base_size is None:
        base_size = get_setting("box_overlay_base_size", 20)
    if spacing is None:
        spacing = get_box_spacing()
    if mode is None:
        mode = get_progression_mode()

    sizes = []

    for i in range(num_boxes):
        if mode == "geometric":
            # Geometric: each box is 1.5x larger
            factor = 1.5 ** i
            size = base_size * factor
        else:
            # Linear: each box adds fixed spacing
            size = base_size + spacing * i

        sizes.append((size, size))  # Square boxes

    return sizes


def get_box_colors(num_boxes: int = None) -> List[str]:
    """
    Get colors for each box.

    Args:
        num_boxes: Number of boxes

    Returns:
        List of color hex values
    """
    if num_boxes is None:
        num_boxes = get_box_count()

    colors = []
    # Use COLOR_ORDER, skipping "center" for outer boxes
    color_names = ["center", "red", "blue", "green", "yellow", "purple", "pink"]

    for i in range(num_boxes):
        color_name = color_names[i % len(color_names)]
        try:
            color_hex = get_color(color_name)
        except KeyError:
            color_hex = "ff0000ff"  # Fallback to red
        colors.append(color_hex)

    return colors


def draw_concentric_boxes(
    canvas,
    center: Tuple[float, float],
    num_boxes: int = None,
    thickness: float = 2
):
    """
    Draw concentric box overlay.

    Args:
        canvas: Talon canvas object
        center: Center point (x, y)
        num_boxes: Number of boxes
        thickness: Line thickness
    """
    if num_boxes is None:
        num_boxes = get_box_count()

    sizes = calculate_box_sizes(num_boxes)
    colors = get_box_colors(num_boxes)
    cx, cy = center

    # Draw from innermost to outermost
    for i, ((w, h), color) in enumerate(zip(sizes, colors)):
        rect = (cx - w / 2, cy - h / 2, w, h)
        draw_rect(canvas, rect, color, thickness)


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
