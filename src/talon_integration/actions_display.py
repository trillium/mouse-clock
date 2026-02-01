"""
Mouse clock display mode actions.
"""

from talon import Module
from .instance import get_mouse_clock_instance
from .adapter import DISPLAY_MODE_CIRCLES, DISPLAY_MODE_BOXES, DISPLAY_MODE_HYBRID, DISPLAY_MODE_GRID

mod = Module()

# Display modes in rotation order
DISPLAY_MODES = [DISPLAY_MODE_CIRCLES, DISPLAY_MODE_BOXES, DISPLAY_MODE_GRID]


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

    def mouse_clock_cycle_mode():
        """Cycle to next display mode."""
        mouse_clock = get_mouse_clock_instance()
        current = mouse_clock.get_display_mode()
        try:
            idx = DISPLAY_MODES.index(current)
            next_idx = (idx + 1) % len(DISPLAY_MODES)
        except ValueError:
            next_idx = 0
        next_mode = DISPLAY_MODES[next_idx]
        mouse_clock.set_display_mode(next_mode)
        print(f"Display mode: {next_mode}")
