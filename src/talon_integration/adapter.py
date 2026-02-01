"""
MouseClockTalonAdapter - Talon-specific wrapper around core mouse clock logic.

Handles canvas management, mouse control, and screen handling.
"""

from typing import List
from talon import canvas, ctrl, ui, cron, actions
from talon.types.point import Point2d

from ..core import config
from ..core.config import get_setting, set_setting
from ..core.mouse_clock import MouseClockCore
from ..core.logger import log_info, initialize_logger
from ..rendering.canvas import draw_mouse_clock
from ..input.guards import set_overlay_active, set_overlay_inactive

print("reloaded trillium/mouse-clock/src/talon_integration/adapter.py")

# Display mode constants
DISPLAY_MODE_CIRCLES = "circles"
DISPLAY_MODE_BOXES = "boxes"
DISPLAY_MODE_HYBRID = "hybrid"
DISPLAY_MODE_GRID = "grid"


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

    def get_display_mode(self) -> str:
        """Get current display mode."""
        return self._display_mode

    def set_display_mode(self, mode: str):
        """Set display mode and save to settings."""
        if mode in (DISPLAY_MODE_CIRCLES, DISPLAY_MODE_BOXES, DISPLAY_MODE_HYBRID, DISPLAY_MODE_GRID):
            self._display_mode = mode
            set_setting("display_mode", mode)
            log_info(f"Display mode set to: {mode}")
            # Refresh display if active
            if self.active:
                for canvas_obj in self.canvases:
                    canvas_obj.freeze()

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
        set_overlay_active("mouse_clock")

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
        set_overlay_inactive("mouse_clock")

    def draw(self, canvas_obj):
        """Draw callback for Talon canvas."""
        # Interpolate radius toward target for smooth animation
        still_animating = self.core.update_radius_animation()

        # Draw debug info at center
        self._draw_debug_info(canvas_obj)

        if self._display_mode == DISPLAY_MODE_BOXES:
            # Draw concentric boxes only
            from ..features.box import draw_concentric_boxes
            draw_concentric_boxes(canvas_obj, (self.core.center_x, self.core.center_y), radius=self.core.radius)
        elif self._display_mode == DISPLAY_MODE_HYBRID:
            # Draw boxes first (subtle, behind circles)
            from ..features.box import draw_concentric_boxes
            draw_concentric_boxes(canvas_obj, (self.core.center_x, self.core.center_y), thickness=1, radius=self.core.radius)
            # Then draw circles on top
            draw_mouse_clock(
                canvas_obj,
                self.core.center_x,
                self.core.center_y,
                self.core.radius,
                config.COLOR_LIST,
                config.COLOR_ACTIVE,
                config.COLOR_TEXT
            )
        elif self._display_mode == DISPLAY_MODE_GRID:
            # Draw letter/color grid overlay
            from ..features.grid import draw_grid_overlay, update_offset_animation
            screen_rect = self.get_screen_rect()
            # Animate grid offset with same lerp factor
            lerp = self.core._animator.get_lerp_factor()
            grid_animating = update_offset_animation(lerp)
            still_animating = still_animating or grid_animating
            draw_grid_overlay(canvas_obj, screen_rect)
        else:
            # Default: circles only
            draw_mouse_clock(
                canvas_obj,
                self.core.center_x,
                self.core.center_y,
                self.core.radius,
                config.COLOR_LIST,
                config.COLOR_ACTIVE,
                config.COLOR_TEXT
            )

        # If still animating, schedule next frame (~60fps)
        if still_animating and self.active_canvas:
            cron.after("16ms", lambda: self.active_canvas.freeze())

    def _draw_debug_info(self, canvas_obj):
        """Draw debug info (lerp factor, increment, elapsed) at center."""
        import time
        from talon.skia import Paint

        paint = Paint()
        paint.color = "white"
        paint.textsize = 14
        paint.style = paint.Style.FILL

        # Get animation values
        animator = self.core._animator
        elapsed = animator.get_elapsed()
        lerp = animator.get_lerp_factor()
        inc = animator.get_dynamic_increment()

        # Calculate time since last input
        if animator._last_input_time:
            since_input = time.time() - animator._last_input_time
            since_str = f"{since_input:.2f}s"
        else:
            since_str = "--"

        # Format debug text
        lines = [
            f"lerp: {lerp:.2f}",
            f"inc: {inc:.0f}",
            f"dur: {elapsed:.2f}s",
            f"gap: {since_str}",
        ]

        # Draw at center, stacked vertically
        x = self.core.center_x
        y = self.core.center_y - 28  # Start above center

        for line in lines:
            canvas_obj.draw_text(line, x - 30, y, paint)
            y += 16

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
