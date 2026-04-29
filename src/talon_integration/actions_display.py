"""
Mouse clock display mode actions.
"""

from talon import Module
from .actions_core import set_mouse_clock_tags, ctx_tags
from .instance import get_mouse_clock_instance
from ..core.constants import DISPLAY_MODE_CIRCLES, DISPLAY_MODE_CLOCK_LETTERS, DISPLAY_MODE_DENSE_GRID, DISPLAY_MODES

mod = Module()


def _set_mode_and_refresh(mode: str):
    """Set display mode using unified mode system."""
    mouse_clock = get_mouse_clock_instance()

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

    def mouse_clock_mode_dense_grid():
        """Switch to dense grid display mode (dense colored letter matrix)."""
        _set_mode_and_refresh(DISPLAY_MODE_DENSE_GRID)

    def mouse_clock_column_preset(preset: str):
        """Set column layout to a named preset and refresh."""
        from ..features.clock_letters.config import set_column_preset
        set_column_preset(preset)
        mouse_clock = get_mouse_clock_instance()
        if mouse_clock.active:
            mouse_clock.refresh_canvases()

    def mouse_clock_column_preset_cycle():
        """Cycle through column layout presets and refresh."""
        from ..features.clock_letters.config import cycle_column_preset
        new_preset = cycle_column_preset()
        print(f"Column preset: {new_preset}")
        mouse_clock = get_mouse_clock_instance()
        if mouse_clock.active:
            mouse_clock.refresh_canvases()

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
        _set_mode_and_refresh(next_mode)

    def mouse_clock_cycle_mode_previous():
        """Cycle to previous display mode."""
        mouse_clock = get_mouse_clock_instance()
        current = mouse_clock.get_display_mode()
        try:
            idx = DISPLAY_MODES.index(current)
            prev_idx = (idx - 1) % len(DISPLAY_MODES)
        except ValueError:
            prev_idx = 0
        prev_mode = DISPLAY_MODES[prev_idx]
        _set_mode_and_refresh(prev_mode)
        print(f"Display mode: {prev_mode}")

