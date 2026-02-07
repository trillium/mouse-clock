_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Draw dispatch for MouseClockTalonAdapter.

Routes canvas draw calls to the correct mode renderer.
No Talon registrations — pure utility.
"""

from talon import cron

from ..core import config
from ..core.config import get_mode_config
from ..rendering.colors import get_color
from ..rendering.canvas import draw_mouse_clock
from ..features.grid import draw_grid_overlay, update_offset_animation
from ..features.clock_letters import draw_clock_letters_overlay

# Display mode constants (inlined for clarity)
DISPLAY_MODE_CIRCLES = "circles"
DISPLAY_MODE_GRID = "grid"
DISPLAY_MODE_CLOCK_LETTERS = "clock_letters"


def draw_dispatch(adapter, canvas_obj):
    """Draw callback dispatcher. Mode determines what is drawn.

    Args:
        adapter: MouseClockTalonAdapter instance
        canvas_obj: Talon canvas object being drawn
    """
    # Interpolate radius toward target for smooth animation
    still_animating = adapter.core.update_radius_animation()

    # Draw based on current mode - single source of truth
    if adapter._display_mode == DISPLAY_MODE_GRID:
        rect = canvas_obj.rect
        screen_rect = (rect.x, rect.y, rect.x + rect.width, rect.y + rect.height)
        lerp = adapter.core._animator.get_lerp_factor()
        grid_animating = update_offset_animation(lerp)
        still_animating = still_animating or grid_animating
        draw_grid_overlay(canvas_obj, screen_rect, alpha=adapter._alpha)
    elif adapter._display_mode == DISPLAY_MODE_CLOCK_LETTERS:
        rect = canvas_obj.rect
        screen_rect = (rect.x, rect.y, rect.x + rect.width, rect.y + rect.height)
        draw_clock_letters_overlay(canvas_obj, screen_rect, alpha=adapter._alpha)
    else:
        # Default: circles
        draw_mouse_clock(
            canvas_obj,
            adapter.core.center_x,
            adapter.core.center_y,
            adapter.core.radius,
            [get_color(c) for c in get_mode_config("circles", "colors")],
            config.COLOR_ACTIVE,
            config.COLOR_TEXT
        )

    # Schedule next frame if animating
    if still_animating and adapter.active_canvas:
        cron.after("16ms", lambda: adapter.active_canvas.freeze())
