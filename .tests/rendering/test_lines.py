"""Tests for rendering/drawing/lines.py."""

import pytest
from mocks.canvas import MockCanvas, MockStyle

from src.rendering.drawing.lines import (
    draw_line,
    draw_dotted_line,
    draw_dashed_line,
    SIMPLE_PATTERNS,
    _get_line_geometry,
)


@pytest.fixture
def canvas():
    return MockCanvas()


class TestLineGeometry:
    def test_horizontal_line(self):
        dx, dy, length, perp_x, perp_y = _get_line_geometry((0, 0), (100, 0))
        assert length == pytest.approx(100)
        assert dx == pytest.approx(1.0)
        assert dy == pytest.approx(0.0)

    def test_vertical_line(self):
        dx, dy, length, perp_x, perp_y = _get_line_geometry((0, 0), (0, 50))
        assert length == pytest.approx(50)
        assert dx == pytest.approx(0.0)
        assert dy == pytest.approx(1.0)

    def test_zero_length(self):
        dx, dy, length, _, _ = _get_line_geometry((5, 5), (5, 5))
        assert length == 0

    def test_diagonal(self):
        dx, dy, length, _, _ = _get_line_geometry((0, 0), (3, 4))
        assert length == pytest.approx(5.0)


class TestDrawLine:
    def test_solid_line(self, canvas):
        draw_line(canvas, (0, 0), (100, 0), "ff0000ff")
        lines = canvas.lines()
        assert len(lines) == 1  # single solid segment

    def test_solid_sets_paint(self, canvas):
        draw_line(canvas, (0, 0), (100, 0), "00ff00ff", thickness=3)
        _, _, _, _, _, paint = canvas.lines()[0]
        assert paint["color"] == "00ff00ff"
        assert paint["stroke_width"] == 3
        assert paint["style"] == MockStyle.STROKE

    def test_dashed_line_multiple_segments(self, canvas):
        # dash pattern: 12px dash, 6px gap over 100px line
        draw_line(canvas, (0, 0), (100, 0), "ff0000ff", line_style="dash")
        lines = canvas.lines()
        assert len(lines) > 1  # multiple dashes

    def test_dotted_line_multiple_segments(self, canvas):
        draw_line(canvas, (0, 0), (100, 0), "ff0000ff", line_style="dot")
        lines = canvas.lines()
        assert len(lines) > 1  # multiple dots

    def test_convenience_dotted(self, canvas):
        draw_dotted_line(canvas, (0, 0), (100, 0), "ff0000ff")
        assert len(canvas.lines()) > 1

    def test_convenience_dashed(self, canvas):
        draw_dashed_line(canvas, (0, 0), (100, 0), "ff0000ff")
        assert len(canvas.lines()) > 1

    def test_zero_length_no_draws(self, canvas):
        draw_line(canvas, (50, 50), (50, 50), "ff0000ff", line_style="dash")
        assert len(canvas.lines()) == 0


class TestSimplePatterns:
    def test_solid_is_zero_gap(self):
        assert SIMPLE_PATTERNS["solid"] == (0, 0)
        assert SIMPLE_PATTERNS["line"] == (0, 0)

    def test_all_styles_have_patterns(self):
        for style in ["solid", "line", "dash", "dot", "tick", "blip", "long"]:
            assert style in SIMPLE_PATTERNS
