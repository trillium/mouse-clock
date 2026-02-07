"""
Mouse clock display mode actions.
"""

from talon import Module
from .actions_core import set_mouse_clock_tags, ctx_tags

mod = Module()

# Display mode constants (inlined to avoid importing adapter.py at module level)
DISPLAY_MODE_CIRCLES = "circles"
DISPLAY_MODE_CLOCK_LETTERS = "clock_letters"

# Display modes in rotation order
DISPLAY_MODES = [DISPLAY_MODE_CIRCLES, DISPLAY_MODE_CLOCK_LETTERS]


def _get_instance():
    from .instance import get_mouse_clock_instance
    return get_mouse_clock_instance()


def _set_mode_and_refresh(mode: str):
    """Set display mode using unified mode system."""
    mouse_clock = _get_instance()

    # Activate clock if not already showing
    if not mouse_clock.active:
        if not mouse_clock.active_canvas:
            mouse_clock.setup()
        mouse_clock.show()

    # Use unified mode setter - handles both display mode and tags
    mouse_clock.set_mode(mode, set_mouse_clock_tags)


@mod.action_class
class DisplayActions:
    def mouse_clock_mode_circles():
        """Switch to circles display mode."""
        _set_mode_and_refresh(DISPLAY_MODE_CIRCLES)

    def mouse_clock_mode_clock_letters():
        """Switch to clock letters display mode (letters in colors)."""
        _set_mode_and_refresh(DISPLAY_MODE_CLOCK_LETTERS)

    def mouse_clock_get_mode() -> str:
        """Get current display mode."""
        mouse_clock = _get_instance()
        return mouse_clock.get_display_mode()

    def mouse_clock_cycle_mode():
        """Cycle to next display mode."""
        mouse_clock = _get_instance()
        current = mouse_clock.get_display_mode()
        try:
            idx = DISPLAY_MODES.index(current)
            next_idx = (idx + 1) % len(DISPLAY_MODES)
        except ValueError:
            next_idx = 0
        next_mode = DISPLAY_MODES[next_idx]
        _set_mode_and_refresh(next_mode)

    def mouse_clock_cycle_mode_previous():
        """Cycle to previous display mode."""
        mouse_clock = _get_instance()
        current = mouse_clock.get_display_mode()
        try:
            idx = DISPLAY_MODES.index(current)
            prev_idx = (idx - 1) % len(DISPLAY_MODES)
        except ValueError:
            prev_idx = 0
        prev_mode = DISPLAY_MODES[prev_idx]
        _set_mode_and_refresh(prev_mode)
        print(f"Display mode: {prev_mode}")

