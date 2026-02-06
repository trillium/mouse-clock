_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Concentric box rendering functions.

Drawing functions for boxes, rays, and intersection markers.
"""

from typing import Tuple

from ...core.config import get_setting
from ...core.geometry import number_to_angle
from ...rendering.drawing import draw_rect, draw_clock_rays, draw_dot
from .config import get_box_count, calculate_box_sizes, get_box_colors


def draw_concentric_boxes(
    canvas,
    center: Tuple[float, float],
    num_boxes: int = None,
    thickness: float = 2,
    radius: float = None
):
    """
    Draw concentric box overlay.

    Args:
        canvas: Talon canvas object
        center: Center point (x, y)
        num_boxes: Number of boxes
        thickness: Line thickness
        radius: Optional outer radius to scale boxes to
    """
    if num_boxes is None:
        num_boxes = get_box_count()

    sizes = calculate_box_sizes(num_boxes)
    colors = get_box_colors(num_boxes)
    cx, cy = center

    # Scale sizes if radius provided
    if radius is not None and sizes:
        max_size = max(sizes[-1])  # Outermost box size
        if max_size > 0:
            scale = radius / max_size
            sizes = [(w * scale, h * scale) for w, h in sizes]

    # Draw from innermost to outermost
    for i, ((w, h), color) in enumerate(zip(sizes, colors)):
        rect = (cx - w / 2, cy - h / 2, w, h)
        draw_rect(canvas, rect, color, thickness)


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
    from ...core.geometry import ray_rect_intersection

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
