_V = "0.0.3"; print(f"[v{_V}] {__name__}")
"""
MouseClockTalonAdapter - Talon-specific wrapper around core mouse clock logic.

Handles mode management, mouse control, show/close, and delegates canvas
setup to adapter_canvas and draw dispatch to adapter_draw.
"""

from typing import List
from talon import ctrl, ui

from ..core import config
from ..core.config import get_setting, set_setting, _auto_save
from ..core.mouse_clock import MouseClockCore
from ..core.logger import log_info, log_debug, log_mode_change, log_tags, log_state, initialize_logger
from ..input.guards import set_overlay_active, set_overlay_inactive
from ..rendering.animation import FadeAnimator

# Display mode constants
DISPLAY_MODE_CIRCLES = "circles"
DISPLAY_MODE_CLOCK_LETTERS = "clock_letters"

# Map modes to their required tags
MODE_TAGS = {
    DISPLAY_MODE_CIRCLES: ["user.mouse_clock_showing"],
    DISPLAY_MODE_CLOCK_LETTERS: ["user.mouse_clock_showing"],
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
        self._display_mode = get_setting("display_mode", DISPLAY_MODE_CLOCK_LETTERS)
        self._alpha = 255  # Current overlay alpha (0-255)
        self._fade_animator = FadeAnimator(
            on_update=self._on_fade_update,
            on_complete=None
        )

    def get_display_mode(self) -> str:
        """Get current display mode."""
        return self._display_mode

    def refresh_canvases(self):
        """Trigger a redraw on all canvases."""
        if self.active:
            for canvas_obj in self.canvases:
                canvas_obj.freeze()

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
        self._display_mode = mode
        set_setting("display_mode", mode)
        _auto_save()

        log_mode_change(old_mode, mode)

        # Update tags if function provided
        if set_tags_fn:
            set_tags_fn(MODE_TAGS[mode])
            log_tags(MODE_TAGS[mode])

        # Refresh display
        self.refresh_canvases()

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
        from .adapter_canvas import setup_canvases
        setup_canvases(self, update_position)

    def _on_fade_update(self, alpha: int):
        """Called when fade animation updates alpha."""
        self._alpha = alpha
        # Trigger redraw on all canvases
        self.refresh_canvases()

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
        # Start pulsing animation
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

    def draw(self, canvas_obj):
        """Draw callback for Talon canvas. Mode determines what is drawn."""
        from .adapter_draw import draw_dispatch
        draw_dispatch(self, canvas_obj)

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

        # Redraw all canvases with the new center
        self.refresh_canvases()
