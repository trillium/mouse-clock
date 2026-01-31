"""
Parrot sound integration for MouseClock.

Maps parrot sounds to mouse clock actions with debouncing
to prevent rapid-fire from sustained sounds.
"""

from talon import Module, Context, actions
from ..input.debounce import debounce
from ..input.guards import is_overlay_active, set_overlay_active, set_overlay_inactive

mod = Module()

# Context that requires mouse_clock_showing tag
ctx = Context()
ctx.matches = r"""
tag: user.mouse_clock_showing
"""

# Debounce interval in milliseconds
DEBOUNCE_MS = 150


@debounce(DEBOUNCE_MS)
def _handle_hiss():
    """Handle hiss sound - widen radius."""
    if is_overlay_active("mouse_clock"):
        actions.user.mouse_clock_widen()


@debounce(DEBOUNCE_MS)
def _handle_shush():
    """Handle shush sound - narrow radius."""
    if is_overlay_active("mouse_clock"):
        actions.user.mouse_clock_narrow()


def on_parrot(event: str):
    """
    Parrot event handler.

    Called by Talon's parrot system when a sound is detected.

    Args:
        event: Sound label (e.g., "hiss", "shush", "pop")
    """
    if event == "hiss":
        _handle_hiss()
    elif event == "shush":
        _handle_shush()


# Register with Talon's parrot system
try:
    from talon import noise
    noise.register("noise", on_parrot)
except ImportError:
    # Parrot/noise module not available
    pass


@mod.action_class
class ParrotActions:
    def mouse_clock_parrot_hiss():
        """Handle hiss sound for mouse clock (manual trigger for testing)."""
        _handle_hiss()

    def mouse_clock_parrot_shush():
        """Handle shush sound for mouse clock (manual trigger for testing)."""
        _handle_shush()


def register_overlay_active():
    """Call when mouse clock becomes active."""
    set_overlay_active("mouse_clock")


def register_overlay_inactive():
    """Call when mouse clock is closed."""
    set_overlay_inactive("mouse_clock")
