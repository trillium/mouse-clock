"""
Concentric Box Targeting Overlay.

Renders axis-aligned rectangular boxes centered at cursor,
each with distinct color for targeting via voice commands.
"""

from typing import List, Tuple
from ..core.config import get_setting
from ..rendering.colors import COLOR_ORDER, get_color
from ..rendering.drawing import draw_rect, draw_clock_rays, draw_dot, draw_text
from ..core.geometry import ray_rect_intersection, number_to_angle


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


# =============================================================================
# Directional Guides
# =============================================================================

def get_ray_length() -> float:
    """Get length for directional rays."""
    sizes = calculate_box_sizes()
    if sizes:
        # Extend past outermost box
        max_size = max(sizes[-1])
        return max_size * 0.75
    return 200


def draw_directional_rays(
    canvas,
    center: Tuple[float, float],
    length: float = None,
    color: str = None,
    thickness: float = 1
):
    """
    Draw 12 clock-hour directional rays.

    Args:
        canvas: Talon canvas object
        center: Center point (x, y)
        length: Ray length
        color: Ray color
        thickness: Line thickness
    """
    if length is None:
        length = get_ray_length()
    if color is None:
        color = get_setting("box_ray_color", "ffffff7f")  # Semi-transparent white

    draw_clock_rays(canvas, center, length, color, thickness, dashed=True)


def draw_intersection_markers(
    canvas,
    center: Tuple[float, float],
    num_boxes: int = None,
    marker_size: float = 3
):
    """
    Draw markers at ray-box intersections.

    Args:
        canvas: Talon canvas object
        center: Center point (x, y)
        num_boxes: Number of boxes
        marker_size: Size of intersection dots
    """
    if num_boxes is None:
        num_boxes = get_box_count()

    sizes = calculate_box_sizes(num_boxes)
    colors = get_box_colors(num_boxes)
    cx, cy = center

    # For each clock hour
    for hour in range(1, 13):
        angle = number_to_angle(hour)

        # For each box, find intersection
        for (w, h), color in zip(sizes, colors):
            rect = (cx - w / 2, cy - h / 2, w, h)
            intersection = ray_rect_intersection((cx, cy), angle, rect)

            if intersection:
                draw_dot(canvas, intersection, marker_size, color)


def draw_boxes_with_guides(
    canvas,
    center: Tuple[float, float],
    num_boxes: int = None,
    show_rays: bool = True,
    show_markers: bool = True
):
    """
    Draw concentric boxes with directional guides.

    Args:
        canvas: Talon canvas object
        center: Center point (x, y)
        num_boxes: Number of boxes
        show_rays: Whether to show directional rays
        show_markers: Whether to show intersection markers
    """
    if num_boxes is None:
        num_boxes = get_box_count()

    # Draw boxes
    draw_concentric_boxes(canvas, center, num_boxes)

    # Draw directional rays
    if show_rays:
        draw_directional_rays(canvas, center)

    # Draw intersection markers
    if show_markers:
        draw_intersection_markers(canvas, center, num_boxes)


# =============================================================================
# Target Computation
# =============================================================================

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
    from ..core.geometry import letter_to_angle

    # Convert letter to clock position
    letter_upper = letter.upper()
    if letter_upper < 'A' or letter_upper > 'L':
        return center

    # A=1, B=2, ..., L=12
    position = ord(letter_upper) - ord('A') + 1
    if position > 12:
        position = 12

    return get_target_position(center, color_name, position)
