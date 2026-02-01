"""
Parrot sound event handlers and action execution.

Routes parrot sounds to appropriate overlay actions.
"""

import time
from talon import actions, ctrl

from ..input.guards import is_overlay_active
from .parrot_config import get_sound_config

# Rate limiters per sound
_rate_limiters = {}

# Double-sound detection tracking
_last_sound_times = {}


def _update_animation_timing():
    """Update animation timing on every sound event (before rate limiting)."""
    try:
        from .instance import get_mouse_clock_instance
        from .adapter import DISPLAY_MODE_GRID
        mc = get_mouse_clock_instance()
        gap_detected = mc.core._animator.update_timing()
        mode = mc.get_display_mode()

        # In grid mode, end sessions when gap detected to toggle direction/mode
        if gap_detected:
            print(f"🕐 gap! mode={mode}")
        if gap_detected and mode == DISPLAY_MODE_GRID:
            from ..features.grid import end_hiss_session, end_shush_session, get_hiss_direction
            print(f"🕐 gap detected! toggling direction...")
            end_hiss_session()
            end_shush_session()
            print(f"🕐 next direction: {get_hiss_direction()}")
    except Exception as e:
        print(f"🕐 _update_animation_timing error: {e}")


def _get_limiter(sound: str):
    """Get or create rate limiter for a sound."""
    from ..input.debounce import RateLimiter
    from ..core.config import get_setting

    if sound not in _rate_limiters:
        debounce_ms = get_setting("debounce_interval_ms", 25)
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

    # For continuous sounds (hiss/shush), update animation timing on EVERY event
    # This must happen BEFORE rate limiting so acceleration builds properly
    action = sound_config.get("action")
    if action in ("widen", "narrow"):
        _update_animation_timing()

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
            # Double sound detected - execute double action
            execute_action(double_action)
            _last_sound_times[event] = 0  # Reset to prevent triple
            return

    # Track this sound time for double detection
    if double_action:
        _last_sound_times[event] = current_time

    action = sound_config.get("action")
    amount = sound_config.get("amount")

    if action:
        execute_action(action, amount)


def execute_action(action: str, amount: int = None):
    """Execute action based on active overlay."""
    # Toggle action works regardless of overlay state
    if action == "toggle":
        _execute_toggle_action()
        return

    # Check which overlay is active and execute appropriate action
    if is_overlay_active("spiral_nudge"):
        print(f"🕐 executing {action} for spiral_nudge")
        _execute_spiral_action(action)
    elif is_overlay_active("mouse_clock"):
        _execute_mouse_clock_action(action)
    elif is_overlay_active("box_overlay"):
        print(f"🕐 executing {action} for box_overlay")
        _execute_box_overlay_action(action)
    else:
        print(f"🕐 no overlay active, ignoring {action}")


def _execute_toggle_action():
    """Toggle the primary overlay visibility."""
    if is_overlay_active("mouse_clock"):
        actions.user.mouse_clock_close()
    elif is_overlay_active("box_overlay"):
        actions.user.box_overlay_hide()
    elif is_overlay_active("spiral_nudge"):
        actions.user.spiral_stop()
    else:
        # Default: show mouse clock
        actions.user.mouse_clock_show()


def _execute_mouse_clock_action(action: str):
    """Execute mouse clock specific action."""
    from .instance import get_mouse_clock_instance
    from .adapter import DISPLAY_MODE_GRID

    mc = get_mouse_clock_instance()

    # In grid mode, hiss/shush have toggle behavior
    if mc.get_display_mode() == DISPLAY_MODE_GRID:
        from ..features.grid import grid_hiss, grid_shush, get_hiss_direction, get_shush_mode

        if action == "widen":
            # Hiss shifts columns, toggling direction each time
            direction = get_hiss_direction()
            increment = mc.core._animator.get_dynamic_increment()
            grid_hiss(increment)
            print(f"🕐 grid: shift {direction} inc={increment:.0f}")
            if mc.active_canvas:
                mc.active_canvas.freeze()
        elif action == "narrow":
            # Shush toggles between widen/narrow radius
            mode = get_shush_mode()
            print(f"🕐 grid shush: mode before={mode}")
            shush_action = grid_shush(0)
            print(f"🕐 grid shush: action={shush_action}")
            if shush_action == "widen":
                actions.user.mouse_clock_widen()
            else:
                actions.user.mouse_clock_narrow()
            if mc.active_canvas:
                mc.active_canvas.freeze()
        elif action == "click":
            actions.user.mouse_clock_close()
            ctrl.mouse_click()
        return

    # Normal mode actions
    print(f"🕐 clock: {action}")
    if action == "widen":
        actions.user.mouse_clock_widen()
    elif action == "narrow":
        actions.user.mouse_clock_narrow()
    elif action == "click":
        actions.user.mouse_clock_close()
        ctrl.mouse_click()
    elif action == "recenter":
        actions.user.mouse_clock_recenter()
    elif action == "go_back":
        actions.user.mouse_clock_go_back()


def _execute_spiral_action(action: str):
    """Execute spiral nudge specific action."""
    if action == "widen" or action == "advance":
        actions.user.spiral_nudge()
    elif action == "narrow" or action == "reverse":
        actions.user.spiral_back()
    elif action == "click":
        actions.user.spiral_stop()
        ctrl.mouse_click()
    elif action == "recenter":
        actions.user.spiral_reset()
    elif action == "go_back":
        actions.user.spiral_back()


def _execute_box_overlay_action(action: str):
    """Execute box overlay specific action."""
    if action == "widen":
        pass  # No widen for boxes
    elif action == "narrow":
        pass  # No narrow for boxes
    elif action == "click":
        actions.user.box_overlay_hide()
        ctrl.mouse_click()
    elif action == "recenter":
        actions.user.box_overlay_recenter()
    elif action == "go_back":
        from ..input.history import pop_position
        pos = pop_position()
        if pos:
            ctrl.mouse_move(pos[0], pos[1])
