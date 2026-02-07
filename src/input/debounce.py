_V = "0.0.2"; print(f"[v{_V}] {__name__}")
"""
Rate limiting utilities for input events.

Provides throttling to prevent runaway behavior from
rapidly-triggered events like parrot sounds.
"""

import time


class RateLimiter:
    """
    Class-based rate limiter for per-sound event throttling.

    Used by parrot handlers to debounce discrete sound events.
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
