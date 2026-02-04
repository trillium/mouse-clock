"""Tests for animation and timing utilities."""

import time
import pytest

from core.animation import exponential_lerp_factor, RadiusAnimator


class TestExponentialLerpFactor:
    def test_at_zero(self):
        """At t=0, should return the base value."""
        result = exponential_lerp_factor(0.0)
        assert result == pytest.approx(0.08)

    def test_at_ramp_time(self):
        """At full ramp time, should return max_factor."""
        result = exponential_lerp_factor(1.5)
        assert result == pytest.approx(0.98)

    def test_beyond_ramp_time(self):
        """Beyond ramp time, should still be max_factor (clamped)."""
        result = exponential_lerp_factor(10.0)
        assert result == pytest.approx(0.98)

    def test_monotonically_increasing(self):
        """Factor should always increase over time."""
        prev = 0.0
        for t in [0.0, 0.1, 0.3, 0.5, 0.8, 1.0, 1.5]:
            val = exponential_lerp_factor(t)
            assert val >= prev
            prev = val

    def test_custom_params(self):
        result = exponential_lerp_factor(0.0, base=0.1, max_factor=0.9)
        assert result == pytest.approx(0.1)


class TestRadiusAnimator:
    def test_initial_increment(self):
        """Before any timing, should return base increment."""
        animator = RadiusAnimator()
        assert animator.get_dynamic_increment() == RadiusAnimator.BASE_INCREMENT

    def test_initial_elapsed(self):
        animator = RadiusAnimator()
        assert animator.get_elapsed() == 0.0

    def test_update_timing_first_call_returns_gap(self):
        animator = RadiusAnimator()
        assert animator.update_timing() is True  # first call = gap detected

    def test_update_timing_rapid_calls_no_gap(self):
        animator = RadiusAnimator()
        animator.update_timing()
        # Immediate second call should NOT detect a gap
        assert animator.update_timing() is False

    def test_clamp_radius_min(self):
        animator = RadiusAnimator()
        assert animator.clamp_radius(5) == RadiusAnimator.MIN_RADIUS

    def test_clamp_radius_normal(self):
        animator = RadiusAnimator()
        assert animator.clamp_radius(200) == 200

    def test_clamp_radius_no_max_by_default(self):
        """MAX_RADIUS is None by default, so no upper clamp."""
        animator = RadiusAnimator()
        assert animator.clamp_radius(99999) == 99999

    def test_reset(self):
        animator = RadiusAnimator()
        animator.update_timing()
        animator.reset()
        assert animator.get_elapsed() == 0.0
        assert animator._animation_start_time is None
        assert animator._last_input_time is None

    def test_lerp_factor_with_cap(self):
        animator = RadiusAnimator()
        lerp = animator.get_lerp_factor()
        assert lerp <= RadiusAnimator.MAX_LERP_FACTOR

    def test_increment_respects_cap(self):
        """Even at max acceleration, increment should be capped."""
        animator = RadiusAnimator()
        animator.update_timing()
        # Fake elapsed time by setting start time far in the past
        animator._animation_start_time = time.time() - 100
        increment = animator.get_dynamic_increment()
        assert increment <= RadiusAnimator.MAX_INCREMENT_PER_EVENT
