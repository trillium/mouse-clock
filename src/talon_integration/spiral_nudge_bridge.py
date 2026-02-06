_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Talon integration for Spiral Nudge Navigation.
"""

from talon import Module, Context, ctrl, canvas, ui
from ..features.spiral_nudge import (
    start_spiral, nudge_forward, nudge_backward,
    reset_spiral, stop_spiral, is_spiral_active,
    get_origin, get_current_position, get_spiral_state
)
from ..input.guards import set_overlay_active, set_overlay_inactive
from ..rendering.drawing import draw_dot, draw_cross, draw_line
from ..core.config import get_setting

mod = Module()
mod.tag("spiral_nudge_active", desc="Tag indicates spiral nudge is active")

ctx = Context()

# Canvas for visual feedback
_canvas = None
_trail_points = []  # List of positions for trail
_show_trail = False


def _get_screen():
    """Get current screen."""
    screens = ui.screens()
    return screens[0] if screens else None


def _draw_callback(c):
    """Canvas draw callback for spiral visual feedback."""
    if not is_spiral_active():
        return

    origin = get_origin()
    current = get_current_position()

    # Draw origin marker (crosshair)
    origin_color = get_setting("spiral_origin_color", "00ff00ff")  # Green
    draw_cross(c, origin, size=8, color=origin_color, thickness=2, style="crosshair")

    # Draw trail if enabled
    if _show_trail and len(_trail_points) > 1:
        trail_color = get_setting("spiral_trail_color", "ffffff40")  # Semi-transparent white
        for i in range(1, len(_trail_points)):
            draw_line(c, _trail_points[i-1], _trail_points[i], trail_color, 1)

    # Draw current position marker
    current_color = get_setting("spiral_current_color", "ff0000ff")  # Red
    draw_dot(c, current, radius=4, color=current_color)


def _show_visual_feedback():
    """Show visual feedback canvas."""
    global _canvas
    if _canvas:
        _canvas.freeze()
        return

    screen = _get_screen()
    if screen:
        _canvas = canvas.Canvas.from_screen(screen)
        _canvas.register("draw", _draw_callback)
        _canvas.freeze()


def _hide_visual_feedback():
    """Hide visual feedback canvas."""
    global _canvas, _trail_points
    if _canvas:
        _canvas.unregister("draw", _draw_callback)
        _canvas.close()
        _canvas = None
    _trail_points = []


def _refresh_canvas():
    """Refresh the canvas."""
    global _canvas
    if _canvas:
        _canvas.freeze()


def _add_trail_point(position):
    """Add a point to the trail."""
    global _trail_points
    if position:
        _trail_points.append(position)


def _move_to(position):
    """Move cursor to position."""
    if position:
        ctrl.mouse_move(position[0], position[1])


@mod.action_class
class SpiralNudgeActions:
    def spiral_start():
        """Start spiral nudge from current cursor position."""
        global _trail_points
        pos = ctrl.mouse_pos()
        start_spiral(pos)
        _trail_points = [pos]  # Initialize trail with origin
        set_overlay_active("spiral_nudge")
        _show_visual_feedback()

    def spiral_nudge():
        """Move to next point on spiral."""
        if not is_spiral_active():
            # Auto-start if not active
            global _trail_points
            pos = ctrl.mouse_pos()
            start_spiral(pos)
            _trail_points = [pos]
            set_overlay_active("spiral_nudge")
            _show_visual_feedback()

        new_pos = nudge_forward()
        _add_trail_point(new_pos)
        _move_to(new_pos)
        _refresh_canvas()

    def spiral_back():
        """Move to previous point on spiral."""
        global _trail_points
        new_pos = nudge_backward()
        if new_pos and _trail_points:
            _trail_points.pop()  # Remove last trail point
        _move_to(new_pos)
        _refresh_canvas()

    def spiral_reset():
        """Reset to spiral origin."""
        global _trail_points
        origin = reset_spiral()
        _trail_points = [origin]  # Reset trail to origin only
        _move_to(origin)
        _refresh_canvas()

    def spiral_stop():
        """Stop spiral navigation."""
        stop_spiral()
        _hide_visual_feedback()
        set_overlay_inactive("spiral_nudge")

    def spiral_toggle_trail():
        """Toggle trail visibility."""
        global _show_trail
        _show_trail = not _show_trail
        _refresh_canvas()

    def spiral_show_visual():
        """Show visual feedback overlay."""
        _show_visual_feedback()

    def spiral_hide_visual():
        """Hide visual feedback overlay."""
        _hide_visual_feedback()
