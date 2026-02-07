"""
Parrot sound integration for MouseClock.

Talon action overrides for discrete parrot sounds (pop, cluck).

NOTE: Imports from .parrot_config, .parrot_handlers, and ..input.guards are
deferred to function bodies to prevent Talon cold-start [ ] cascade.
"""

from talon import Module, Context

mod = Module()

# Context for overriding parrot actions when mouse clock is showing
parrot_ctx = Context()
parrot_ctx.matches = r"""
tag: user.mouse_clock_showing
tag: user.parrot_on
"""


def _on_parrot(sound):
    from .parrot_handlers import on_parrot
    on_parrot(sound)


@parrot_ctx.action_class("user")
class MouseClockParrotOverrides:
    def noise_lip_pop():
        """Pop clicks and closes the clock."""
        _on_parrot("pop")

    def noise_tongue_click():
        """Cluck toggles visibility."""
        _on_parrot("cluck")


@mod.action_class
class ParrotActions:
    def mouse_clock_parrot_reset_config():
        """Reset parrot sound configuration to defaults."""
        from .parrot_config import reset_sound_config
        from .parrot_handlers import clear_rate_limiters
        reset_sound_config()
        clear_rate_limiters()

    def mouse_clock_parrot_set_param(sound: str, param: str, value: str):
        """Set a parrot sound parameter (e.g., 'pop enabled false')."""
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
