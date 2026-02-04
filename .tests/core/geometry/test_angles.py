"""Tests for angle conversion utilities."""

import math
import pytest

from core.geometry.angles import (
    to_radians,
    to_cartesian,
    to_angle,
    normalize_angle,
    opposite_angle,
)


class TestToRadians:
    def test_zero(self):
        assert to_radians(0) == 0.0

    def test_90_degrees(self):
        assert to_radians(90) == pytest.approx(math.pi / 2)

    def test_180_degrees(self):
        assert to_radians(180) == pytest.approx(math.pi)

    def test_360_degrees(self):
        assert to_radians(360) == pytest.approx(2 * math.pi)

    def test_negative(self):
        assert to_radians(-90) == pytest.approx(-math.pi / 2)


class TestToCartesian:
    def test_zero_degrees(self):
        x, y = to_cartesian(0)
        assert x == pytest.approx(1.0)
        assert y == pytest.approx(0.0)

    def test_90_degrees(self):
        x, y = to_cartesian(90)
        assert x == pytest.approx(0.0, abs=1e-10)
        assert y == pytest.approx(1.0)

    def test_180_degrees(self):
        x, y = to_cartesian(180)
        assert x == pytest.approx(-1.0)
        assert y == pytest.approx(0.0, abs=1e-10)

    def test_270_degrees(self):
        x, y = to_cartesian(270)
        assert x == pytest.approx(0.0, abs=1e-10)
        assert y == pytest.approx(-1.0)


class TestToAngle:
    def test_right(self):
        assert to_angle(1, 0) == pytest.approx(0.0)

    def test_up(self):
        assert to_angle(0, 1) == pytest.approx(90.0)

    def test_left(self):
        assert to_angle(-1, 0) == pytest.approx(180.0)

    def test_down(self):
        assert to_angle(0, -1) == pytest.approx(-90.0)


class TestNormalizeAngle:
    def test_already_normalized(self):
        assert normalize_angle(90) == 90

    def test_zero(self):
        assert normalize_angle(0) == 0

    def test_360_becomes_zero(self):
        assert normalize_angle(360) == 0

    def test_over_360(self):
        assert normalize_angle(450) == 90

    def test_negative(self):
        assert normalize_angle(-30) == 330

    def test_large_negative(self):
        assert normalize_angle(-390) == 330

    def test_multiple_rotations(self):
        assert normalize_angle(720) == 0


class TestOppositeAngle:
    def test_zero(self):
        assert opposite_angle(0) == 180

    def test_90(self):
        assert opposite_angle(90) == 270

    def test_270(self):
        assert opposite_angle(270) == 90

    def test_350(self):
        assert opposite_angle(350) == 170

    def test_180(self):
        assert opposite_angle(180) == 0
