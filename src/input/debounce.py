"""
Debounce and rate limiting utilities for input events.

Provides throttling mechanisms to prevent runaway behavior from
rapidly-triggered events like parrot sounds.
"""

import time
from typing import Callable, Dict, Any
from functools import wraps


# Global cooldown state
_cooldowns: Dict[str, float] = {}
_last_call_times: Dict[str, float] = {}


def debounce(min_interval_ms: float):
    """
    Decorator to enforce minimum interval between calls.

    If called again before the interval has passed, the call is ignored.

    Args:
        min_interval_ms: Minimum milliseconds between calls

    Returns:
        Decorator function

    Example:
        @debounce(150)
        def on_sound_detected():
            # Only runs if 150ms has passed since last call
            pass
    """
    min_interval_sec = min_interval_ms / 1000.0

    def decorator(func: Callable) -> Callable:
        last_call = [0.0]  # Use list to allow mutation in closure

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if now - last_call[0] >= min_interval_sec:
                last_call[0] = now
                return func(*args, **kwargs)
            return None

        return wrapper

    return decorator


def throttle(max_rate_per_sec: float):
    """
    Decorator to limit call frequency to max rate per second.

    Args:
        max_rate_per_sec: Maximum calls allowed per second

    Returns:
        Decorator function

    Example:
        @throttle(5)  # Max 5 calls per second
        def on_continuous_sound():
            pass
    """
    min_interval = 1.0 / max_rate_per_sec

    def decorator(func: Callable) -> Callable:
        last_call = [0.0]

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if now - last_call[0] >= min_interval:
                last_call[0] = now
                return func(*args, **kwargs)
            return None

        return wrapper

    return decorator


def set_cooldown(event_type: str, duration_ms: float):
    """
    Set a cooldown for an event type.

    Args:
        event_type: Identifier for the event
        duration_ms: Cooldown duration in milliseconds
    """
    _cooldowns[event_type] = time.time() + (duration_ms / 1000.0)


def is_cooling_down(event_type: str) -> bool:
    """
    Check if an event type is in cooldown period.

    Args:
        event_type: Identifier for the event

    Returns:
        True if still cooling down, False if ready
    """
    if event_type not in _cooldowns:
        return False
    return time.time() < _cooldowns[event_type]


def reset_cooldown(event_type: str):
    """
    Clear cooldown for an event type.

    Args:
        event_type: Identifier for the event
    """
    if event_type in _cooldowns:
        del _cooldowns[event_type]


def reset_all_cooldowns():
    """Clear all cooldowns."""
    _cooldowns.clear()


class RateLimiter:
    """
    Class-based rate limiter for more complex scenarios.

    Useful when you need per-instance rate limiting or want to
    query the limiter state.
    """

    def __init__(self, min_interval_ms: float):
        """
        Initialize rate limiter.

        Args:
            min_interval_ms: Minimum milliseconds between allowed calls
        """
        self.min_interval = min_interval_ms / 1000.0
        self.last_call = 0.0

    def try_acquire(self) -> bool:
        """
        Try to acquire permission to proceed.

        Returns:
            True if allowed, False if rate limited
        """
        now = time.time()
        if now - self.last_call >= self.min_interval:
            self.last_call = now
            return True
        return False

    def time_until_ready(self) -> float:
        """
        Get time in seconds until next call is allowed.

        Returns:
            Seconds until ready (0 if already ready)
        """
        elapsed = time.time() - self.last_call
        remaining = self.min_interval - elapsed
        return max(0.0, remaining)

    def reset(self):
        """Reset the limiter, allowing immediate next call."""
        self.last_call = 0.0
