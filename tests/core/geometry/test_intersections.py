"""Tests for ray intersection calculations."""

import pytest

from core.geometry.intersections import (
    ray_line_intersection,
    ray_circle_intersection,
    ray_rect_intersection,
)


class TestRayLineIntersection:
    def test_ray_right_hits_vertical_line(self):
        """Ray going right (90 clock) should hit a vertical line."""
        hit = ray_line_intersection(
            ray_origin=(0, 0),
            ray_angle_degrees=90,
            line_start=(50, -100),
            line_end=(50, 100),
        )
        assert hit is not None
        assert hit[0] == pytest.approx(50.0)
        assert hit[1] == pytest.approx(0.0, abs=1e-10)

    def test_ray_up_hits_horizontal_line(self):
        """Ray going up (0 clock) should hit a horizontal line above."""
        hit = ray_line_intersection(
            ray_origin=(50, 50),
            ray_angle_degrees=0,
            line_start=(0, 0),
            line_end=(100, 0),
        )
        assert hit is not None
        assert hit[0] == pytest.approx(50.0, abs=1e-10)
        assert hit[1] == pytest.approx(0.0, abs=1e-10)

    def test_parallel_no_hit(self):
        """Parallel ray and line should return None."""
        hit = ray_line_intersection(
            ray_origin=(0, 0),
            ray_angle_degrees=90,
            line_start=(0, 10),
            line_end=(100, 10),
        )
        assert hit is None

    def test_ray_wrong_direction(self):
        """Ray pointing away from line should not hit it."""
        hit = ray_line_intersection(
            ray_origin=(0, 0),
            ray_angle_degrees=270,  # left
            line_start=(50, -100),
            line_end=(50, 100),
        )
        assert hit is None


class TestRayCircleIntersection:
    def test_ray_hits_circle(self):
        """Ray from origin toward a circle should find intersection."""
        hit = ray_circle_intersection(
            origin=(0, 0),
            angle_degrees=90,  # right
            center=(100, 0),
            radius=20,
        )
        assert hit is not None
        assert hit[0] == pytest.approx(80.0)
        assert hit[1] == pytest.approx(0.0, abs=1e-10)

    def test_ray_misses_circle(self):
        """Ray pointing away from circle should miss."""
        hit = ray_circle_intersection(
            origin=(0, 0),
            angle_degrees=270,  # left
            center=(100, 0),
            radius=20,
        )
        assert hit is None

    def test_ray_from_inside_circle(self):
        """Ray from inside circle should hit the far side."""
        hit = ray_circle_intersection(
            origin=(100, 0),
            angle_degrees=90,
            center=(100, 0),
            radius=50,
        )
        assert hit is not None
        assert hit[0] == pytest.approx(150.0)


class TestRayRectIntersection:
    def test_ray_hits_right_edge(self):
        """Ray going right should hit right edge of rect."""
        hit = ray_rect_intersection(
            origin=(50, 50),
            angle_degrees=90,
            rect=(0, 0, 100, 100),
        )
        assert hit is not None
        assert hit[0] == pytest.approx(100.0)
        assert hit[1] == pytest.approx(50.0, abs=1e-10)

    def test_ray_hits_top_edge(self):
        """Ray going up should hit top edge of rect."""
        hit = ray_rect_intersection(
            origin=(50, 50),
            angle_degrees=0,
            rect=(0, 0, 100, 100),
        )
        assert hit is not None
        assert hit[0] == pytest.approx(50.0, abs=1e-10)
        assert hit[1] == pytest.approx(0.0)

    def test_ray_outside_rect_no_hit(self):
        """Ray originating outside and pointing away should not hit."""
        hit = ray_rect_intersection(
            origin=(200, 200),
            angle_degrees=90,  # right, away from rect
            rect=(0, 0, 100, 100),
        )
        assert hit is None
