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
    """Log parrot event with timing, radius, and acceleration info."""
    from .instance import get_mouse_clock_instance
    from ..core.animation import exponential_lerp_factor

    now = time.time() * 1000  # ms

    if sound in _last_exec_times:
        delta = now - _last_exec_times[sound]
        delta_str = f"{delta:6.1f}ms"
    else:
        delta_str = "  first"

    _last_exec_times[sound] = now

    # Get radius and acceleration info
    try:
        mc = get_mouse_clock_instance()
        r = mc.core.radius
        tr = mc.core.target_radius
        if mc.core._animation_start_time:
            elapsed = time.time() - mc.core._animation_start_time
            lerp = exponential_lerp_factor(elapsed)
            inc = mc.core._get_dynamic_increment()
            accel_str = f"t={elapsed:.2f}s inc={inc:.0f} lerp={lerp:.2f}"
        else:
            accel_str = "lerp=--"
        radius_str = f"r={r:.0f}->{tr:.0f} {accel_str}"
    except:
        radius_str = "r=?"

    print(f"🕐 {sound:6} -> {action:8} | Δ {delta_str} | {radius_str}")


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
