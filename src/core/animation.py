"""
Animation and timing utilities for smooth radius transitions.

Provides exponential acceleration for hiss/shush radius control.
"""

import time
from typing import Optional


def exponential_lerp_factor(
    elapsed_seconds: float,
    base: float = 0.08,
    max_factor: float = 0.98,
    ramp_time: float = 1.5,
    exponent: float = 4.0
) -> float:
    """
    Calculate an accelerating lerp factor based on elapsed time.

    Starts slow for fine control, accelerates for rapid large movements.

    Args:
        elapsed_seconds: How long the sound has been active
        base: Starting lerp factor (slow, precise)
        max_factor: Maximum lerp factor (fast)
        ramp_time: Seconds to reach max acceleration
        exponent: Curve steepness (2.0 = quadratic, 3.0 = cubic, 4.0 = quartic)

    Returns:
        Lerp factor between base and max_factor
    """
    # Normalize time to 0-1 range over ramp_time
    t = min(elapsed_seconds / ramp_time, 1.0)

    # Apply exponential curve
    curve = t ** exponent

    # Interpolate between base and max
    return base + (max_factor - base) * curve


class RadiusAnimator:
    """
    Manages smooth radius animation with exponential acceleration.

    Tracks timing for continuous sound input (hiss/shush) and provides
    accelerating increment and lerp values.
    """

    # Configuration - can be tuned
    BASE_INCREMENT = 3          # Starting pixels per event
    MAX_MULTIPLIER = 50         # Maximum multiplier (3 * 50 = 150px max)
    RAMP_TIME = 1.5             # Seconds to reach max acceleration
    GAP_THRESHOLD = 0.3         # Seconds of silence before resetting (was 0.15)

    def __init__(self):
        self._animation_start_time: Optional[float] = None
        self._last_input_time: Optional[float] = None

    def update_timing(self):
        """
        Update animation timing on each input event.

        Resets acceleration if there's been a gap in input.
        """
        now = time.time()
        # If gap since last input exceeds threshold, reset acceleration
        if self._last_input_time is None or (now - self._last_input_time) > self.GAP_THRESHOLD:
            self._animation_start_time = now
        self._last_input_time = now

    def get_elapsed(self) -> float:
        """Get elapsed time since animation started."""
        if self._animation_start_time is None:
            return 0.0
        return time.time() - self._animation_start_time

    def get_dynamic_increment(self) -> float:
        """
        Get radius increment that accelerates over time.

        Returns small increment at start for precision,
        large increment after sustained input for speed.
        """
        if self._animation_start_time is None:
            return self.BASE_INCREMENT

        elapsed = self.get_elapsed()
        # Normalize to 0-1 over ramp time
        t = min(elapsed / self.RAMP_TIME, 1.0)
        # Quartic curve (t^4) - stays flat then explodes
        curve = t ** 4
        multiplier = 1 + (self.MAX_MULTIPLIER - 1) * curve
        return self.BASE_INCREMENT * multiplier

    def get_lerp_factor(self) -> float:
        """
        Get lerp factor for interpolating radius toward target.

        Accelerates over time for snappier response during sustained input.
        """
        if self._animation_start_time is None:
            return 0.15  # Fallback base
        return exponential_lerp_factor(self.get_elapsed())

    def reset(self):
        """Reset animation state."""
        self._animation_start_time = None
        self._last_input_time = None
