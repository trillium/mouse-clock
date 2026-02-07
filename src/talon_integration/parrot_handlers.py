"""
Parrot sound event handlers and action execution.

Routes discrete parrot sounds (pop, cluck, tut) to overlay actions.
"""

import time
from talon import actions, ctrl

from ..input.guards import is_overlay_active
from .parrot_config import get_sound_config

# Rate limiters per sound
_rate_limiters = {}

# Double-sound detection tracking
_last_sound_times = {}


def _get_limiter(sound: str):
    """Get or create rate limiter for a sound."""
    from ..input.debounce import RateLimiter
    from ..core.config import get_setting

    if sound not in _rate_limiters:
        debounce_ms = get_setting("debounce_interval_ms", 150)
        _rate_limiters[sound] = RateLimiter(debounce_ms)
    return _rate_limiters[sound]


def clear_rate_limiters():
    """Clear all rate limiters (call after config reload)."""
    _rate_limiters.clear()


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

    # Check for double-sound detection
    current_time = time.time() * 1000  # ms
    double_action = sound_config.get("double_action")
    double_window = sound_config.get("double_window_ms", 400)

    if double_action and event in _last_sound_times:
        elapsed = current_time - _last_sound_times[event]
        if elapsed < double_window:
            execute_action(double_action)
            _last_sound_times[event] = 0  # Reset to prevent triple
            return

    # Track this sound time for double detection
    if double_action:
        _last_sound_times[event] = current_time

    action = sound_config.get("action")
    if action:
        execute_action(action)


def execute_action(action: str):
    """Execute action based on active overlay."""
    if action == "toggle":
        _execute_toggle_action()
        return

    if is_overlay_active("spiral_nudge"):
        _execute_spiral_action(action)
    elif is_overlay_active("mouse_clock"):
        _execute_mouse_clock_action(action)


def _execute_toggle_action():
    """Toggle the primary overlay visibility."""
    if is_overlay_active("mouse_clock"):
        actions.user.mouse_clock_close()
    elif is_overlay_active("spiral_nudge"):
        actions.user.spiral_stop()
    else:
        actions.user.mouse_clock_show()


def _execute_mouse_clock_action(action: str):
    """Execute mouse clock specific action."""
    if action == "click":
        actions.user.mouse_clock_close()
        ctrl.mouse_click()
    elif action == "recenter":
        actions.user.mouse_clock_recenter()
    elif action == "go_back":
        actions.user.mouse_clock_go_back()


def _execute_spiral_action(action: str):
    """Execute spiral nudge specific action."""
    if action == "click":
        actions.user.spiral_stop()
        ctrl.mouse_click()
    elif action == "recenter":
        actions.user.spiral_reset()
    elif action == "go_back":
        actions.user.spiral_back()
