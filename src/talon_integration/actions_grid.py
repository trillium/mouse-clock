"""
Grid mode targeting actions.

Move mouse to grid intersections based on letter + color + style.
Supports both grid mode and clock_letters mode.
"""

from talon import Module, ctrl
from .instance import get_mouse_clock_instance
from .adapter import DISPLAY_MODE_CLOCK_LETTERS
from ..features.grid.targeting import get_grid_target
from ..features.clock_letters.targeting import get_clock_letters_target

mod = Module()


def _get_target(letter: str, color: str, h_style: str = None, v_style: str = None):
    """Get target position based on current display mode."""
    mouse_clock = get_mouse_clock_instance()
    screen_rect = mouse_clock.get_screen_rect()

    if mouse_clock.get_display_mode() == DISPLAY_MODE_CLOCK_LETTERS:
        # Clock letters mode - no styles
        return get_clock_letters_target(screen_rect, letter, color)
    else:
        # Grid mode - use styles
        return get_grid_target(screen_rect, letter, color, h_style=h_style, v_style=v_style)


@mod.action_class
class GridActions:
    def grid_move_to(letter: str, color: str, style: str):
        """Move mouse to grid intersection (letter + color + style)."""
        x, y = _get_target(letter, color, h_style=style, v_style=style)
        ctrl.mouse_move(x, y)
        print(f"[grid_move_to] {letter} {color} {style} -> ({x:.0f}, {y:.0f})")

    def grid_move_to_full(letter: str, h_style: str, color: str, v_style: str):
        """Move mouse to grid intersection with separate horizontal/vertical styles."""
        x, y = _get_target(letter, color, h_style=h_style, v_style=v_style)
        ctrl.mouse_move(x, y)
        print(f"[grid_move_to_full] {letter} {h_style} {color} {v_style} -> ({x:.0f}, {y:.0f})")

    def grid_move_simple(letter: str, color: str):
        """Move mouse to grid intersection (letter + color, default styles)."""
        x, y = _get_target(letter, color)
        ctrl.mouse_move(x, y)
        print(f"[grid_move_simple] {letter} {color} -> ({x:.0f}, {y:.0f})")
