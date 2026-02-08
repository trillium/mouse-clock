"""
Basic shape drawing primitives for overlay systems.

Provides a consistent API for drawing lines, circles, rectangles, dots,
crosses, and text on Talon canvas objects.
"""

from typing import Tuple
from talon.skia import Paint


def draw_line(
    canvas,
    start: Tuple[float, float],
    end: Tuple[float, float],
    color: str,
    thickness: float = 2,
):
    """
    Draw a solid line segment.

    Args:
        canvas: Talon canvas object
        start: Start point (x, y)
        end: End point (x, y)
        color: 8-digit RGBA hex color
        thickness: Line width in pixels
    """
    paint = canvas.paint
    paint.color = color
    paint.style = Paint.Style.STROKE
    paint.stroke_width = thickness
    canvas.draw_line(start[0], start[1], end[0], end[1])


def draw_circle(
    canvas,
    center: Tuple[float, float],
    radius: float,
    color: str,
    thickness: float = 2,
    filled: bool = False
):
    """
    Draw a circle outline or filled.

    Args:
        canvas: Talon canvas object
        center: Center point (x, y)
        radius: Circle radius
        color: 8-digit RGBA hex color
        thickness: Line width for outline
        filled: Whether to fill the circle
    """
    paint = canvas.paint
    paint.color = color
    paint.style = Paint.Style.FILL if filled else Paint.Style.STROKE
    paint.stroke_width = thickness

    canvas.draw_circle(center[0], center[1], radius)


def draw_rect(
    canvas,
    rect: Tuple[float, float, float, float],
    color: str,
    thickness: float = 2,
    filled: bool = False
):
    """
    Draw a rectangle outline or filled.

    Args:
        canvas: Talon canvas object
        rect: Rectangle as (x, y, width, height)
        color: 8-digit RGBA hex color
        thickness: Line width for outline
        filled: Whether to fill the rectangle
    """
    x, y, w, h = rect

    paint = canvas.paint
    paint.color = color

    if filled:
        # For filled rect, draw using fill style
        from talon.skia import Rect
        paint.style = Paint.Style.FILL
        paint.stroke_width = 0
        # Rect takes (left, top, width, height), NOT (left, top, right, bottom)
        canvas.draw_rect(Rect(x, y, w, h))
    else:
        # Draw outline using 4 lines
        top_left = (x, y)
        top_right = (x + w, y)
        bottom_right = (x + w, y + h)
        bottom_left = (x, y + h)

        draw_line(canvas, top_left, top_right, color, thickness)
        draw_line(canvas, top_right, bottom_right, color, thickness)
        draw_line(canvas, bottom_right, bottom_left, color, thickness)
        draw_line(canvas, bottom_left, top_left, color, thickness)


def draw_dot(
    canvas,
    center: Tuple[float, float],
    radius: float,
    color: str
):
    """
    Draw a small filled circle marker.

    Args:
        canvas: Talon canvas object
        center: Center point (x, y)
        radius: Dot radius
        color: 8-digit RGBA hex color
    """
    draw_circle(canvas, center, radius, color, filled=True)


def draw_cross(
    canvas,
    center: Tuple[float, float],
    size: float,
    color: str,
    thickness: float = 2,
    style: str = "plus"
):
    """
    Draw a cross marker (+ or x).

    Args:
        canvas: Talon canvas object
        center: Center point (x, y)
        size: Half-length of cross arms
        color: 8-digit RGBA hex color
        thickness: Line width
        style: "plus" for + shape, "x" for x shape
    """
    cx, cy = center

    if style == "x":
        # Diagonal cross
        draw_line(canvas, (cx - size, cy - size), (cx + size, cy + size), color, thickness)
        draw_line(canvas, (cx - size, cy + size), (cx + size, cy - size), color, thickness)
    else:
        # Plus cross (default)
        draw_line(canvas, (cx - size, cy), (cx + size, cy), color, thickness)
        draw_line(canvas, (cx, cy - size), (cx, cy + size), color, thickness)


def draw_text(
    canvas,
    position: Tuple[float, float],
    text: str,
    color: str,
    font_size: float = 16,
    anchor: str = "center"
):
    """
    Render text with configurable anchor point.

    Args:
        canvas: Talon canvas object
        position: Position (x, y) for anchor
        text: Text to render
        color: 8-digit RGBA hex color
        font_size: Font size in pixels
        anchor: Anchor position - "center", "left", "right", "top", "bottom",
                or combinations like "top-left", "bottom-right"
    """
    paint = canvas.paint
    paint.color = color
    paint.textsize = font_size

    x, y = position

    # Get text bounds for alignment
    # Estimate text width (approximate)
    text_width = len(text) * font_size * 0.6
    text_height = font_size

    # Adjust position based on anchor
    if "left" in anchor:
        pass  # x stays as-is
    elif "right" in anchor:
        x -= text_width
    else:  # center horizontally by default
        x -= text_width / 2

    if "top" in anchor:
        y += text_height
    elif "bottom" in anchor:
        pass  # y stays as-is
    else:  # center vertically by default
        y += text_height / 2

    canvas.draw_text(text, x, y)
