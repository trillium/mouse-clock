"""
Canvas lifecycle management for overlay systems.

Provides a consistent API for creating, managing, and disposing of
Talon canvas overlays, with multi-monitor support.
"""

from typing import Callable, List, Optional, Tuple
from talon import canvas, ui
from talon.types.point import Point2d


def create_overlay_canvas(screen=None, draw_callback: Callable = None):
    """
    Create a transparent overlay canvas for a screen.

    Args:
        screen: Talon screen object. If None, uses first screen.
        draw_callback: Optional draw function to register immediately.

    Returns:
        Canvas object
    """
    if screen is None:
        screens = ui.screens()
        screen = screens[0] if screens else None

    if screen is None:
        raise RuntimeError("No screens available")

    canvas_obj = canvas.Canvas.from_screen(screen)

    if draw_callback:
        canvas_obj.register("draw", draw_callback)

    return canvas_obj


def create_all_screen_canvases(draw_callback: Callable = None) -> List:
    """
    Create overlay canvases for all screens.

    Args:
        draw_callback: Optional draw function to register on each canvas.

    Returns:
        List of canvas objects (one per screen)
    """
    canvases = []
    for screen in ui.screens():
        canvas_obj = create_overlay_canvas(screen, draw_callback)
        canvases.append(canvas_obj)
    return canvases


def clear_canvas(canvas_obj):
    """
    Remove all drawings from canvas.

    Note: In Talon, this is typically done by unregistering/re-registering
    the draw callback or calling freeze() to trigger a redraw.

    Args:
        canvas_obj: Canvas to clear
    """
    # Trigger a redraw which clears and redraws
    canvas_obj.freeze()


def refresh_canvas(canvas_obj):
    """
    Trigger canvas redraw (freeze).

    Args:
        canvas_obj: Canvas to refresh
    """
    canvas_obj.freeze()


def refresh_all_canvases(canvases: List):
    """
    Refresh all canvases.

    Args:
        canvases: List of canvas objects
    """
    for canvas_obj in canvases:
        canvas_obj.freeze()


def close_canvas(canvas_obj, draw_callback: Callable = None):
    """
    Dispose of canvas resources.

    Args:
        canvas_obj: Canvas to close
        draw_callback: If provided, unregisters this callback before closing
    """
    if draw_callback:
        try:
            canvas_obj.unregister("draw", draw_callback)
        except Exception:
            pass  # Already unregistered
    canvas_obj.close()


def close_all_canvases(canvases: List, draw_callback: Callable = None):
    """
    Close all canvases and clear the list.

    Args:
        canvases: List of canvas objects
        draw_callback: If provided, unregisters this callback from each
    """
    for canvas_obj in canvases:
        close_canvas(canvas_obj, draw_callback)
    canvases.clear()


def get_canvas_for_point(
    point: Tuple[float, float],
    canvases: List,
    screens: List = None
) -> Optional[object]:
    """
    Find which canvas contains a given point (multi-monitor support).

    Args:
        point: Point to check (x, y)
        canvases: List of canvas objects (one per screen)
        screens: Optional list of screens (auto-fetched if not provided)

    Returns:
        Canvas containing the point, or None if not found
    """
    if screens is None:
        screens = ui.screens()

    if len(canvases) != len(screens):
        return None

    x, y = point
    point2d = Point2d(x, y)

    for i, screen in enumerate(screens):
        if screen.rect.contains(point2d):
            return canvases[i]

    return None


def get_screen_for_point(point: Tuple[float, float]):
    """
    Find which screen contains a given point.

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
