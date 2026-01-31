"""
Talon integration for Lettered Line Overlay.
"""

from talon import Module, Context, canvas, ui
from ..features.line_overlay import (
    draw_single_line, draw_all_lines, get_y_for_letter,
    draw_line_with_verticals, get_x_for_color, draw_all_verticals
)
from ..input.guards import set_overlay_active, set_overlay_inactive

mod = Module()
mod.tag("line_overlay_showing", desc="Tag indicates line overlay is showing")

ctx = Context()

# Global state
_canvas = None
_current_letter = None
_show_verticals = False


def _get_screen_dimensions():
    """Get current screen dimensions."""
    screens = ui.screens()
    if screens:
        rect = screens[0].rect
        return rect.width, rect.height
    return 1920, 1080


def _draw_callback(c):
    """Canvas draw callback."""
    global _current_letter, _show_verticals
    width, height = _get_screen_dimensions()

    if _current_letter and _show_verticals:
        draw_line_with_verticals(c, _current_letter, width, height)
    elif _current_letter:
        draw_single_line(c, _current_letter, width, height)
    else:
        draw_all_lines(c, width, height)
        if _show_verticals:
            draw_all_verticals(c, width, height)


def show_line(letter: str = None, with_verticals: bool = False):
    """
    Show line overlay for a specific letter.

    Args:
        letter: Band letter (A-E). If None, shows all lines.
        with_verticals: Whether to show vertical intersection lines.
    """
    global _canvas, _current_letter, _show_verticals

    _current_letter = letter.upper() if letter else None
    _show_verticals = with_verticals

    if _canvas:
        _canvas.freeze()
        return

    screens = ui.screens()
    if screens:
        _canvas = canvas.Canvas.from_screen(screens[0])
        _canvas.register("draw", _draw_callback)
        _canvas.freeze()
        set_overlay_active("line_overlay")


def toggle_verticals():
    """Toggle vertical lines on/off."""
    global _show_verticals, _canvas
    _show_verticals = not _show_verticals
    if _canvas:
        _canvas.freeze()


def hide_line():
    """Hide the line overlay."""
    global _canvas, _current_letter, _show_verticals

    if _canvas:
        _canvas.unregister("draw", _draw_callback)
        _canvas.close()
        _canvas = None
        _current_letter = None
        _show_verticals = False
        set_overlay_inactive("line_overlay")


def move_to_line(letter: str):
    """Move cursor to the Y position of a letter band."""
    from talon import ctrl

    width, height = _get_screen_dimensions()
    y = get_y_for_letter(letter, height)

    if y is not None:
        current_x, _ = ctrl.mouse_pos()
        ctrl.mouse_move(current_x, y)


def move_to_intersection(letter: str, color: str):
    """Move cursor to intersection of horizontal letter and vertical color."""
    from talon import ctrl

    width, height = _get_screen_dimensions()
    y = get_y_for_letter(letter, height)
    x = get_x_for_color(color, width)

    if x is not None and y is not None:
        ctrl.mouse_move(x, y)


@mod.action_class
class LineOverlayActions:
    def line_overlay_show(letter: str = None):
        """Show line overlay, optionally for specific letter."""
        show_line(letter)

    def line_overlay_show_with_verticals(letter: str = None):
        """Show line overlay with vertical guides."""
        show_line(letter, with_verticals=True)

    def line_overlay_toggle_verticals():
        """Toggle vertical lines on/off."""
        toggle_verticals()

    def line_overlay_hide():
        """Hide line overlay."""
        hide_line()

    def line_overlay_move(letter: str):
        """Move cursor to line position and hide overlay."""
        move_to_line(letter)
        hide_line()

    def line_overlay_move_intersection(letter: str, color: str):
        """Move cursor to intersection of letter and color."""
        move_to_intersection(letter, color)
        hide_line()

    def line_overlay_show_all():
        """Show all horizontal lines."""
        show_line(None)

    def line_overlay_show_grid():
        """Show full grid (horizontals + verticals)."""
        show_line(None, with_verticals=True)
