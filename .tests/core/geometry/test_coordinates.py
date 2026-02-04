"""Tests for coordinate calculation utilities."""

import math
import pytest

from core.geometry.coordinates import (
    move_in_direction,
    distance_between,
    point_on_circle,
    clamp_to_bounds,
)


class TestMoveInDirection:
    def test_move_up(self):
        """0 degrees in clock = straight up (negative y in screen coords)."""
        x, y = move_in_direction(0, 100, (0, 0))
        assert x == pytest.approx(0.0, abs=1e-10)
        assert y == pytest.approx(-100.0)

    def test_move_right(self):
        """90 degrees in clock = right (positive x)."""
        x, y = move_in_direction(90, 50, (0, 0))
        assert x == pytest.approx(50.0)
        assert y == pytest.approx(0.0, abs=1e-10)

    def test_move_down(self):
        """180 degrees in clock = down (positive y in screen coords)."""
        x, y = move_in_direction(180, 100, (0, 0))
        assert x == pytest.approx(0.0, abs=1e-10)
        assert y == pytest.approx(100.0)

    def test_with_origin(self):
        x, y = move_in_direction(90, 50, (10, 10))
        assert x == pytest.approx(60.0)
        assert y == pytest.approx(10.0, abs=1e-10)

    def test_zero_distance(self):
        x, y = move_in_direction(45, 0, (100, 200))
        assert x == pytest.approx(100.0)
        assert y == pytest.approx(200.0)


class TestDistanceBetween:
    def test_3_4_5_triangle(self):
        assert distance_between((0, 0), (3, 4)) == pytest.approx(5.0)

    def test_same_point(self):
        assert distance_between((1, 1), (1, 1)) == pytest.approx(0.0)

    def test_horizontal(self):
        assert distance_between((0, 0), (10, 0)) == pytest.approx(10.0)

    def test_vertical(self):
        assert distance_between((0, 0), (0, 7)) == pytest.approx(7.0)

    def test_negative_coords(self):
        assert distance_between((-3, -4), (0, 0)) == pytest.approx(5.0)


class TestPointOnCircle:
    def test_top(self):
        """0 degrees clock = top of circle."""
        x, y = point_on_circle((100, 100), 50, 0)
        assert x == pytest.approx(100.0, abs=1e-10)
        assert y == pytest.approx(50.0)

    def test_right(self):
        """90 degrees clock = right of circle."""
        x, y = point_on_circle((100, 100), 50, 90)
        assert x == pytest.approx(150.0)
        assert y == pytest.approx(100.0, abs=1e-10)

    def test_bottom(self):
        """180 degrees clock = bottom of circle."""
        x, y = point_on_circle((100, 100), 50, 180)
        assert x == pytest.approx(100.0, abs=1e-10)
        assert y == pytest.approx(150.0)

    def test_left(self):
        """270 degrees clock = left of circle."""
        x, y = point_on_circle((100, 100), 50, 270)
        assert x == pytest.approx(50.0)
        assert y == pytest.approx(100.0, abs=1e-10)


class TestClampToBounds:
    def test_inside_bounds(self):
        assert clamp_to_bounds((50, 50), (0, 0, 100, 100)) == (50, 50)

    def test_clamp_x_high(self):
        assert clamp_to_bounds((150, 50), (0, 0, 100, 100)) == (100, 50)

    def test_clamp_x_low(self):
        assert clamp_to_bounds((-10, 50), (0, 0, 100, 100)) == (0, 50)

    def test_clamp_y_high(self):
        assert clamp_to_bounds((50, 200), (0, 0, 100, 100)) == (50, 100)

    def test_clamp_y_low(self):
        assert clamp_to_bounds((50, -5), (0, 0, 100, 100)) == (50, 0)

    def test_on_boundary(self):
        assert clamp_to_bounds((100, 100), (0, 0, 100, 100)) == (100, 100)

    def test_nonzero_origin(self):
        assert clamp_to_bounds((5, 5), (10, 10, 100, 100)) == (10, 10)
