_V = "0.0.2"; print(f"[v{_V}] {__name__}")
"""
Core mouse clock actions - activate, close, radius control.

This module owns the ctx_tags Context for managing mouse_clock_showing tag.
Other modules should use set_mouse_clock_tags() and clear_mouse_clock_tags()
instead of manipulating ctx_tags directly.

NOTE: Imports from .instance, .adapter, and ..core.logger are deferred to
function bodies to prevent Talon cold-start [ ] cascade. These modules come
later alphabetically than actions_core.py, so importing them at module level
causes Python to load them before Talon's file scanner reaches them.
"""

from talon import Context, Module, actions

mod = Module()

# Context for dynamic tags - owned by this module
ctx_tags = Context()
ctx_tags.matches = r"""
tag: user.use_mouse_clock
"""


def _get_instance():
    from .instance import get_mouse_clock_instance
    return get_mouse_clock_instance()


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
        mouse_clock = _get_instance()
        if not mouse_clock.active_canvas:
            mouse_clock.setup()
        mouse_clock.show()
        mouse_clock.clear_state()
        # Use unified mode system - sets both display mode and tags
        current_mode = mouse_clock.get_display_mode()
        mouse_clock.set_mode(current_mode, set_mouse_clock_tags)

    def mouse_clock_show():
        """Alias for mouse_clock_activate"""
        actions.user.mouse_clock_activate()

    def mouse_clock_close():
        """Close the mouse clock, color pie, and hats info panel"""
        clear_mouse_clock_tags()
        mouse_clock = _get_instance()
        mouse_clock.close()
        actions.user.color_pie_hide()
        actions.user.hats_info_hide()

    def mouse_clock_toggle():
        """Toggle mouse clock on/off"""
        mouse_clock = _get_instance()
        if mouse_clock.active_canvas:
            actions.user.mouse_clock_close()
        else:
            actions.user.mouse_clock_activate()

    def mouse_clock_go_back():
        """Revert to the previous mouse position"""
        mouse_clock = _get_instance()
        mouse_clock.go_back()

    def mouse_clock_widen():
        """Increases the radius of the circle"""
        mouse_clock = _get_instance()
        mouse_clock.widen_radius()
        if mouse_clock.core.last_command:
            letters, colors = mouse_clock.core.last_command
            x, y = mouse_clock.calculate_mouse_position(letters, colors)
            mouse_clock.move_mouse(x, y)

    def mouse_clock_narrow():
        """Decreases the radius of the circle"""
        mouse_clock = _get_instance()
        mouse_clock.narrow_radius()
        if mouse_clock.core.last_command:
            letters, colors = mouse_clock.core.last_command
            x, y = mouse_clock.calculate_mouse_position(letters, colors)
            mouse_clock.move_mouse(x, y)

    def mouse_clock_set_radius(num: int):
        """Sets the radius of mouse clock"""
        mouse_clock = _get_instance()
        mouse_clock.set_radius(num)

    def mouse_clock_recenter():
        """Recenter the clock at the current mouse position"""
        mouse_clock = _get_instance()
        mouse_clock.recenter()

    def mouse_clock_scoot(num: int, letter_list: str):
        """Shift the whole clock a direction"""
        from ..core.logger import log_info
        # Note: This was a stub in the original code
        log_info(f"[scoot] {num} {letter_list}")
