"""
Core mouse clock actions - activate, close, radius control.

This module owns the ctx_tags Context for managing mouse_clock_showing tag.
Other modules should use set_mouse_clock_tags() and clear_mouse_clock_tags()
instead of manipulating ctx_tags directly.
"""

from talon import Context, Module, actions
from .instance import get_mouse_clock_instance
from .adapter import DISPLAY_MODE_INFO
from ..core.logger import log_info

print("reloaded trillium/mouse-clock/src/talon_integration/actions_core.py 7")

mod = Module()

# Context for dynamic tags - owned by this module
ctx_tags = Context()
ctx_tags.matches = r"""
tag: user.use_mouse_clock
"""


def set_mouse_clock_tags(tags: list):
    """Set the mouse clock tags. Called when showing clock or changing modes."""
    ctx_tags.tags = tags
    print(f"[DEBUG] Set ctx_tags.tags to: {ctx_tags.tags}")


def clear_mouse_clock_tags():
    """Clear all mouse clock tags. Called when closing clock."""
    ctx_tags.tags = []
    print(f"[DEBUG] Cleared ctx_tags.tags")

@mod.action_class
class CoreActions:
    def mouse_clock_activate():
        """Show mouse clock"""
        mouse_clock = get_mouse_clock_instance()
        if not mouse_clock.active_canvas:
            mouse_clock.setup()
        mouse_clock.show()
        mouse_clock.clear_state()
        # Set tags based on current display mode
        tags = ["user.mouse_clock_showing"]
        if mouse_clock.get_display_mode() == DISPLAY_MODE_INFO:
            tags.append("user.mouse_clock_info_mode")
        set_mouse_clock_tags(tags)

    def mouse_clock_show():
        """Alias for mouse_clock_activate"""
        actions.user.mouse_clock_activate()

    def mouse_clock_close():
        """Close the mouse clock"""
        clear_mouse_clock_tags()
        mouse_clock = get_mouse_clock_instance()
        mouse_clock.close()

    def mouse_clock_toggle():
        """Toggle mouse clock on/off"""
        mouse_clock = get_mouse_clock_instance()
        if mouse_clock.active_canvas:
            actions.user.mouse_clock_close()
        else:
            actions.user.mouse_clock_activate()

    def mouse_clock_go_back():
        """Revert to the previous mouse position"""
        mouse_clock = get_mouse_clock_instance()
        mouse_clock.go_back()

    def mouse_clock_widen():
        """Increases the radius of the circle"""
        mouse_clock = get_mouse_clock_instance()
        mouse_clock.widen_radius()
        if mouse_clock.core.last_command:
            letters, colors = mouse_clock.core.last_command
            x, y = mouse_clock.calculate_mouse_position(letters, colors)
            mouse_clock.move_mouse(x, y)

    def mouse_clock_narrow():
        """Decreases the radius of the circle"""
        mouse_clock = get_mouse_clock_instance()
        mouse_clock.narrow_radius()
        if mouse_clock.core.last_command:
            letters, colors = mouse_clock.core.last_command
            x, y = mouse_clock.calculate_mouse_position(letters, colors)
            mouse_clock.move_mouse(x, y)

    def mouse_clock_set_radius(num: int):
        """Sets the radius of mouse clock"""
        mouse_clock = get_mouse_clock_instance()
        mouse_clock.set_radius(num)

    def mouse_clock_recenter():
        """Recenter the clock at the current mouse position"""
        mouse_clock = get_mouse_clock_instance()
        mouse_clock.recenter()

    def mouse_clock_scoot(num: int, letter_list: str):
        """Shift the whole clock a direction"""
        # Note: This was a stub in the original code
        log_info(f"[scoot] {num} {letter_list}")
