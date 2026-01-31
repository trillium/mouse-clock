"""
Talon integration for Lettered Line Overlay.
"""

from talon import Module, Context, canvas, ui
from ..features.line_overlay import (
    draw_single_line, draw_all_lines, get_y_for_letter
)
from ..input.guards import set_overlay_active, set_overlay_inactive

mod = Module()
mod.tag("line_overlay_showing", desc="Tag indicates line overlay is showing")

ctx = Context()

# Global state
_canvas = None
_current_letter = None


def _get_screen_dimensions():
    """Get current screen dimensions."""
    screens = ui.screens()
    if screens:
        rect = screens[0].rect
        return rect.width, rect.height
    return 1920, 1080


def _draw_callback(c):
    """Canvas draw callback."""
    global _current_letter
    width, height = _get_screen_dimensions()

    if _current_letter:
        draw_single_line(c, _current_letter, width, height)
    else:
        draw_all_lines(c, width, height)


def show_line(letter: str = None):
    """
    Show line overlay for a specific letter.

    Args:
        letter: Band letter (A-E). If None, shows all lines.
    """
    global _canvas, _current_letter

    _current_letter = letter.upper() if letter else None

    if _canvas:
        _canvas.freeze()
        return

    screens = ui.screens()
    if screens:
        _canvas = canvas.Canvas.from_screen(screens[0])
        _canvas.register("draw", _draw_callback)
        _canvas.freeze()
        set_overlay_active("line_overlay")


def hide_line():
    """Hide the line overlay."""
    global _canvas, _current_letter

    if _canvas:
        _canvas.unregister("draw", _draw_callback)
        _canvas.close()
        _canvas = None
        _current_letter = None
        set_overlay_inactive("line_overlay")


def move_to_line(letter: str):
    """Move cursor to the Y position of a letter band."""
    from talon import ctrl

    width, height = _get_screen_dimensions()
    y = get_y_for_letter(letter, height)

    if y is not None:
        current_x, _ = ctrl.mouse_pos()
        ctrl.mouse_move(current_x, y)


@mod.action_class
class LineOverlayActions:
    def line_overlay_show(letter: str = None):
        """Show line overlay, optionally for specific letter."""
        show_line(letter)

    def line_overlay_hide():
        """Hide line overlay."""
        hide_line()

    def line_overlay_move(letter: str):
        """Move cursor to line position and hide overlay."""
        move_to_line(letter)
        hide_line()

    def line_overlay_show_all():
        """Show all horizontal lines."""
        show_line(None)
