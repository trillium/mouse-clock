"""
Mouse clock display mode actions.
"""

from .instance import mod, get_mouse_clock_instance
from .adapter import DISPLAY_MODE_CIRCLES, DISPLAY_MODE_BOXES, DISPLAY_MODE_HYBRID, DISPLAY_MODE_GRID


@mod.action_class
class DisplayActions:
    def mouse_clock_mode_circles():
        """Switch to circles display mode."""
        mouse_clock = get_mouse_clock_instance()
        mouse_clock.set_display_mode(DISPLAY_MODE_CIRCLES)

    def mouse_clock_mode_boxes():
        """Switch to boxes display mode."""
        mouse_clock = get_mouse_clock_instance()
        mouse_clock.set_display_mode(DISPLAY_MODE_BOXES)

    def mouse_clock_mode_hybrid():
        """Switch to hybrid display mode (boxes + circles)."""
        mouse_clock = get_mouse_clock_instance()
        mouse_clock.set_display_mode(DISPLAY_MODE_HYBRID)

    def mouse_clock_mode_grid():
        """Switch to grid display mode (letters + colors)."""
        mouse_clock = get_mouse_clock_instance()
        mouse_clock.set_display_mode(DISPLAY_MODE_GRID)

    def mouse_clock_get_mode() -> str:
        """Get current display mode."""
        mouse_clock = get_mouse_clock_instance()
        return mouse_clock.get_display_mode()
