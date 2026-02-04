"""Tests for debounce and rate limiting utilities."""

import time
import pytest

from input.debounce import (
    debounce,
    throttle,
    set_cooldown,
    is_cooling_down,
    reset_cooldown,
    reset_all_cooldowns,
    RateLimiter,
)


class TestDebounceDecorator:
    def test_first_call_executes(self):
        call_count = [0]

        @debounce(1000)
        def fn():
            call_count[0] += 1

        fn()
        assert call_count[0] == 1

    def test_rapid_calls_debounced(self):
        call_count = [0]

        @debounce(1000)
        def fn():
            call_count[0] += 1

        fn()
        fn()
        fn()
        assert call_count[0] == 1

    def test_returns_none_when_debounced(self):
        @debounce(1000)
        def fn():
            return 42

        assert fn() == 42
        assert fn() is None


class TestThrottleDecorator:
    def test_first_call_executes(self):
        call_count = [0]

        @throttle(1)  # 1 per second
        def fn():
            call_count[0] += 1

        fn()
        assert call_count[0] == 1

    def test_rapid_calls_throttled(self):
        call_count = [0]

        @throttle(1)  # 1 per second
        def fn():
            call_count[0] += 1

        fn()
        fn()
        fn()
        assert call_count[0] == 1


class TestCooldowns:
    def setup_method(self):
        reset_all_cooldowns()

    def test_not_cooling_down_initially(self):
        assert is_cooling_down("test") is False

    def test_set_cooldown(self):
        set_cooldown("test", 5000)  # 5 second cooldown
        assert is_cooling_down("test") is True

    def test_cooldown_expires(self):
        set_cooldown("test", 1)  # 1ms cooldown
        time.sleep(0.01)
        assert is_cooling_down("test") is False

    def test_reset_cooldown(self):
        set_cooldown("test", 5000)
        reset_cooldown("test")
        assert is_cooling_down("test") is False

    def test_reset_all(self):
        set_cooldown("a", 5000)
        set_cooldown("b", 5000)
        reset_all_cooldowns()
        assert is_cooling_down("a") is False
        assert is_cooling_down("b") is False

    def test_reset_nonexistent(self):
        """Should not raise."""
        reset_cooldown("nonexistent")


class TestRateLimiter:
    def test_first_acquire(self):
        rl = RateLimiter(1000)
        assert rl.try_acquire() is True

    def test_rapid_acquire_blocked(self):
        rl = RateLimiter(1000)
        rl.try_acquire()
        assert rl.try_acquire() is False

    def test_time_until_ready_zero_initially(self):
        rl = RateLimiter(1000)
        assert rl.time_until_ready() == 0.0

    def test_time_until_ready_after_acquire(self):
        rl = RateLimiter(1000)
        rl.try_acquire()
        remaining = rl.time_until_ready()
        assert remaining > 0

    def test_reset(self):
        rl = RateLimiter(1000)
        rl.try_acquire()
        rl.reset()
        assert rl.try_acquire() is True
