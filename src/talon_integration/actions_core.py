"""
Core mouse clock actions - activate, close, radius control.

This module owns the ctx_tags Context for managing mouse_clock_showing tag.
Other modules should use set_mouse_clock_tags() and clear_mouse_clock_tags()
instead of manipulating ctx_tags directly.
"""

from talon import Context, Module, actions
from .instance import get_mouse_clock_instance
from ..core.pipeline import get_start_mode

mod = Module()

# Context for dynamic tags - owned by this module
ctx_tags = Context()
ctx_tags.matches = r"""
tag: user.use_mouse_clock
"""


def set_mouse_clock_tags(tags: list):
    """Set the mouse clock tags. Called when showing clock or changing modes."""
    from ..core.logger import log_tags
    ctx_tags.tags = tags
    log_tags(tags)


def clear_mouse_clock_tags():
    """Clear all mouse clock tags. Called when closing clock."""
    from ..core.logger import log_debug
    ctx_tags.tags = []
    log_debug("Tags cleared")

@mod.action_class
class CoreActions:
    def mouse_clock_activate():
        """Show mouse clock"""
        mouse_clock = get_mouse_clock_instance()
        if not mouse_clock.active_canvas:
            mouse_clock.setup()
        mouse_clock.show()
        mouse_clock.clear_state()
        # Start at the beginning of the view pipeline
        start_mode = get_start_mode()
        mouse_clock.set_mode(start_mode, set_mouse_clock_tags)

    def mouse_clock_show():
        """Alias for mouse_clock_activate"""
        actions.user.mouse_clock_activate()

    def mouse_clock_close():
        """Close the mouse clock, clock ring, and hats info panel"""
        clear_mouse_clock_tags()
        mouse_clock = get_mouse_clock_instance()
        mouse_clock.clear_state()
        mouse_clock.close()
        actions.user.clock_ring_hide()
        actions.user.hats_info_hide()

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
        mouse_clock.core.clear_state()
        mouse_clock.recenter()

