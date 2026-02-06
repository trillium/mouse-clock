_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Talon integration for Concentric Box Targeting.
"""

from talon import Module, Context, canvas, ctrl, ui
from ..features.box import (
    draw_concentric_boxes, draw_boxes_with_guides, get_size_for_color,
    get_target_position, get_target_from_letter
)
from ..input.guards import set_overlay_active, set_overlay_inactive

mod = Module()
mod.tag("box_overlay_showing", desc="Tag indicates box overlay is showing")

ctx = Context()

# Global state
_canvas = None
_center = None
_show_guides = False


def _get_screen():
    """Get current screen."""
    screens = ui.screens()
    return screens[0] if screens else None


def _draw_callback(c):
    """Canvas draw callback."""
    if _center:
        if _show_guides:
            draw_boxes_with_guides(c, _center)
        else:
            draw_concentric_boxes(c, _center)


def show_boxes(with_guides: bool = False):
    """Show concentric box overlay at current cursor position."""
    global _canvas, _center, _show_guides

    _center = ctrl.mouse_pos()
    _show_guides = with_guides

    if _canvas:
        _canvas.freeze()
        return

    screen = _get_screen()
    if screen:
        _canvas = canvas.Canvas.from_screen(screen)
        _canvas.register("draw", _draw_callback)
        _canvas.freeze()
        set_overlay_active("box_overlay")


def toggle_guides():
    """Toggle directional guides on/off."""
    global _show_guides, _canvas
    _show_guides = not _show_guides
    if _canvas:
        _canvas.freeze()


def hide_boxes():
    """Hide the box overlay."""
    global _canvas, _center, _show_guides

    if _canvas:
        _canvas.unregister("draw", _draw_callback)
        _canvas.close()
        _canvas = None
        _center = None
        _show_guides = False
        set_overlay_inactive("box_overlay")


def recenter_boxes():
    """Recenter boxes at current cursor position."""
    global _center, _canvas
    _center = ctrl.mouse_pos()
    if _canvas:
        _canvas.freeze()


@mod.action_class
class ConcentricBoxActions:
    def box_overlay_show():
        """Show concentric box overlay."""
        show_boxes()

    def box_overlay_show_guided():
        """Show concentric box overlay with directional guides."""
        show_boxes(with_guides=True)

    def box_overlay_toggle_guides():
        """Toggle directional guides on/off."""
        toggle_guides()

    def box_overlay_hide():
        """Hide concentric box overlay."""
        hide_boxes()

    def box_overlay_recenter():
        """Recenter boxes at current cursor position."""
        recenter_boxes()

    def box_overlay_toggle():
        """Toggle box overlay on/off."""
        if _canvas:
            hide_boxes()
        else:
            show_boxes()

    def box_overlay_target(color: str, direction: int):
        """Move cursor to box-direction intersection."""
        global _center
        if _center is None:
            _center = ctrl.mouse_pos()

        pos = get_target_position(_center, color, direction)
        ctrl.mouse_move(pos[0], pos[1])

    def box_overlay_target_letter(color: str, letter: str):
        """Move cursor to box-letter intersection."""
        global _center
        if _center is None:
            _center = ctrl.mouse_pos()

        pos = get_target_from_letter(_center, color, letter)
        ctrl.mouse_move(pos[0], pos[1])
