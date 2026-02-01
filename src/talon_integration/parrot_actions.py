"""
Parrot sound integration for MouseClock.

Talon action overrides and action class for parrot sounds.
"""

import time
from talon import Module, Context

from .parrot_config import (
    set_sound_param,
    reset_sound_config,
    reload_sound_config,
)
from .parrot_handlers import on_parrot, clear_rate_limiters
from ..input.guards import set_overlay_active, set_overlay_inactive

mod = Module()

# Context that requires mouse_clock_showing tag
ctx = Context()
ctx.matches = r"""
tag: user.mouse_clock_showing
"""

# Context for overriding parrot actions when mouse clock is showing
parrot_ctx = Context()
parrot_ctx.matches = r"""
tag: user.mouse_clock_showing
tag: user.parrot_on
"""

# Track last execution time per sound for timing display
_last_exec_times = {}


@parrot_ctx.action_class("user")
class MouseClockParrotOverrides:
    def noise_hiss():
        """Hiss widens the clock radius."""
        _log_parrot_event("hiss", "widen")
        on_parrot("hiss")

    def noise_shh():
        """Shush narrows the clock radius."""
        _log_parrot_event("shush", "narrow")
        on_parrot("shush")

    def noise_lip_pop():
        """Pop clicks and closes the clock."""
        _log_parrot_event("pop", "click")
        on_parrot("pop")

    def noise_tongue_click():
        """Cluck toggles visibility."""
        _log_parrot_event("cluck", "toggle")
        on_parrot("cluck")


def _log_parrot_event(sound: str, action: str):
    """Log parrot event with debug info matching visual display."""
    from .instance import get_mouse_clock_instance
    from datetime import datetime

    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

    try:
        mc = get_mouse_clock_instance()
        animator = mc.core._animator

        lerp = animator.get_lerp_factor()
        inc = animator.get_dynamic_increment()
        dur = animator.get_elapsed()

        if animator._last_input_time:
            last_input = datetime.fromtimestamp(animator._last_input_time).strftime("%H:%M:%S.%f")[:-3]
        else:
            last_input = "--"

        print(f"🕐 {timestamp} {sound:6} | lerp:{lerp:.2f} inc:{inc:.0f} dur:{dur:.2f}s last:{last_input}")
    except:
        print(f"🕐 {timestamp} {sound:6} | (no instance)")


@mod.action_class
class ParrotActions:
    def mouse_clock_parrot_hiss():
        """Handle hiss sound for mouse clock (manual trigger for testing)."""
        on_parrot("hiss")

    def mouse_clock_parrot_shush():
        """Handle shush sound for mouse clock (manual trigger for testing)."""
        on_parrot("shush")

    def mouse_clock_parrot_reset_config():
        """Reset parrot sound configuration to defaults."""
        reset_sound_config()
        clear_rate_limiters()

    def mouse_clock_parrot_reload():
        """Reload parrot sound configuration."""
        reload_sound_config()
        clear_rate_limiters()

    def mouse_clock_parrot_set_param(sound: str, param: str, value: str):
        """Set a parrot sound parameter (e.g., 'hiss amount 30')."""
        # Try to convert to int if numeric
        try:
            value = int(value)
        except ValueError:
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
        set_sound_param(sound, param, value)


def register_overlay_active():
    """Call when mouse clock becomes active."""
    set_overlay_active("mouse_clock")


def register_overlay_inactive():
    """Call when mouse clock is closed."""
    set_overlay_inactive("mouse_clock")
