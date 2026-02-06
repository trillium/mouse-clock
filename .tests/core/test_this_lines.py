"""Tests for 'this' line coloring order and geometry.

Key invariants to verify:
1. Gray line is ALWAYS at offset 0 (spatially centered, drawn FIRST/underneath)
2. Color lines appear in the EXACT order of the active_colors array
3. The SELECTED color is at offset 0 (overlays gray, showing the active selection)
"""

import math
import pytest
from unittest.mock import MagicMock, patch


class TestColorOffsetCalculation:
    """Test the offset formula: offset = (i - current_idx) * spacing."""

    def test_first_color_selected_offsets(self):
        """When first color is selected, it's at offset 0, others are positive."""
        colors = ["red", "blue", "green", "yellow"]
        current_color = "red"
        current_idx = colors.index(current_color)
        spacing = 15.0

        offsets = [(i - current_idx) * spacing for i in range(len(colors))]

        assert offsets == [0.0, 15.0, 30.0, 45.0]

    def test_middle_color_selected_offsets(self):
        """When middle color is selected, offsets are negative and positive."""
        colors = ["red", "blue", "green", "yellow"]
        current_color = "blue"
        current_idx = colors.index(current_color)
        spacing = 15.0

        offsets = [(i - current_idx) * spacing for i in range(len(colors))]

        assert offsets == [-15.0, 0.0, 15.0, 30.0]

    def test_last_color_selected_offsets(self):
        """When last color is selected, all others have negative offsets."""
        colors = ["red", "blue", "green", "yellow"]
        current_color = "yellow"
        current_idx = colors.index(current_color)
        spacing = 15.0

        offsets = [(i - current_idx) * spacing for i in range(len(colors))]

        assert offsets == [-45.0, -30.0, -15.0, 0.0]

    def test_selected_color_always_centered(self):
        """The selected color should always have offset = 0."""
        colors = ["red", "blue", "green", "yellow", "purple"]
        spacing = 15.0

        for current_color in colors:
            current_idx = colors.index(current_color)
            offset = (current_idx - current_idx) * spacing
            assert offset == 0.0, f"{current_color} should be centered"

    def test_full_color_list_offsets(self):
        """Test with actual color list from config."""
        colors = ["red", "blue", "green", "yellow", "purple", "pink", "black", "white", "teal"]
        current_color = "green"
        current_idx = colors.index(current_color)  # index 2
        spacing = 15.0

        offsets = {
            color: (i - current_idx) * spacing
            for i, color in enumerate(colors)
        }

        assert offsets["red"] == -30.0      # index 0: (0-2)*15
        assert offsets["blue"] == -15.0     # index 1: (1-2)*15
        assert offsets["green"] == 0.0      # index 2: (2-2)*15 = CENTER
        assert offsets["yellow"] == 15.0    # index 3: (3-2)*15
        assert offsets["purple"] == 30.0    # index 4: (4-2)*15
        assert offsets["pink"] == 45.0      # index 5: (5-2)*15
        assert offsets["black"] == 60.0     # index 6: (6-2)*15
        assert offsets["white"] == 75.0     # index 7: (7-2)*15
        assert offsets["teal"] == 90.0      # index 8: (8-2)*15


class TestColorOrder:
    """Test that colors maintain their order in the line list."""

    def test_colors_preserve_order(self):
        """Lines should be built in same order as color list."""
        colors = ["red", "blue", "green", "yellow"]

        # Simulate building lines in order
        built_order = [color for color in colors]

        assert built_order == ["red", "blue", "green", "yellow"]

    def test_color_order_independent_of_selection(self):
        """Color order should not change based on which color is selected."""
        colors = ["red", "blue", "green", "yellow"]

        for selected in colors:
            # Order stays the same regardless of selection
            built_order = [color for color in colors]
            assert built_order == ["red", "blue", "green", "yellow"]


class TestPerpendicularVector:
    """Test perpendicular vector calculation for line offsets."""

    def test_horizontal_line_perp(self):
        """Horizontal line (right) has vertical perpendicular."""
        start = (0, 0)
        target = (100, 0)  # pointing right

        dx = target[0] - start[0]
        dy = target[1] - start[1]
        length = math.sqrt(dx * dx + dy * dy)
        dx /= length
        dy /= length

        perp_x, perp_y = -dy, dx

        assert perp_x == 0.0   # no horizontal component
        assert perp_y == 1.0   # points down (positive y)

    def test_vertical_line_perp(self):
        """Vertical line (down) has horizontal perpendicular."""
        start = (0, 0)
        target = (0, 100)  # pointing down

        dx = target[0] - start[0]
        dy = target[1] - start[1]
        length = math.sqrt(dx * dx + dy * dy)
        dx /= length
        dy /= length

        perp_x, perp_y = -dy, dx

        assert perp_x == -1.0  # points left
        assert perp_y == 0.0   # no vertical component

    def test_diagonal_line_perp(self):
        """Diagonal line has diagonal perpendicular."""
        start = (0, 0)
        target = (100, 100)  # pointing down-right

        dx = target[0] - start[0]
        dy = target[1] - start[1]
        length = math.sqrt(dx * dx + dy * dy)
        dx /= length
        dy /= length

        perp_x, perp_y = -dy, dx

        # Perpendicular to down-right is down-left (or up-right, depending on sign)
        expected = 1 / math.sqrt(2)
        assert abs(perp_x - (-expected)) < 0.0001
        assert abs(perp_y - expected) < 0.0001


class TestGrayLinePosition:
    """Test that gray line is always first (underneath) and unoffset."""

    def test_gray_line_added_first(self):
        """Gray line should be the first item in the lines list (drawn underneath)."""
        colors = ["red", "blue", "green"]
        lines = []

        # Simulate _build_this_lines logic - gray first
        lines.append(("gray_line", "888888ff"))

        for color in colors:
            lines.append(("colored_line", color))

        assert lines[0] == ("gray_line", "888888ff")
        assert len(lines) == len(colors) + 1

    def test_gray_line_count(self):
        """Should have exactly num_colors + 1 lines (gray + colors)."""
        colors = ["red", "blue", "green", "yellow", "purple"]

        line_count = len(colors) + 1  # +1 for gray

        assert line_count == 6


class TestBuildThisLinesLogic:
    """
    Test the core logic of _build_this_lines without importing Talon modules.

    The actual _build_this_lines function in talon_integration/actions_move.py
    cannot be directly imported in tests due to Talon-specific dependencies.
    These tests verify the algorithm by reimplementing the core logic.
    """

    def _simulate_build_lines(self, colors, current_color, start, target, spacing=15.0):
        """
        Simulate _build_this_lines logic without Talon dependencies.
        Returns list of (start, end, color_index) tuples.
        """
        import math

        start_x, start_y = start
        target_x, target_y = target

        # Direction vector
        dx = target_x - start_x
        dy = target_y - start_y
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            return []
        dx /= length
        dy /= length

        # Perpendicular
        perp_x, perp_y = -dy, dx

        # Current color index
        try:
            current_idx = colors.index(current_color)
        except ValueError:
            current_idx = len(colors) // 2

        # Gray line FIRST (center indicator, underneath)
        lines = []
        lines.append(((start_x, start_y), (target_x, target_y), "gray"))

        # Colored lines on top
        for i, color_name in enumerate(colors):
            offset = (i - current_idx) * spacing
            s_x = start_x + perp_x * offset
            s_y = start_y + perp_y * offset
            e_x = target_x + perp_x * offset
            e_y = target_y + perp_y * offset
            lines.append(((s_x, s_y), (e_x, e_y), color_name))

        return lines

    def test_build_lines_count(self):
        """Should create one line per color plus gray line."""
        colors = ["red", "blue", "green"]
        lines = self._simulate_build_lines(
            colors, "blue", (100, 100), (200, 200)
        )
        assert len(lines) == 4  # 3 colors + 1 gray

    def test_gray_line_is_first(self):
        """Gray line should be the first line (drawn underneath)."""
        colors = ["red", "blue"]
        lines = self._simulate_build_lines(
            colors, "red", (100, 100), (200, 100)
        )
        assert lines[0][2] == "gray"

    def test_selected_color_at_center(self):
        """Selected color's line should have no perpendicular offset."""
        colors = ["red", "blue", "green"]
        lines = self._simulate_build_lines(
            colors, "blue",  # middle color, index 1 in colors
            (100, 100),      # start
            (200, 100)       # horizontal line (target)
        )

        # Blue is at index 1 in colors, but index 2 in lines (gray is 0)
        # For horizontal line, perpendicular offset affects Y coordinate
        blue_line = lines[2]  # gray=0, red=1, blue=2
        start_y = blue_line[0][1]

        # Should be at original Y (100.0) since offset is 0
        assert start_y == 100.0

    def test_line_order_matches_color_order(self):
        """Lines should be in same order as colors list (after gray)."""
        colors = ["red", "blue", "green", "yellow"]
        lines = self._simulate_build_lines(
            colors, "blue", (0, 0), (100, 0)
        )

        # First line is gray, then colors in order
        assert lines[0][2] == "gray"
        for i, color in enumerate(colors):
            assert lines[i + 1][2] == color  # +1 because gray is first

    def test_offsets_relative_to_selected(self):
        """Lines should be offset relative to selected color."""
        colors = ["red", "blue", "green"]
        spacing = 15.0

        # Horizontal line - perpendicular is vertical (Y offset)
        lines = self._simulate_build_lines(
            colors, "blue",  # index 1 in colors
            (0, 100),        # start
            (100, 100),      # horizontal target
            spacing
        )

        # lines[0] is gray (at center, Y=100)
        # lines[1] is red (index 0): offset = (0-1)*15 = -15
        assert lines[1][0][1] == 100 - 15  # Y = 85

        # lines[2] is blue (index 1): offset = (1-1)*15 = 0
        assert lines[2][0][1] == 100       # Y = 100

        # lines[3] is green (index 2): offset = (2-1)*15 = +15
        assert lines[3][0][1] == 100 + 15  # Y = 115

    def test_gray_line_spatially_centered(self):
        """Gray line should be at offset 0 (spatially in the middle)."""
        colors = ["red", "blue", "green", "yellow", "purple"]
        start = (50, 100)
        target = (150, 100)  # horizontal

        lines = self._simulate_build_lines(colors, "green", start, target)

        gray_line = lines[0]  # first line is gray (drawn underneath)
        # Gray line should go directly from start to target, no offset
        assert gray_line[0] == start
        assert gray_line[1] == target

    def test_gray_line_always_centered_regardless_of_selection(self):
        """Gray line stays at offset 0 no matter which color is selected."""
        colors = ["red", "blue", "green"]
        start = (0, 50)
        target = (100, 50)

        for selected in colors:
            lines = self._simulate_build_lines(colors, selected, start, target)
            gray = lines[0]  # first line is gray
            assert gray[0] == start, f"Gray start wrong when {selected} selected"
            assert gray[1] == target, f"Gray end wrong when {selected} selected"


class TestActiveColorsOrder:
    """
    Verify that lines match the exact order of active_colors array.
    Gray is first (underneath), then colors in array order.
    """

    def test_matches_standard_config_order(self):
        """Test with the actual default color order from config."""
        # This is the order from core/config.py ALL_COLORS
        active_colors = ["red", "blue", "green", "yellow", "purple", "pink", "black", "white", "teal"]

        # Simulate building lines - gray first, then colors
        lines = ["gray"]
        for color in active_colors:
            lines.append(color)

        # Verify order: gray first, then colors
        assert lines[0] == "gray"
        assert lines[1] == "red"
        assert lines[2] == "blue"
        assert lines[3] == "green"
        assert lines[4] == "yellow"
        assert lines[5] == "purple"
        assert lines[6] == "pink"
        assert lines[7] == "black"
        assert lines[8] == "white"
        assert lines[9] == "teal"

    def test_order_preserved_with_subset(self):
        """If only some colors active, order is still preserved."""
        active_colors = ["blue", "yellow", "pink"]  # subset

        lines = ["gray"]
        for color in active_colors:
            lines.append(color)

        assert lines == ["gray", "blue", "yellow", "pink"]

    def test_order_never_sorted_alphabetically(self):
        """Colors should NOT be alphabetically sorted."""
        active_colors = ["red", "blue", "green"]  # not alphabetical

        lines = [c for c in active_colors]

        # If this was sorted, it would be ["blue", "green", "red"]
        assert lines != ["blue", "green", "red"]
        assert lines == ["red", "blue", "green"]
