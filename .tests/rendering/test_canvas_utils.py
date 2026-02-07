"""Tests for rendering/canvas/utils.py — pure calculation functions."""

import math
import pytest

from src.rendering.canvas.utils import calculate_ring_radius, calculate_clock_position


class TestCalculateRingRadius:
    def test_center_ring_is_zero(self):
        assert calculate_ring_radius(0, 10, 300) == 0

    def test_outer_ring_equals_radius(self):
        # Last ring (index = total-1) should equal outer_radius
        assert calculate_ring_radius(9, 10, 300) == 300

    def test_middle_ring_proportional(self):
        # Ring 5 of 10 with radius 300 → 300 * 5/9
        result = calculate_ring_radius(5, 10, 300)
        assert result == pytest.approx(300 * 5 / 9)

    def test_two_rings(self):
        # Ring 0 = center, Ring 1 = full radius
        assert calculate_ring_radius(0, 2, 200) == 0
        assert calculate_ring_radius(1, 2, 200) == 200


class TestCalculateClockPosition:
    def test_twelve_oclock(self):
        """Letter index 0 should be at 12 o'clock (straight up)."""
        # Actually index is 1-based where 1=A at 12 o'clock
        # Angle = 30 * 1 - 90 = -60 degrees
        # Wait — let me check: for letter_index=0, angle = 30*0-90 = -90 deg
        # cos(-90°) = 0, sin(-90°) = -1
        # So (center_x + 0, center_y - radius) = straight up
        x, y = calculate_clock_position(0, 100, 500, 500)
        assert x == pytest.approx(500, abs=0.1)
        assert y == pytest.approx(400, abs=0.1)  # 500 - 100

    def test_three_oclock(self):
        """3 o'clock = 90 degrees from 12."""
        # letter_index=3: angle = 30*3-90 = 0 degrees → (1, 0)
        x, y = calculate_clock_position(3, 100, 500, 500)
        assert x == pytest.approx(600, abs=0.1)  # 500 + 100
        assert y == pytest.approx(500, abs=0.1)

    def test_six_oclock(self):
        """6 o'clock = 180 degrees from 12."""
        # letter_index=6: angle = 30*6-90 = 90 degrees → (0, 1)
        x, y = calculate_clock_position(6, 100, 500, 500)
        assert x == pytest.approx(500, abs=0.1)
        assert y == pytest.approx(600, abs=0.1)  # 500 + 100

    def test_nine_oclock(self):
        """9 o'clock = 270 degrees from 12."""
        # letter_index=9: angle = 30*9-90 = 180 degrees → (-1, 0)
        x, y = calculate_clock_position(9, 100, 500, 500)
        assert x == pytest.approx(400, abs=0.1)  # 500 - 100
        assert y == pytest.approx(500, abs=0.1)

    def test_zero_radius_at_center(self):
        x, y = calculate_clock_position(3, 0, 100, 200)
        assert x == pytest.approx(100)
        assert y == pytest.approx(200)
