"""Tests for rendering/drawing/primitives.py."""

import pytest
from mocks.canvas import MockCanvas, MockStyle

# Import after talon mocks installed by conftest
from src.rendering.drawing.primitives import (
    draw_circle,
    draw_dot,
    draw_cross,
    draw_text,
    draw_rect,
)


@pytest.fixture
def canvas():
    return MockCanvas()


class TestDrawCircle:
    def test_stroke_circle(self, canvas):
        draw_circle(canvas, (100, 200), 50, "ff0000ff")
        assert len(canvas.circles()) == 1
        _, x, y, r, paint = canvas.circles()[0]
        assert (x, y, r) == (100, 200, 50)
        assert paint["color"] == "ff0000ff"
        assert paint["style"] == MockStyle.STROKE

    def test_filled_circle(self, canvas):
        draw_circle(canvas, (100, 200), 50, "00ff00ff", filled=True)
        _, x, y, r, paint = canvas.circles()[0]
        assert paint["style"] == MockStyle.FILL

    def test_custom_thickness(self, canvas):
        draw_circle(canvas, (0, 0), 10, "ffffffff", thickness=5)
        _, _, _, _, paint = canvas.circles()[0]
        assert paint["stroke_width"] == 5


class TestDrawDot:
    def test_dot_is_filled_circle(self, canvas):
        draw_dot(canvas, (50, 50), 3, "ff0000ff")
        assert len(canvas.circles()) == 1
        _, x, y, r, paint = canvas.circles()[0]
        assert (x, y, r) == (50, 50, 3)
        assert paint["style"] == MockStyle.FILL


class TestDrawCross:
    def test_plus_cross(self, canvas):
        draw_cross(canvas, (100, 100), 10, "00ff00ff")
        lines = canvas.lines()
        assert len(lines) == 2  # horizontal + vertical

    def test_x_cross(self, canvas):
        draw_cross(canvas, (100, 100), 10, "00ff00ff", style="x")
        lines = canvas.lines()
        assert len(lines) == 2  # two diagonals


class TestDrawText:
    def test_basic_text(self, canvas):
        draw_text(canvas, (100, 100), "hello", "ffffffff")
        texts = canvas.texts()
        assert len(texts) == 1
        assert texts[0][1] == "hello"

    def test_text_sets_color(self, canvas):
        draw_text(canvas, (0, 0), "test", "ff0000ff")
        _, _, _, _, paint = canvas.texts()[0]
        assert paint["color"] == "ff0000ff"

    def test_text_font_size(self, canvas):
        draw_text(canvas, (0, 0), "test", "ffffffff", font_size=24)
        _, _, _, _, paint = canvas.texts()[0]
        assert paint["textsize"] == 24


class TestDrawRect:
    def test_outline_rect_uses_lines(self, canvas):
        draw_rect(canvas, (10, 20, 100, 50), "ff0000ff")
        lines = canvas.lines()
        assert len(lines) == 4  # 4 sides
