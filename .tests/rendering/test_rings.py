"""Tests for rendering/canvas/rings.py."""

import pytest
from mocks.canvas import MockCanvas, MockStyle

from src.rendering.canvas.rings import draw_concentric_rings, draw_clock_position_dots


@pytest.fixture
def canvas():
    return MockCanvas()


class TestDrawConcentricRings:
    def test_ring_count_matches_colors(self, canvas):
        colors = ["ff0000ff", "00ff00ff", "0000ffff"]
        draw_concentric_rings(canvas, 500, 500, 300, colors)
        circles = canvas.circles()
        assert len(circles) == 3

    def test_rings_centered(self, canvas):
        colors = ["ff0000ff", "00ff00ff"]
        draw_concentric_rings(canvas, 100, 200, 300, colors)
        for _, x, y, _, _ in canvas.circles():
            assert x == 100
            assert y == 200

    def test_ring_colors_match(self, canvas):
        colors = ["ff0000ff", "00ff00ff", "0000ffff"]
        draw_concentric_rings(canvas, 0, 0, 300, colors)
        circles = canvas.circles()
        for i, (_, _, _, _, paint) in enumerate(circles):
            assert paint["color"] == colors[i]

    def test_first_ring_zero_radius(self, canvas):
        draw_concentric_rings(canvas, 0, 0, 300, ["ff0000ff", "00ff00ff"])
        _, _, _, r, _ = canvas.circles()[0]
        assert r == 0

    def test_last_ring_full_radius(self, canvas):
        draw_concentric_rings(canvas, 0, 0, 300, ["ff0000ff", "00ff00ff"])
        _, _, _, r, _ = canvas.circles()[-1]
        assert r == 300


class TestDrawClockPositionDots:
    def test_total_dots(self, canvas):
        """Each ring draws 12 dots (clock positions)."""
        colors = ["ff0000ff", "00ff00ff", "0000ffff"]
        draw_clock_position_dots(canvas, 500, 500, 300, colors, dot_radius=5)
        circles = canvas.circles()
        # 3 rings * 12 positions = 36 dots
        assert len(circles) == 36

    def test_dots_are_filled(self, canvas):
        draw_clock_position_dots(canvas, 500, 500, 300, ["ff0000ff"], dot_radius=5)
        for _, _, _, _, paint in canvas.circles():
            assert paint["style"] == MockStyle.FILL

    def test_dot_radius(self, canvas):
        draw_clock_position_dots(canvas, 0, 0, 300, ["ff0000ff"], dot_radius=7)
        for _, _, _, r, _ in canvas.circles():
            assert r == 7
