"""
Mouse clock debug and logging actions.
"""

from talon import Module, actions, ctrl

mod = Module()


def _get_instance():
    from .instance import get_mouse_clock_instance
    return get_mouse_clock_instance()


@mod.action_class
class DebugActions:
    def mouse_clock_debug_position():
        """Print current mouse position and debug info to log file."""
        from ..core.logger import log_info, log_separator
        mouse_clock = _get_instance()
        current_x, current_y = ctrl.mouse_pos()
        screen_rect = mouse_clock.get_screen_rect()

        log_separator()
        log_info("[DEBUG] Mouse Clock Position Info")
        log_separator()
        log_info(f"Current mouse position: ({current_x}, {current_y})")
        log_info(f"Clock center: ({mouse_clock.core.center_x}, {mouse_clock.core.center_y})")
        log_info(f"Clock active: {mouse_clock.active}")
        log_info(f"Clock radius: {mouse_clock.core.radius}")
        log_info(f"Screen bounds: left={screen_rect[0]}, top={screen_rect[1]}, right={screen_rect[2]}, bottom={screen_rect[3]}")
        if mouse_clock.core.last_command:
            log_info(f"Last command: letters={mouse_clock.core.last_command[0]}, colors={mouse_clock.core.last_command[1]}")
        log_info(f"History length: {len(mouse_clock.core.history)}")
        log_separator()

    def mouse_clock_show_log_location():
        """Show the current log file location."""
        from ..core.logger import log_info, get_current_log_file
        log_file = get_current_log_file()
        if log_file:
            log_info(f"Current log file: {log_file}")
            actions.user.boolean_print("Mouse Clock", f"Logging to: {log_file}")
        else:
            actions.user.boolean_print("Mouse Clock", "No log file currently active")

    def mouse_clock_log_position():
        """Log the current mouse position immediately."""
        from ..core.logger import log_info, log_separator
        current_x, current_y = ctrl.mouse_pos()
        log_separator()
        log_info(f"[POSITION CHECK] Current mouse position: ({current_x}, {current_y})")
        log_separator()
        actions.user.boolean_print("Mouse Clock", f"Logged position: ({current_x}, {current_y})")

    def mouse_clock_log_marker(text: str):
        """Log a custom marker/comment for context."""
        from ..core.logger import log_info, log_separator
        log_separator()
        log_info(f"[MARKER] {text}")
        log_separator()
        actions.user.boolean_print("Mouse Clock", f"Marker logged: {text}")
