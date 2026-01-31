"""
Parrot sound integration for MouseClock.

Maps parrot sounds to mouse clock actions with debouncing
and configurable mappings.
"""

from talon import Module, Context, actions
from ..input.debounce import RateLimiter
from ..input.guards import is_overlay_active, set_overlay_active, set_overlay_inactive
from ..core.config import get_setting, set_setting

mod = Module()

# Context that requires mouse_clock_showing tag
ctx = Context()
ctx.matches = r"""
tag: user.mouse_clock_showing
"""

# Default sound configuration
DEFAULT_SOUND_CONFIG = {
    "hiss": {
        "action": "widen",
        "amount": 20,  # radius increment
        "enabled": True,
    },
    "shush": {
        "action": "narrow",
        "amount": 20,
        "enabled": True,
    },
    "pop": {
        "action": "click",
        "enabled": False,  # Disabled by default
    },
}

# Rate limiters per sound (150ms debounce)
_rate_limiters = {}


def _get_limiter(sound: str) -> RateLimiter:
    """Get or create rate limiter for a sound."""
    if sound not in _rate_limiters:
        debounce_ms = get_setting("debounce_interval_ms", 150)
        _rate_limiters[sound] = RateLimiter(debounce_ms)
    return _rate_limiters[sound]


def get_sound_config() -> dict:
    """Get current sound configuration."""
    return get_setting("parrot_sounds", DEFAULT_SOUND_CONFIG)


def set_sound_config(config: dict):
    """Set sound configuration."""
    set_setting("parrot_sounds", config)


def get_sound_param(sound: str, param: str, default=None):
    """Get a parameter for a specific sound."""
    config = get_sound_config()
    if sound in config:
        return config[sound].get(param, default)
    return default


def set_sound_param(sound: str, param: str, value):
    """Set a parameter for a specific sound."""
    config = get_sound_config()
    if sound not in config:
        config[sound] = {}
    config[sound][param] = value
    set_sound_config(config)


def _execute_action(action: str, amount: int = None):
    """Execute action based on active overlay."""
    # Check which overlay is active and execute appropriate action
    if is_overlay_active("spiral_nudge"):
        _execute_spiral_action(action)
    elif is_overlay_active("mouse_clock"):
        _execute_mouse_clock_action(action)


def _execute_mouse_clock_action(action: str):
    """Execute mouse clock specific action."""
    if action == "widen":
        actions.user.mouse_clock_widen()
    elif action == "narrow":
        actions.user.mouse_clock_narrow()
    elif action == "click":
        actions.user.mouse_clock_close()
        from talon import ctrl
        ctrl.mouse_click()


def _execute_spiral_action(action: str):
    """Execute spiral nudge specific action."""
    if action == "widen" or action == "advance":
        actions.user.spiral_nudge()
    elif action == "narrow" or action == "reverse":
        actions.user.spiral_back()
    elif action == "click":
        actions.user.spiral_stop()
        from talon import ctrl
        ctrl.mouse_click()


def on_parrot(event: str):
    """
    Parrot event handler.

    Called by Talon's parrot system when a sound is detected.
    """
    config = get_sound_config()

    if event not in config:
        return

    sound_config = config[event]

    if not sound_config.get("enabled", True):
        return

    # Check rate limiter
    limiter = _get_limiter(event)
    if not limiter.try_acquire():
        return

    action = sound_config.get("action")
    amount = sound_config.get("amount")

    if action:
        _execute_action(action, amount)


# Register with Talon's parrot system
try:
    from talon import noise
    noise.register("noise", on_parrot)
except ImportError:
    # Parrot/noise module not available
    pass


def reset_sound_config():
    """Reset sound configuration to defaults."""
    set_sound_config(DEFAULT_SOUND_CONFIG.copy())
    _rate_limiters.clear()


def reload_sound_config():
    """Reload sound configuration (clears rate limiters)."""
    _rate_limiters.clear()


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

    def mouse_clock_parrot_reload():
        """Reload parrot sound configuration."""
        reload_sound_config()

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
