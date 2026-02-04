"""Tests for MouseClockCore."""

import pytest

from core.mouse_clock import MouseClockCore
from core import config


class TestMouseClockCoreInit:
    def test_default_center(self):
        mc = MouseClockCore()
        assert mc.center_x == 0
        assert mc.center_y == 0

    def test_custom_center(self):
        mc = MouseClockCore(center_x=100, center_y=200)
        assert mc.center_x == 100
        assert mc.center_y == 200

    def test_default_radius(self):
        mc = MouseClockCore()
        assert mc.radius == config.DEFAULT_RADIUS

    def test_custom_radius(self):
        mc = MouseClockCore(radius=500)
        assert mc.radius == 500

    def test_initial_state(self):
        mc = MouseClockCore()
        assert mc.history == []
        assert mc.last_letters == []
        assert mc.last_colors == []


class TestUpdateCenter:
    def test_update(self):
        mc = MouseClockCore()
        mc.update_center(500, 300)
        assert mc.center_x == 500
        assert mc.center_y == 300


class TestCalculateMousePosition:
    def test_single_letter_single_color(self):
        mc = MouseClockCore(center_x=500, center_y=500, radius=300)
        x, y = mc.calculate_mouse_position(["c"], ["red"])
        # C = 90 degrees (clock) = right direction
        # red is index 1 out of 6, so radius * 1/6 = 50
        assert x > 500  # should move right
        assert y == pytest.approx(500, abs=5)

    def test_center_color_stays_at_center(self):
        mc = MouseClockCore(center_x=500, center_y=500, radius=300)
        x, y = mc.calculate_mouse_position(["a"], ["center"])
        # center = distance 0, so should stay at center
        assert x == pytest.approx(500, abs=1)
        assert y == pytest.approx(500, abs=1)

    def test_letter_f_goes_down(self):
        mc = MouseClockCore(center_x=500, center_y=500, radius=300)
        x, y = mc.calculate_mouse_position(["f"], ["pink"])
        # F = 180 degrees = down, pink is outermost ring
        assert y > 500

    def test_letter_l_goes_up(self):
        mc = MouseClockCore(center_x=500, center_y=500, radius=300)
        x, y = mc.calculate_mouse_position(["l"], ["pink"])
        # L = 0 degrees = up
        assert y < 500


class TestIncrementalMerging:
    def test_letters_only_merges_with_previous(self):
        mc = MouseClockCore(center_x=500, center_y=500, radius=300)
        # First command: letter + color
        mc.calculate_mouse_position(["a"], ["red"])
        # Second command: only letters - should merge with prev colors
        x, y = mc.calculate_mouse_position(["c"], [])
        # Should use red from previous
        assert mc.last_colors == ["red"]

    def test_colors_only_merges_with_previous(self):
        mc = MouseClockCore(center_x=500, center_y=500, radius=300)
        mc.calculate_mouse_position(["a"], ["red"])
        mc.calculate_mouse_position([], ["blue"])
        assert mc.last_letters == ["a"]

    def test_repeat_skips_merging(self):
        mc = MouseClockCore(center_x=500, center_y=500, radius=300)
        mc.calculate_mouse_position(["a"], ["red"])
        mc.last_letters = ["a"]
        mc.last_colors = ["red"]
        mc.calculate_mouse_position(["c"], ["blue"], is_repeat=True)
        # With repeat, should NOT merge
        assert mc.last_letters == ["c"]
        assert mc.last_colors == ["blue"]


class TestHistory:
    def test_add_and_pop(self):
        mc = MouseClockCore()
        mc.add_to_history(100, 200)
        mc.add_to_history(300, 400)
        assert mc.pop_from_history() == (300, 400)
        assert mc.pop_from_history() == (100, 200)

    def test_pop_empty(self):
        mc = MouseClockCore()
        assert mc.pop_from_history() is None


class TestRadius:
    def test_set_radius(self):
        mc = MouseClockCore()
        mc.set_radius(500)
        assert mc.radius == 500
        assert mc.target_radius == 500

    def test_set_radius_min_clamp(self):
        mc = MouseClockCore()
        mc.set_radius(5)
        assert mc.radius == config.MIN_RADIUS

    def test_widen_increases_target(self):
        mc = MouseClockCore(radius=100)
        mc.target_radius = 100
        mc.widen_radius()
        assert mc.target_radius > 100

    def test_narrow_decreases_target(self):
        mc = MouseClockCore(radius=100)
        mc.target_radius = 100
        mc.narrow_radius()
        assert mc.target_radius < 100

    def test_update_animation_converges(self):
        mc = MouseClockCore(radius=100)
        mc.target_radius = 200
        # Run enough iterations to converge
        for _ in range(200):
            still_animating = mc.update_radius_animation()
        assert mc.radius == pytest.approx(200, abs=1)

    def test_update_animation_no_change(self):
        mc = MouseClockCore(radius=100)
        mc.target_radius = 100
        assert mc.update_radius_animation() is False


class TestClearState:
    def test_clear(self):
        mc = MouseClockCore()
        mc.last_letters = ["a", "b"]
        mc.last_colors = ["red"]
        mc.clear_state()
        assert mc.last_letters == []
        assert mc.last_colors == []
        assert mc.last_command == ([], [])


class TestEdgeDistance:
    def test_right_edge(self):
        mc = MouseClockCore(center_x=500, center_y=500)
        dist = mc.calculate_edge_distance(90, (0, 0, 1000, 1000))
        assert dist == pytest.approx(500.0, abs=1)

    def test_up_edge(self):
        mc = MouseClockCore(center_x=500, center_y=500)
        dist = mc.calculate_edge_distance(0, (0, 0, 1000, 1000))
        assert dist == pytest.approx(500.0, abs=1)
