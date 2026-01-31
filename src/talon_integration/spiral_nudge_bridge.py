"""
Talon integration for Spiral Nudge Navigation.
"""

from talon import Module, Context, ctrl
from ..features.spiral_nudge import (
    start_spiral, nudge_forward, nudge_backward,
    reset_spiral, stop_spiral, is_spiral_active
)
from ..input.guards import set_overlay_active, set_overlay_inactive

mod = Module()
mod.tag("spiral_nudge_active", desc="Tag indicates spiral nudge is active")

ctx = Context()


def _move_to(position):
    """Move cursor to position."""
    if position:
        ctrl.mouse_move(position[0], position[1])


@mod.action_class
class SpiralNudgeActions:
    def spiral_start():
        """Start spiral nudge from current cursor position."""
        pos = ctrl.mouse_pos()
        start_spiral(pos)
        set_overlay_active("spiral_nudge")

    def spiral_nudge():
        """Move to next point on spiral."""
        if not is_spiral_active():
            # Auto-start if not active
            pos = ctrl.mouse_pos()
            start_spiral(pos)
            set_overlay_active("spiral_nudge")

        new_pos = nudge_forward()
        _move_to(new_pos)

    def spiral_back():
        """Move to previous point on spiral."""
        new_pos = nudge_backward()
        _move_to(new_pos)

    def spiral_reset():
        """Reset to spiral origin."""
        origin = reset_spiral()
        _move_to(origin)

    def spiral_stop():
        """Stop spiral navigation."""
        stop_spiral()
        set_overlay_inactive("spiral_nudge")
