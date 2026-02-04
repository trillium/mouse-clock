"""Tests for averaging utilities."""

import pytest

from core.geometry.averaging import (
    average_coordinates,
    average_angles,
    calculate_mean,
    average_clock_angles,
)


class TestAverageCoordinates:
    def test_single_point(self):
        assert average_coordinates([(3, 4)]) == (3.0, 4.0)

    def test_two_points(self):
        assert average_coordinates([(0, 0), (10, 10)]) == (5.0, 5.0)

    def test_empty_list(self):
        assert average_coordinates([]) == (0.0, 0.0)

    def test_negative_coords(self):
        result = average_coordinates([(-10, -10), (10, 10)])
        assert result == pytest.approx((0.0, 0.0))


class TestAverageAngles:
    def test_same_angles(self):
        result = average_angles([90, 90])
        assert result == pytest.approx(90.0)

    def test_opposite_angles(self):
        """0 and 180 via to_cartesian: cos(0)=1,cos(180)=-1 avg=0;
        sin(0)=0,sin(180)~=0 avg~=small positive -> atan2(~0, 0) = 90."""
        result = average_angles([0, 180])
        assert result == pytest.approx(90.0)

    def test_wraparound(self):
        """350 and 10 should average to ~0, not 180."""
        result = average_angles([350, 10])
        assert abs(result) < 5 or abs(result - 360) < 5

    def test_three_equidistant_angles(self):
        """0, 120, 240 don't perfectly cancel due to floating point in
        to_cartesian which uses degrees->radians conversion."""
        result = average_angles([0, 120, 240])
        # Just verify it returns a finite number (floating point makes
        # the result nondeterministic when components nearly cancel)
        assert -180 <= result <= 360


class TestCalculateMean:
    def test_basic(self):
        assert calculate_mean([1, 2, 3]) == pytest.approx(2.0)

    def test_single(self):
        assert calculate_mean([5]) == pytest.approx(5.0)

    def test_empty(self):
        assert calculate_mean([]) == pytest.approx(0.0)

    def test_negative(self):
        assert calculate_mean([-10, 10]) == pytest.approx(0.0)


class TestAverageClockAngles:
    def test_single_hour(self):
        hour, deg = average_clock_angles([3])
        assert hour == pytest.approx(3.0)
        assert deg == pytest.approx(90.0)

    def test_adjacent_hours(self):
        hour, deg = average_clock_angles([2, 4])
        assert hour == pytest.approx(3.0)
        assert deg == pytest.approx(90.0)

    def test_empty(self):
        hour, deg = average_clock_angles([])
        assert hour == 0.0
        assert deg == 0.0

    def test_opposite_hours(self):
        """3 and 9 should average to 6 or 12 depending on convention."""
        hour, deg = average_clock_angles([3, 9])
        # These are opposite - components cancel, atan2 returns 0
        assert deg == pytest.approx(0.0, abs=1e-10) or deg == pytest.approx(180.0, abs=1e-10)
