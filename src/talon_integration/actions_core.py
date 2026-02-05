"""
Core mouse clock actions - activate, close, radius control.
"""

from talon import Module
from talon import actions
from .instance import ctx_tags, get_mouse_clock_instance
from .adapter import DISPLAY_MODE_INFO
from ..core.logger import log_info

print("reloaded trillium/mouse-clock/src/talon_integration/actions_core.py 6")

mod = Module()

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
        ctx_tags.tags = tags
        print(f"[DEBUG] Set ctx_tags.tags to: {ctx_tags.tags}")

    def mouse_clock_show():
        """Alias for mouse_clock_activate"""
        actions.user.mouse_clock_activate()

    def mouse_clock_close():
        """Close the mouse clock"""
        ctx_tags.tags = []  # Clears both mouse_clock_showing and mouse_clock_info_mode
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
