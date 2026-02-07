_V = "0.0.2"; print(f"[v{_V}] {__name__}")
"""
Parrot sound integration for MouseClock.

Talon action overrides and action class for parrot sounds.

NOTE: Imports from .parrot_config, .parrot_handlers, and ..input.guards are
deferred to function bodies to prevent Talon cold-start [ ] cascade.
"""

import time
from talon import Module, Context, actions, cron

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

# Cron jobs for keyboard-triggered continuous sounds
_keyboard_hiss_job = None
_keyboard_shush_job = None


def _on_parrot(sound):
    from .parrot_handlers import on_parrot
    on_parrot(sound)


@parrot_ctx.action_class("user")
class MouseClockParrotOverrides:
    def noise_hiss():
        """Hiss widens the clock radius."""
        _log_parrot_event("hiss", "widen")
        _on_parrot("hiss")

    def noise_shh():
        """Shush narrows the clock radius."""
        _log_parrot_event("shush", "narrow")
        _on_parrot("shush")

    def noise_lip_pop():
        """Pop clicks and closes the clock."""
        _log_parrot_event("pop", "click")
        _on_parrot("pop")

    def noise_tongue_click():
        """Cluck toggles visibility."""
        _log_parrot_event("cluck", "toggle")
        _on_parrot("cluck")


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

        print(f"\U0001f550 {timestamp} {sound:6} | lerp:{lerp:.2f} inc:{inc:.0f} dur:{dur:.2f}s last:{last_input}")
    except:
        print(f"\U0001f550 {timestamp} {sound:6} | (no instance)")


@mod.action_class
class ParrotActions:
    def mouse_clock_parrot_hiss():
        """Handle hiss sound for mouse clock (manual trigger for testing)."""
        _on_parrot("hiss")

    def mouse_clock_parrot_shush():
        """Handle shush sound for mouse clock (manual trigger for testing)."""
        _on_parrot("shush")

    def mouse_clock_parrot_reset_config():
        """Reset parrot sound configuration to defaults."""
        from .parrot_config import reset_sound_config
        from .parrot_handlers import clear_rate_limiters
        reset_sound_config()
        clear_rate_limiters()

    def mouse_clock_parrot_reload():
        """Reload parrot sound configuration."""
        from .parrot_config import reload_sound_config
        from .parrot_handlers import clear_rate_limiters
        reload_sound_config()
        clear_rate_limiters()

    def mouse_clock_parrot_set_param(sound: str, param: str, value: str):
        """Set a parrot sound parameter (e.g., 'hiss amount 30')."""
        from .parrot_config import set_sound_param
        # Try to convert to int if numeric
        try:
            value = int(value)
        except ValueError:
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
        set_sound_param(sound, param, value)

    def mouse_clock_keyboard_hiss_start():
        """Start continuous hiss triggered by keyboard."""

        global _keyboard_hiss_job
        if _keyboard_hiss_job is None:
            def hiss_tick():
                actions.user.boolean_print("Hiss (keyboard)", "tick")
                _on_parrot("hiss")
            _keyboard_hiss_job = cron.interval("30ms", hiss_tick)

    def mouse_clock_keyboard_hiss_stop():
        """Stop keyboard-triggered hiss."""
        global _keyboard_hiss_job
        if _keyboard_hiss_job is not None:
            cron.cancel(_keyboard_hiss_job)
            _keyboard_hiss_job = None

    def mouse_clock_keyboard_shush_start():
        """Start continuous shush triggered by keyboard."""

        global _keyboard_shush_job
        if _keyboard_shush_job is None:
            def shush_tick():
                actions.user.boolean_print("Shush (keyboard)", "tick")
                _on_parrot("shush")
            _keyboard_shush_job = cron.interval("30ms", shush_tick)

    def mouse_clock_keyboard_shush_stop():
        """Stop keyboard-triggered shush."""
        global _keyboard_shush_job
        if _keyboard_shush_job is not None:
            cron.cancel(_keyboard_shush_job)
            _keyboard_shush_job = None


def register_overlay_active():
    """Call when mouse clock becomes active."""
    from ..input.guards import set_overlay_active
    set_overlay_active("mouse_clock")


def register_overlay_inactive():
    """Call when mouse clock is closed."""
    from ..input.guards import set_overlay_inactive
    set_overlay_inactive("mouse_clock")
