_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Canvas lifecycle management for MouseClockTalonAdapter.

Module-level canvas registry and setup_canvases() helper.
No Talon registrations — pure utility.
"""

from talon import canvas, ui
from talon.types.point import Point2d

# Module-level canvas registry - tracks ALL canvases ever created
# This allows cleanup of stale canvases after hot reload
_all_canvases = []


def _cleanup_all_canvases():
    """Force close all registered canvases. Called on module reload."""
    global _all_canvases
    for c in _all_canvases:
        try:
            c.close()
        except Exception:
            pass
    _all_canvases = []


# Clean up any stale canvases from previous module load
_cleanup_all_canvases()


def setup_canvases(adapter, update_position: bool = True):
    """Set up canvases for all screens.

    Args:
        adapter: MouseClockTalonAdapter instance
        update_position: If True, read current mouse position. If False, use existing center.
    """
    if update_position:
        adapter.get_mouse_position()

    screens = ui.screens()

    # Close any existing canvases
    if hasattr(adapter, 'canvases') and adapter.canvases:
        for canvas_obj in adapter.canvases:
            canvas_obj.close()
    adapter.canvases = []

    # Create a canvas for each screen
    global _all_canvases
    for screen in screens:
        canvas_obj = canvas.Canvas.from_screen(screen)
        adapter.canvases.append(canvas_obj)
        _all_canvases.append(canvas_obj)  # Track in module-level registry
        if adapter.active:
            canvas_obj.register("draw", adapter.draw)
            canvas_obj.freeze()

    # For compatibility, set active_canvas and screen to the one under the mouse
    mouse_point = Point2d(adapter.core.center_x, adapter.core.center_y)
    screen_found = None
    for screen in screens:
        if screen.rect.contains(mouse_point):
            screen_found = screen
            break
    if screen_found is None:
        screen_found = screens[0]
    adapter.screen = screen_found
    adapter.active_canvas = adapter.canvases[screens.index(adapter.screen)]
