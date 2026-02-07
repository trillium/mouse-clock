_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Talon integration for Lettered Line Overlay.
"""

from talon import Module, Context, canvas, ctrl, ui
from ..features.line import (
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
_active_lines = set()  # Set of active letter lines (A, B, C, etc.)


def _get_screen_dimensions():
    """Get current screen dimensions."""
    screens = ui.screens()
    if screens:
        rect = screens[0].rect
        return rect.width, rect.height
    return 1920, 1080


def _draw_callback(c):
    """Canvas draw callback."""
    global _current_letter, _show_verticals, _active_lines
    width, height = _get_screen_dimensions()

    if _current_letter and _show_verticals:
        draw_line_with_verticals(c, _current_letter, width, height)
    elif _current_letter:
        draw_single_line(c, _current_letter, width, height)
    elif _active_lines:
        # Draw only active lines
        for letter in _active_lines:
            draw_single_line(c, letter, width, height)
        if _show_verticals:
            draw_all_verticals(c, width, height)
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
    global _canvas, _current_letter, _show_verticals, _active_lines

    if _canvas:
        _canvas.unregister("draw", _draw_callback)
        _canvas.close()
        _canvas = None
        _current_letter = None
        _show_verticals = False
        _active_lines = set()
        set_overlay_inactive("line_overlay")


def add_line(letter: str):
    """Add a specific letter line to active set."""
    global _active_lines, _current_letter, _canvas
    _active_lines.add(letter.upper())
    _current_letter = None  # Clear single-line mode
    if _canvas:
        _canvas.freeze()


def remove_line(letter: str):
    """Remove a specific letter line from active set."""
    global _active_lines, _canvas
    _active_lines.discard(letter.upper())
    if _canvas:
        _canvas.freeze()


def show_verticals():
    """Show vertical lines."""
    global _show_verticals, _canvas
    _show_verticals = True
    if _canvas:
        _canvas.freeze()


def hide_verticals():
    """Hide vertical lines."""
    global _show_verticals, _canvas
    _show_verticals = False
    if _canvas:
        _canvas.freeze()


def clear_all_lines():
    """Clear all lines but keep overlay active."""
    global _active_lines, _current_letter, _show_verticals, _canvas
    _active_lines = set()
    _current_letter = None
    _show_verticals = False
    if _canvas:
        _canvas.freeze()


def move_to_line(letter: str):
    """Move cursor to the Y position of a letter band."""
    width, height = _get_screen_dimensions()
    y = get_y_for_letter(letter, height)

    if y is not None:
        current_x, _ = ctrl.mouse_pos()
        ctrl.mouse_move(current_x, y)


def move_to_intersection(letter: str, color: str):
    """Move cursor to intersection of horizontal letter and vertical color."""
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

    def line_overlay_add_line(letter: str):
        """Add a specific line to the display."""
        add_line(letter)

    def line_overlay_remove_line(letter: str):
        """Remove a specific line from the display."""
        remove_line(letter)

    def line_overlay_verticals_on():
        """Show vertical lines."""
        show_verticals()

    def line_overlay_verticals_off():
        """Hide vertical lines."""
        hide_verticals()

    def line_overlay_clear():
        """Clear all lines."""
        clear_all_lines()
        hide_line()
