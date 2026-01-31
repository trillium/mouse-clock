"""
Talon integration bridge for the mouse clock.

This module provides the Talon-specific wrapper around the core mouse clock logic,
handling canvas management, mouse control, and voice command actions.
"""

from typing import List
from talon import Context, Module, canvas, ctrl, ui
from talon.types.point import Point2d

from ..core import config
from ..core.mouse_clock import MouseClockCore, flip_letter_to_opposite, parse_voice_inputs
from ..core.logger import logger, log_debug, log_info, log_warning, log_separator, initialize_logger, get_current_log_file
from ..rendering.canvas import draw_mouse_clock


ctx = Context()
ctx.lists["user.mouse"] = ["mouse"]

mod = Module()

mod.tag("use_mouse_clock", desc="Tag enables using mouse clock")
mod.tag("mouse_clock_showing", desc="Tag indicates whether the mouse clock is showing")

# Only use if tag is active
ctx.matches = r"""
tag: user.use_mouse_clock
"""


class MouseClockTalonAdapter:
    """
    Talon-specific adapter for the MouseClockCore.

    This class wraps the core mouse clock logic and provides Talon-specific
    functionality like canvas management, mouse control, and screen handling.
    """

    def __init__(self):
        # Initialize a new log file for this instance
        log_file = initialize_logger()
        log_info(f"MouseClockTalonAdapter instance created")
        log_info(f"Logging to: {log_file}")

        self.core = MouseClockCore()
        self.screen = None
        self.active_canvas = None
        self.canvases = []
        self.active = False

    def get_mouse_position(self) -> tuple[float, float]:
        """Get current mouse position from Talon and update core."""
        mouse_x, mouse_y = ctrl.mouse_pos()
        self.core.update_center(mouse_x, mouse_y)
        return mouse_x, mouse_y

    def get_screen_rect(self) -> tuple[float, float, float, float]:
        """Get the screen rectangle bounds for the current screen."""
        if not self.screen:
            screens = ui.screens()
            self.screen = screens[0] if screens else None

        if self.screen:
            rect = self.screen.rect
            return (rect.x, rect.y, rect.x + rect.width, rect.y + rect.height)

        # Fallback bounds
        return (0, 0, config.DEFAULT_SCREEN_WIDTH, config.DEFAULT_SCREEN_HEIGHT)

    def calculate_mouse_position(
        self,
        letter_list: List[str],
        color_list: List[str],
        is_repeat: bool = False
    ) -> tuple[float, float]:
        """Calculate mouse position using core logic with Talon screen info."""
        screen_rect = self.get_screen_rect()
        return self.core.calculate_mouse_position(
            letter_list,
            color_list,
            is_repeat=is_repeat,
            screen_rect=screen_rect,
            clock_active=self.active
        )

    def setup(self, update_position: bool = True):
        """Set up canvases for all screens.

        Args:
            update_position: If True, read current mouse position. If False, use existing center.
        """
        if update_position:
            self.get_mouse_position()

        screens = ui.screens()

        # Close any existing canvases
        if hasattr(self, 'canvases') and self.canvases:
            for canvas_obj in self.canvases:
                canvas_obj.close()
        self.canvases = []

        # Create a canvas for each screen
        for screen in screens:
            canvas_obj = canvas.Canvas.from_screen(screen)
            self.canvases.append(canvas_obj)
            if self.active:
                canvas_obj.register("draw", self.draw)
                canvas_obj.freeze()

        # For compatibility, set active_canvas and screen to the one under the mouse
        mouse_point = Point2d(self.core.center_x, self.core.center_y)
        screen_found = None
        for screen in screens:
            if screen.rect.contains(mouse_point):
                screen_found = screen
                break
        if screen_found is None:
            screen_found = screens[0]
        self.screen = screen_found
        self.active_canvas = self.canvases[screens.index(self.screen)]

    def show(self):
        """Show the mouse clock on all canvases."""
        if self.active:
            return
        for canvas_obj in self.canvases:
            canvas_obj.register("draw", self.draw)
            canvas_obj.freeze()
        self.active = True

    def close(self):
        """Close the mouse clock and clean up canvases."""
        if not self.active:
            return
        for canvas_obj in self.canvases:
            canvas_obj.unregister("draw", self.draw)
            canvas_obj.close()
        self.canvases = []
        self.active_canvas = None
        self.active = False

    def draw(self, canvas_obj):
        """Draw callback for Talon canvas."""
        draw_mouse_clock(
            canvas_obj,
            self.core.center_x,
            self.core.center_y,
            self.core.radius,
            config.COLOR_LIST,
            config.COLOR_ACTIVE,
            config.COLOR_TEXT
        )

    def move_mouse(self, x: float, y: float):
        """Move the mouse to the specified position and add to history."""
        ctrl.mouse_move(x, y)
        self.core.add_to_history(x, y)

    def go_back(self):
        """Revert to the previous mouse position."""
        position = self.core.pop_from_history()
        if position:
            x, y = position
            ctrl.mouse_move(x, y)

    def widen_radius(self):
        """Increase the radius of the circle."""
        self.core.widen_radius()
        if self.active and self.active_canvas:
            self.active_canvas.freeze()

    def narrow_radius(self):
        """Decrease the radius of the circle."""
        self.core.narrow_radius()
        if self.active and self.active_canvas:
            self.active_canvas.freeze()

    def set_radius(self, num: int):
        """Set the radius to a specific value and refresh the canvas if active."""
        self.core.set_radius(num)
        if self.active and self.active_canvas:
            self.active_canvas.freeze()

    def clear_state(self):
        """Clear the command state."""
        self.core.clear_state()

    def recenter(self):
        """Recenter the clock at the current mouse position and redraw."""
        # Get current mouse position
        current_x, current_y = ctrl.mouse_pos()

        # Recenter the clock at current position
        self.get_mouse_position()

        # If there was a last command, recalculate and move to the same relative position
        if self.core.last_command and (self.core.last_command[0] or self.core.last_command[1]):
            letters, colors = self.core.last_command
            x, y = self.calculate_mouse_position(letters, colors)
            self.move_mouse(x, y)

        if self.active:
            # Redraw all canvases with the new center
            for canvas_obj in self.canvases:
                canvas_obj.freeze()


# Global instance - using factory function for better control
_mouse_clock_instance = None


def get_mouse_clock_instance() -> MouseClockTalonAdapter:
    """Get the global mouse clock instance (singleton pattern)."""
    global _mouse_clock_instance
    if _mouse_clock_instance is None:
        _mouse_clock_instance = MouseClockTalonAdapter()
    return _mouse_clock_instance


@mod.action_class
class ClockActions:
    def mouse_clock_activate():
        """Show mouse clock"""
        mouse_clock = get_mouse_clock_instance()
        if not mouse_clock.active_canvas:
            mouse_clock.setup()
        mouse_clock.show()
        mouse_clock.clear_state()
        ctx.tags = ["user.mouse_clock_showing"]

    def mouse_clock_close():
        """Close the mouse clock"""
        ctx.tags = []
        mouse_clock = get_mouse_clock_instance()
        mouse_clock.close()

    def mouse_clock_move_multiple(letters_colors: List[str]):
        """Move the mouse to the intersection(s) of letters and colors.

        If the same command is repeated, recenter the clock at the current position
        and apply the command again, effectively moving in that direction.
        """
        mouse_clock = get_mouse_clock_instance()
        typed_expressions = parse_voice_inputs(letters_colors)
        letters = typed_expressions['letters']
        colors = typed_expressions['colors']

        # Validate: Must have at least one letter (direction)
        if not letters:
            log_warning("[mouse_clock] Ignoring command - no direction specified (letters required)")
            return

        # Store as the original command (non-reversed)
        mouse_clock.core.original_command = (letters, colors)

        # Check if this exact command was just executed
        is_repeat = (mouse_clock.core.last_command == (letters, colors) and
                     mouse_clock.core.last_command != ([], []) and
                     letters and colors)

        if is_repeat:
            # Same command repeated - recenter at current position
            mouse_clock.get_mouse_position()
            # Redraw all canvases with the new center
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()

        x, y = mouse_clock.calculate_mouse_position(letters, colors, is_repeat=is_repeat)
        mouse_clock.move_mouse(x, y)

    def mouse_clock_move_opposite():
        """Move the mouse in the opposite direction of the original command."""
        mouse_clock = get_mouse_clock_instance()

        if not mouse_clock.core.original_command or mouse_clock.core.original_command == ([], []):
            log_warning("[opposite] No original command to reverse")
            return

        orig_letters, orig_colors = mouse_clock.core.original_command

        if not orig_letters:
            log_warning("[opposite] No letters in original command to reverse")
            return

        # Always flip from the ORIGINAL letters
        opposite_letters = [flip_letter_to_opposite(letter) for letter in orig_letters]

        # Check if we're repeating the reverse command
        is_repeat_reverse = (mouse_clock.core.last_command == (opposite_letters, orig_colors))

        if is_repeat_reverse:
            # Repeating reverse - recenter and move away again
            log_info(f"[opposite] Repeating reverse - recentering and moving away")
            mouse_clock.get_mouse_position()
            # Redraw all canvases with the new center
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()

        log_info(f"[opposite] Original letters: {orig_letters} -> Opposite: {opposite_letters}")
        log_info(f"[opposite] Colors: {orig_colors}")

        x, y = mouse_clock.calculate_mouse_position(opposite_letters, orig_colors, is_repeat=is_repeat_reverse)
        mouse_clock.move_mouse(x, y)

    def mouse_clock_move_original():
        """Move the mouse in the original direction (opposite of reverse)."""
        mouse_clock = get_mouse_clock_instance()

        if not mouse_clock.core.original_command or mouse_clock.core.original_command == ([], []):
            log_warning("[original] No original command to move toward")
            return

        orig_letters, orig_colors = mouse_clock.core.original_command

        if not orig_letters:
            log_warning("[original] No letters in original command")
            return

        # Check if we're repeating the original direction command
        is_repeat_original = (mouse_clock.core.last_command == (orig_letters, orig_colors))

        if is_repeat_original:
            # Repeating original - recenter and move toward again
            log_info(f"[original] Repeating original direction - recentering and moving toward")
            mouse_clock.get_mouse_position()
            # Redraw all canvases with the new center
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()

        log_info(f"[original] Moving toward original direction: {orig_letters}")
        log_info(f"[original] Colors: {orig_colors}")

        x, y = mouse_clock.calculate_mouse_position(orig_letters, orig_colors, is_repeat=is_repeat_original)
        mouse_clock.move_mouse(x, y)

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

    def mouse_clock_scoot(num: int, letter_list: str):
        """Shift the whole clock a direction"""
        # Note: This was a stub in the original code
        log_info(f"[scoot] {num} {letter_list}")

    def mouse_clock_recenter():
        """Recenter the clock at the current mouse position"""
        mouse_clock = get_mouse_clock_instance()
        mouse_clock.recenter()

    def mouse_clock_recenter_and_move(letters_colors: List[str]):
        """Recenter clock at current position, then move to specified location"""
        mouse_clock = get_mouse_clock_instance()
        mouse_clock.recenter()
        typed_expressions = parse_voice_inputs(letters_colors)
        letters = typed_expressions['letters']
        colors = typed_expressions['colors']
        x, y = mouse_clock.calculate_mouse_position(letters, colors)
        mouse_clock.move_mouse(x, y)

    def mouse_clock_move_and_activate(letters_colors: List[str]):
        """Move mouse to position (with clock off), then activate clock at new position."""
        mouse_clock = get_mouse_clock_instance()
        typed_expressions = parse_voice_inputs(letters_colors)
        letters = typed_expressions['letters']
        colors = typed_expressions['colors']

        # Validate: Must have at least one letter (direction)
        if not letters:
            log_warning("[mouse_clock] Ignoring command - no direction specified (letters required)")
            return

        # Get current mouse position FIRST before calculating
        mouse_clock.get_mouse_position()

        # Calculate position with clock off
        log_info(f"[move_and_activate] Before calc - center: ({mouse_clock.core.center_x}, {mouse_clock.core.center_y})")
        x, y = mouse_clock.calculate_mouse_position(letters, colors)
        log_info(f"[move_and_activate] Calculated new position: ({x}, {y})")

        # Move mouse to new position FIRST
        mouse_clock.move_mouse(x, y)
        log_info(f"[move_and_activate] Mouse moved to: ({x}, {y})")

        # Update the core center to the position we just moved to
        # (Don't rely on reading it back due to timing issues)
        mouse_clock.core.update_center(x, y)
        log_info(f"[move_and_activate] Updated center to: ({x}, {y})")

        # Now setup the clock at the new position (don't update position again)
        mouse_clock.setup(update_position=False)
        log_info(f"[move_and_activate] After setup - center: ({mouse_clock.core.center_x}, {mouse_clock.core.center_y})")
        mouse_clock.show()
        mouse_clock.clear_state()
        ctx.tags = ["user.mouse_clock_showing"]

        # Store as original command for potential reversal
        mouse_clock.core.original_command = (letters, colors)

    def mouse_clock_debug_position():
        """Print current mouse position and debug info to log file."""
        mouse_clock = get_mouse_clock_instance()
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
        from talon import actions
        log_file = get_current_log_file()
        if log_file:
            log_info(f"Current log file: {log_file}")
            actions.user.boolean_print("Mouse Clock", f"Logging to: {log_file}")
        else:
            actions.user.boolean_print("Mouse Clock", "No log file currently active")

    def mouse_clock_log_position():
        """Log the current mouse position immediately."""
        from talon import actions
        current_x, current_y = ctrl.mouse_pos()
        log_separator()
        log_info(f"[POSITION CHECK] Current mouse position: ({current_x}, {current_y})")
        log_separator()
        actions.user.boolean_print("Mouse Clock", f"Logged position: ({current_x}, {current_y})")

    def mouse_clock_log_marker(text: str):
        """Log a custom marker/comment for context."""
        from talon import actions
        log_separator()
        log_info(f"[MARKER] {text}")
        log_separator()
        actions.user.boolean_print("Mouse Clock", f"Marker logged: {text}")
