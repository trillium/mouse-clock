"""Clock settings overlay — voice actions and tag management.

Provides actions to show/hide/adjust the clock settings panel
and manages the clock_settings_active tag for command gating.
"""

from talon import Context, Module

from . import settings_overlay

mod = Module()
mod.tag("clock_settings_active", desc="Clock settings overlay is showing")

ctx = Context()


def _update_tag():
    """Sync the clock_settings_active tag with overlay visibility."""
    if settings_overlay.is_showing():
        ctx.tags = ["user.clock_settings_active"]
    else:
        ctx.tags = []


settings_overlay.set_on_hide(_update_tag)


@mod.action_class
class Actions:
    def clock_settings_show():
        """Show the clock settings overlay"""
        settings_overlay.show()
        _update_tag()

    def clock_settings_hide():
        """Hide the clock settings overlay"""
        settings_overlay.hide()
        _update_tag()

    def clock_settings_increase(n: int):
        """Increase setting at row n"""
        settings_overlay.adjust(n, 1)

    def clock_settings_decrease(n: int):
        """Decrease setting at row n"""
        settings_overlay.adjust(n, -1)

    def clock_settings_reset(n: int):
        """Reset setting at row n to default"""
        settings_overlay.reset(n)

    def clock_settings_refresh():
        """Refresh the clock settings overlay"""
        if settings_overlay.is_showing():
            settings_overlay.hide()
            settings_overlay.show()
            _update_tag()
