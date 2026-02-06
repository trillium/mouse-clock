"""
MouseClockTalonAdapter - Talon-specific wrapper around core mouse clock logic.

Handles canvas management, mouse control, and screen handling.
"""

from typing import List
from talon import canvas, ctrl, ui, cron, actions
from talon.types.point import Point2d

from ..core import config
from ..core.config import get_setting, set_setting, get_mode_config
from ..rendering.colors import get_color
from ..core.mouse_clock import MouseClockCore
from ..core.logger import log_info, log_debug, log_mode_change, log_tags, log_state, initialize_logger
from ..rendering.canvas import draw_mouse_clock
from ..input.guards import set_overlay_active, set_overlay_inactive
from ..features.box import draw_concentric_boxes
from ..features.grid import draw_grid_overlay, update_offset_animation
from ..features.clock_letters import draw_clock_letters_overlay
from ..rendering.animation import FadeAnimator
from ..rendering.drawing import draw_line, draw_dot
from .debug_overlay import draw_debug_info
# NOTE: draw_info_overlay imported lazily in draw() to avoid module load order issues

print("reloaded adapter.py 8 - unified mode system")

# Module-level canvas registry - tracks ALL canvases ever created
# This allows cleanup of stale canvases after hot reload
_all_canvases = []

def _cleanup_all_canvases():
    """Force close all registered canvases. Called on module reload."""
    global _all_canvases
    for c in _all_canvases:
        try:
            c.close()
        except Exception:
            pass
    _all_canvases = []
    print("[DEBUG] Cleaned up all registered canvases")

# Clean up any stale canvases from previous module load
_cleanup_all_canvases()

# Display mode constants
DISPLAY_MODE_CIRCLES = "circles"
DISPLAY_MODE_BOXES = "boxes"
DISPLAY_MODE_GRID = "grid"
DISPLAY_MODE_INFO = "info"
DISPLAY_MODE_CLOCK_LETTERS = "clock_letters"
DISPLAY_MODE_THIS = "this"  # Line targeting mode

# Map modes to their required tags
MODE_TAGS = {
    DISPLAY_MODE_CIRCLES: ["user.mouse_clock_showing"],
    DISPLAY_MODE_BOXES: ["user.mouse_clock_showing"],
    DISPLAY_MODE_GRID: ["user.mouse_clock_showing"],
    DISPLAY_MODE_INFO: ["user.mouse_clock_showing", "user.mouse_clock_info_mode"],
    DISPLAY_MODE_CLOCK_LETTERS: ["user.mouse_clock_showing"],
    DISPLAY_MODE_THIS: ["user.mouse_clock_showing", "user.mouse_clock_this_mode"],
}


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
        self._display_mode = get_setting("display_mode", DISPLAY_MODE_CIRCLES)
        self._alpha = 255  # Current overlay alpha (0-255)
        self._fade_animator = FadeAnimator(
            on_update=self._on_fade_update,
            on_complete=None
        )
        # "this" mode state
        self._this_lines = []  # List of (start, end, color_hex) tuples
        self._this_line_data = None  # Geometry for color switching
        self._previous_mode = None  # Mode to return to after "this"

    def get_display_mode(self) -> str:
        """Get current display mode."""
        return self._display_mode

    def set_mode(self, mode: str, set_tags_fn=None):
        """Set display mode and update tags. Single source of truth for mode changes.

        Args:
            mode: The display mode to set
            set_tags_fn: Function to call to set tags (injected to avoid circular import)
        """
        if mode not in MODE_TAGS:
            log_info(f"Unknown mode: {mode}")
            return

        old_mode = self._display_mode

        # When entering "this" mode, remember previous mode
        if mode == DISPLAY_MODE_THIS and old_mode != DISPLAY_MODE_THIS:
            self._previous_mode = old_mode

        # When leaving "this" mode, clear line state
        if old_mode == DISPLAY_MODE_THIS and mode != DISPLAY_MODE_THIS:
            self._this_lines = []
            self._this_line_data = None

        self._display_mode = mode

        # Only save non-"this" modes to settings (don't persist "this")
        if mode != DISPLAY_MODE_THIS:
            set_setting("display_mode", mode)

        log_mode_change(old_mode, mode)

        # Update tags if function provided
        if set_tags_fn:
            set_tags_fn(MODE_TAGS[mode])
            log_tags(MODE_TAGS[mode])

        # Handle animation state changes
        if self.active:
            if mode in (DISPLAY_MODE_INFO, DISPLAY_MODE_THIS):
                # Stop pulsing for info and this modes
                self._fade_animator._pulsing = False
                self._alpha = 255
            elif old_mode in (DISPLAY_MODE_INFO, DISPLAY_MODE_THIS):
                # Restart pulsing when leaving these modes
                self._fade_animator.alpha = 255
                self._fade_animator.pulse(min_alpha=80, max_alpha=255, fade_out_ms=4000, fade_in_ms=1000, delay_at_min_ms=2000)
            # Refresh display
            for canvas_obj in self.canvases:
                canvas_obj.freeze()

    def set_display_mode(self, mode: str):
        """Set display mode and save to settings. Legacy method - prefer set_mode()."""
        self.set_mode(mode)

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
        global _all_canvases
        for screen in screens:
            canvas_obj = canvas.Canvas.from_screen(screen)
            self.canvases.append(canvas_obj)
            _all_canvases.append(canvas_obj)  # Track in module-level registry
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

    def _on_fade_update(self, alpha: int):
        """Called when fade animation updates alpha."""
        self._alpha = alpha
        # Trigger redraw on all canvases
        for canvas_obj in self.canvases:
            canvas_obj.freeze()

    def _on_fade_out_complete(self):
        """Called when fade out animation completes."""
        # Now actually close the canvases
        for canvas_obj in self.canvases:
            canvas_obj.unregister("draw", self.draw)
            canvas_obj.close()
        self.canvases = []
        self.active_canvas = None
        self.active = False
        set_overlay_inactive("mouse_clock")
        log_debug("Canvases closed")

    def show(self):
        """Show the mouse clock on all canvases with fade in."""
        log_state("show", active=self.active, canvases=len(self.canvases))
        if self.active:
            return
        # Start at full opacity, then pulse down
        self._alpha = 255
        for canvas_obj in self.canvases:
            canvas_obj.register("draw", self.draw)
            canvas_obj.freeze()
        self.active = True
        set_overlay_active("mouse_clock")
        # Start pulsing animation (skip for info mode - static display)
        if self._display_mode != DISPLAY_MODE_INFO:
            # Slow fade out (4s), quick fade in (1s), 2s pause at transparent
            self._fade_animator.alpha = 255
            self._fade_animator.pulse(min_alpha=80, max_alpha=255, fade_out_ms=4000, fade_in_ms=1000, delay_at_min_ms=2000)
        log_info(f"Clock shown, mode={self._display_mode}")

    def close(self):
        """Close the mouse clock instantly."""
        log_state("close", active=self.active, canvases=len(self.canvases))
        # Stop any animations
        self._fade_animator._pulsing = False

        # If we have canvases, close them immediately
        if self.canvases:
            self._on_fade_out_complete()
        else:
            self.active = False
        log_info("Clock closed")

    def set_this_lines(self, lines: list):
        """Set lines to draw for 'this' mode. Each line is (start, end, color_hex)."""
        self._this_lines = lines
        # Trigger redraw
        for canvas_obj in self.canvases:
            canvas_obj.freeze()

    def get_previous_mode(self) -> str:
        """Get the mode to return to after 'this' mode."""
        return self._previous_mode or DISPLAY_MODE_CLOCK_LETTERS

    def draw(self, canvas_obj):
        """Draw callback for Talon canvas. Mode determines what is drawn."""
        # Interpolate radius toward target for smooth animation
        still_animating = self.core.update_radius_animation()

        # Draw based on current mode - single source of truth
        if self._display_mode == DISPLAY_MODE_THIS:
            # Draw "this" lines only
            self._draw_this_lines(canvas_obj)
        elif self._display_mode == DISPLAY_MODE_BOXES:
            draw_concentric_boxes(canvas_obj, (self.core.center_x, self.core.center_y), radius=self.core.radius)
        elif self._display_mode == DISPLAY_MODE_GRID:
            rect = canvas_obj.rect
            screen_rect = (rect.x, rect.y, rect.x + rect.width, rect.y + rect.height)
            lerp = self.core._animator.get_lerp_factor()
            grid_animating = update_offset_animation(lerp)
            still_animating = still_animating or grid_animating
            draw_grid_overlay(canvas_obj, screen_rect, alpha=self._alpha)
        elif self._display_mode == DISPLAY_MODE_INFO:
            from ..features.info.render import draw_info_overlay
            rect = canvas_obj.rect
            screen_rect = (rect.x, rect.y, rect.x + rect.width, rect.y + rect.height)
            draw_info_overlay(canvas_obj, screen_rect)
        elif self._display_mode == DISPLAY_MODE_CLOCK_LETTERS:
            rect = canvas_obj.rect
            screen_rect = (rect.x, rect.y, rect.x + rect.width, rect.y + rect.height)
            draw_clock_letters_overlay(canvas_obj, screen_rect, alpha=self._alpha)
        else:
            # Default: circles
            draw_mouse_clock(
                canvas_obj,
                self.core.center_x,
                self.core.center_y,
                self.core.radius,
                [get_color(c) for c in get_mode_config("circles", "colors")],
                config.COLOR_ACTIVE,
                config.COLOR_TEXT
            )

        # Schedule next frame if animating
        if still_animating and self.active_canvas:
            cron.after("16ms", lambda: self.active_canvas.freeze())

    def _draw_this_lines(self, canvas_obj):
        """Draw the 'this' mode lines."""
        if not self._this_lines:
            return
        # Draw color lines first (thin)
        for start, end, color in self._this_lines[:-1]:
            draw_line(canvas_obj, start, end, color, thickness=1)
        # Draw gray line last (thicker, on top)
        start, end, color = self._this_lines[-1]
        draw_line(canvas_obj, start, end, color, thickness=2)
        draw_dot(canvas_obj, start, 4, "ffffffff")  # White start dot
        draw_dot(canvas_obj, end, 6, "ffffffff")    # White target dot

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
