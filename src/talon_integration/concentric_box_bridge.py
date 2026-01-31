"""
Talon integration for Concentric Box Targeting.
"""

from talon import Module, Context, canvas, ctrl, ui
from ..features.concentric_box import draw_concentric_boxes, get_size_for_color
from ..input.guards import set_overlay_active, set_overlay_inactive

mod = Module()
mod.tag("box_overlay_showing", desc="Tag indicates box overlay is showing")

ctx = Context()

# Global state
_canvas = None
_center = None


def _get_screen():
    """Get current screen."""
    screens = ui.screens()
    return screens[0] if screens else None


def _draw_callback(c):
    """Canvas draw callback."""
    if _center:
        draw_concentric_boxes(c, _center)


def show_boxes():
    """Show concentric box overlay at current cursor position."""
    global _canvas, _center

    _center = ctrl.mouse_pos()

    if _canvas:
        _canvas.freeze()
        return

    screen = _get_screen()
    if screen:
        _canvas = canvas.Canvas.from_screen(screen)
        _canvas.register("draw", _draw_callback)
        _canvas.freeze()
        set_overlay_active("box_overlay")


def hide_boxes():
    """Hide the box overlay."""
    global _canvas, _center

    if _canvas:
        _canvas.unregister("draw", _draw_callback)
        _canvas.close()
        _canvas = None
        _center = None
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
