_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Mouse control primitives for navigation systems.

Provides a thin wrapper over Talon's ctrl module for cursor manipulation
and screen-aware position management.
"""

from typing import Tuple, Optional
from talon import ctrl, ui
from talon.types.point import Point2d


def get_mouse_position() -> Tuple[float, float]:
    """
    Get current cursor position.

    Returns:
        Tuple of (x, y) coordinates
    """
    return ctrl.mouse_pos()


def set_mouse_position(x: float, y: float):
    """
    Move cursor to absolute position.

    Args:
        x: X coordinate
        y: Y coordinate
    """
    ctrl.mouse_move(x, y)


def move_mouse_relative(dx: float, dy: float):
    """
    Move cursor by offset from current position.

    Args:
        dx: Horizontal offset (positive = right)
        dy: Vertical offset (positive = down)
    """
    current_x, current_y = ctrl.mouse_pos()
    ctrl.mouse_move(current_x + dx, current_y + dy)


def get_screen_for_mouse():
    """
    Get the screen containing the current cursor position.

    Returns:
        Screen object containing the cursor, or first screen if not found
    """
    x, y = ctrl.mouse_pos()
    point = Point2d(x, y)

    for screen in ui.screens():
        if screen.rect.contains(point):
            return screen

    screens = ui.screens()
    return screens[0] if screens else None


def get_screen_rect(screen=None) -> Tuple[float, float, float, float]:
    """
    Get bounds of a screen.

    Args:
        screen: Screen object. If None, uses screen containing mouse.

    Returns:
        Tuple of (x, y, width, height)
    """
    if screen is None:
        screen = get_screen_for_mouse()

    if screen is None:
        # Fallback dimensions
        return (0, 0, 1920, 1080)

    rect = screen.rect
    return (rect.x, rect.y, rect.width, rect.height)


def get_screen_bounds(screen=None) -> Tuple[float, float, float, float]:
    """
    Get screen bounds as (left, top, right, bottom).

    Args:
        screen: Screen object. If None, uses screen containing mouse.

    Returns:
        Tuple of (left, top, right, bottom)
    """
    x, y, w, h = get_screen_rect(screen)
    return (x, y, x + w, y + h)
