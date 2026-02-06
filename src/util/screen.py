_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Screen and window utilities for multi-monitor support.

Provides functions for querying screen layouts, window positions,
and constraining points to screen bounds.
"""

from typing import Tuple, List, Optional
from talon import ui
from talon.types.point import Point2d


def get_all_screens() -> List:
    """
    List all available screens.

    Returns:
        List of Talon screen objects
    """
    return ui.screens()


def get_primary_screen():
    """
    Get the primary/main screen.

    Returns:
        Primary screen object, or first screen if no primary
    """
    screens = ui.screens()
    # Talon typically returns primary first, or check for main attribute
    for screen in screens:
        if hasattr(screen, 'main') and screen.main:
            return screen
    return screens[0] if screens else None


def get_active_window_rect() -> Optional[Tuple[float, float, float, float]]:
    """
    Get bounds of the currently focused window.

    Returns:
        Tuple of (x, y, width, height) or None if no active window
    """
    try:
        window = ui.active_window()
        if window and window.rect:
            rect = window.rect
            return (rect.x, rect.y, rect.width, rect.height)
    except Exception:
        pass
    return None


def point_to_screen(point: Tuple[float, float]):
    """
    Find which screen contains a point.

    Args:
        point: Point to check (x, y)

    Returns:
        Screen containing the point, or first screen if not found
    """
    x, y = point
    point2d = Point2d(x, y)

    for screen in ui.screens():
        if screen.rect.contains(point2d):
            return screen

    screens = ui.screens()
    return screens[0] if screens else None


def clamp_to_screen(
    point: Tuple[float, float],
    screen=None,
    margin: float = 0
) -> Tuple[float, float]:
    """
    Keep point within screen bounds.

    Args:
        point: Point to clamp (x, y)
        screen: Screen to clamp to. If None, uses screen containing point.
        margin: Pixels of margin from screen edge

    Returns:
        Clamped point (x, y)
    """
    x, y = point

    if screen is None:
        screen = point_to_screen(point)

    if screen is None:
        return point

    rect = screen.rect
    min_x = rect.x + margin
    max_x = rect.x + rect.width - margin
    min_y = rect.y + margin
    max_y = rect.y + rect.height - margin

    clamped_x = max(min_x, min(x, max_x))
    clamped_y = max(min_y, min(y, max_y))

    return (clamped_x, clamped_y)


def screen_center(screen=None) -> Tuple[float, float]:
    """
    Get center point of a screen.

    Args:
        screen: Screen to get center of. If None, uses primary screen.

    Returns:
        Center point (x, y)
    """
    if screen is None:
        screen = get_primary_screen()

    if screen is None:
        return (960.0, 540.0)  # Fallback center

    rect = screen.rect
    return (rect.x + rect.width / 2, rect.y + rect.height / 2)


def get_screen_rect(screen=None) -> Tuple[float, float, float, float]:
    """
    Get screen bounds as (x, y, width, height).

    Args:
        screen: Screen to query. If None, uses primary screen.

    Returns:
        Tuple of (x, y, width, height)
    """
    if screen is None:
        screen = get_primary_screen()

    if screen is None:
        return (0, 0, 1920, 1080)

    rect = screen.rect
    return (rect.x, rect.y, rect.width, rect.height)


def get_screen_bounds(screen=None) -> Tuple[float, float, float, float]:
    """
    Get screen bounds as (left, top, right, bottom).

    Args:
        screen: Screen to query. If None, uses primary screen.

    Returns:
        Tuple of (left, top, right, bottom)
    """
    x, y, w, h = get_screen_rect(screen)
    return (x, y, x + w, y + h)
