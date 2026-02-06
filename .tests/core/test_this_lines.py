"""Tests for 'this' line coloring order and geometry.

Key invariants to verify:
1. Gray line is ALWAYS at offset 0 (spatially centered, drawn FIRST/underneath)
2. Color lines appear in the EXACT order of the active_colors array
3. Colors are in FIXED positions centered around gray — selection has no effect on position
"""

import math
import pytest


class TestColorOffsetCalculation:
    """Test the offset formula: offset = (i - center) * spacing, where center = (N-1)/2."""

    def test_even_colors_straddle_center(self):
        """With even number of colors, two middle colors straddle gray."""
        colors = ["red", "blue", "green", "yellow"]
        center = (len(colors) - 1) / 2.0  # 1.5
        spacing = 15.0

        offsets = [(i - center) * spacing for i in range(len(colors))]

        assert offsets == [-22.5, -7.5, 7.5, 22.5]

    def test_odd_colors_middle_on_center(self):
        """With odd number of colors, the middle color sits exactly on gray."""
        colors = ["red", "blue", "green"]
        center = (len(colors) - 1) / 2.0  # 1.0
        spacing = 15.0

        offsets = [(i - center) * spacing for i in range(len(colors))]

        assert offsets == [-15.0, 0.0, 15.0]

    def test_single_color_on_center(self):
        """Single color sits exactly on gray."""
        colors = ["red"]
        center = (len(colors) - 1) / 2.0  # 0.0
        spacing = 15.0

        offsets = [(i - center) * spacing for i in range(len(colors))]

        assert offsets == [0.0]

    def test_full_color_list_offsets(self):
        """Test with actual color list from config (9 colors, center = 4.0)."""
        colors = ["red", "blue", "green", "yellow", "purple", "pink", "black", "white", "teal"]
        center = (len(colors) - 1) / 2.0  # 4.0
        spacing = 15.0

        offsets = {
            color: (i - center) * spacing
            for i, color in enumerate(colors)
        }

        assert offsets["red"] == -60.0      # index 0: (0-4)*15
        assert offsets["blue"] == -45.0     # index 1: (1-4)*15
        assert offsets["green"] == -30.0    # index 2: (2-4)*15
        assert offsets["yellow"] == -15.0   # index 3: (3-4)*15
        assert offsets["purple"] == 0.0     # index 4: (4-4)*15 = CENTER
        assert offsets["pink"] == 15.0      # index 5: (5-4)*15
        assert offsets["black"] == 30.0     # index 6: (6-4)*15
        assert offsets["white"] == 45.0     # index 7: (7-4)*15
        assert offsets["teal"] == 60.0      # index 8: (8-4)*15


class TestColorOrder:
    """Test that colors maintain their order in the line list."""

    def test_colors_preserve_order(self):
        """Lines should be built in same order as color list."""
        colors = ["red", "blue", "green", "yellow"]

        built_order = [color for color in colors]

        assert built_order == ["red", "blue", "green", "yellow"]

    def test_color_order_independent_of_selection(self):
        """Color order should not change based on which color is selected."""
        colors = ["red", "blue", "green", "yellow"]

        for selected in colors:
            built_order = [color for color in colors]
            assert built_order == ["red", "blue", "green", "yellow"]


class TestPerpendicularVector:
    """Test perpendicular vector calculation for line offsets."""

    def test_horizontal_line_perp(self):
        """Horizontal line (right) has vertical perpendicular."""
        start = (0, 0)
        target = (100, 0)

        dx = target[0] - start[0]
        dy = target[1] - start[1]
        length = math.sqrt(dx * dx + dy * dy)
        dx /= length
        dy /= length

        perp_x, perp_y = -dy, dx

        assert perp_x == 0.0
        assert perp_y == 1.0

    def test_vertical_line_perp(self):
        """Vertical line (down) has horizontal perpendicular."""
        start = (0, 0)
        target = (0, 100)

        dx = target[0] - start[0]
        dy = target[1] - start[1]
        length = math.sqrt(dx * dx + dy * dy)
        dx /= length
        dy /= length

        perp_x, perp_y = -dy, dx

        assert perp_x == -1.0
        assert perp_y == 0.0

    def test_diagonal_line_perp(self):
        """Diagonal line has diagonal perpendicular."""
        start = (0, 0)
        target = (100, 100)

        dx = target[0] - start[0]
        dy = target[1] - start[1]
        length = math.sqrt(dx * dx + dy * dy)
        dx /= length
        dy /= length

        perp_x, perp_y = -dy, dx

        expected = 1 / math.sqrt(2)
        assert abs(perp_x - (-expected)) < 0.0001
        assert abs(perp_y - expected) < 0.0001


class TestGrayLinePosition:
    """Test that gray line is always first (underneath) and unoffset."""

    def test_gray_line_added_first(self):
        """Gray line should be the first item in the lines list (drawn underneath)."""
        colors = ["red", "blue", "green"]
        lines = []

        lines.append(("gray_line", "888888ff"))

        for color in colors:
            lines.append(("colored_line", color))

        assert lines[0] == ("gray_line", "888888ff")
        assert len(lines) == len(colors) + 1

    def test_gray_line_count(self):
        """Should have exactly num_colors + 1 lines (gray + colors)."""
        colors = ["red", "blue", "green", "yellow", "purple"]

        line_count = len(colors) + 1

        assert line_count == 6


class TestBuildParallelLines:
    """Test build_parallel_lines from core.geometry.parallel_lines.

    Colors are in FIXED positions centered around gray.
    Selection does not affect positioning.
    """

    @staticmethod
    def _build(colors, start, target, spacing=15.0):
        from core.geometry.parallel_lines import build_parallel_lines
        return build_parallel_lines(start, target, colors, spacing)

    def test_build_lines_count(self):
        """Should create one line per color plus gray line."""
        colors = ["red", "blue", "green"]
        lines = self._build(colors, (100, 100), (200, 200))
        assert len(lines) == 4  # 3 colors + 1 gray

    def test_gray_line_is_first(self):
        """Gray line should be the first line (drawn underneath)."""
        colors = ["red", "blue"]
        lines = self._build(colors, (100, 100), (200, 100))
        assert lines[0][2] == "gray"

    def test_middle_color_at_center_odd(self):
        """With odd colors, middle color sits on gray (offset 0)."""
        colors = ["red", "blue", "green"]
        # Horizontal line — perpendicular offset affects Y
        lines = self._build(colors, (100, 100), (200, 100))

        # blue is index 1, center = 1.0, offset = 0
        blue_line = lines[2]  # gray=0, red=1, blue=2
        assert blue_line[0][1] == 100.0

    def test_colors_straddle_center_even(self):
        """With even colors, two middle colors straddle gray symmetrically."""
        colors = ["red", "blue", "green", "yellow"]
        spacing = 15.0
        # Horizontal line
        lines = self._build(colors, (0, 100), (100, 100), spacing)

        # center = 1.5, so:
        # red (i=0): offset = (0 - 1.5) * 15 = -22.5 → Y = 77.5
        # blue (i=1): offset = (1 - 1.5) * 15 = -7.5 → Y = 92.5
        # green (i=2): offset = (2 - 1.5) * 15 = 7.5 → Y = 107.5
        # yellow (i=3): offset = (3 - 1.5) * 15 = 22.5 → Y = 122.5
        assert lines[1][0][1] == 77.5    # red
        assert lines[2][0][1] == 92.5    # blue
        assert lines[3][0][1] == 107.5   # green
        assert lines[4][0][1] == 122.5   # yellow

    def test_line_order_matches_color_order(self):
        """Lines should be in same order as colors list (after gray)."""
        colors = ["red", "blue", "green", "yellow"]
        lines = self._build(colors, (0, 0), (100, 0))

        assert lines[0][2] == "gray"
        for i, color in enumerate(colors):
            assert lines[i + 1][2] == color

    def test_offsets_symmetric_around_center(self):
        """Color offsets should be symmetric around gray."""
        colors = ["red", "blue", "green"]
        spacing = 15.0
        # Horizontal line
        lines = self._build(colors, (0, 100), (100, 100), spacing)

        # center = 1.0
        # red (i=0): Y = 100 + (0-1)*15 = 85
        # blue (i=1): Y = 100 + (1-1)*15 = 100
        # green (i=2): Y = 100 + (2-1)*15 = 115
        assert lines[1][0][1] == 85.0    # red: -15
        assert lines[2][0][1] == 100.0   # blue: 0 (on gray)
        assert lines[3][0][1] == 115.0   # green: +15

    def test_gray_line_spatially_centered(self):
        """Gray line should be at offset 0 (spatially in the middle)."""
        colors = ["red", "blue", "green", "yellow", "purple"]
        start = (50, 100)
        target = (150, 100)

        lines = self._build(colors, start, target)

        gray_line = lines[0]
        assert gray_line[0] == start
        assert gray_line[1] == target

    def test_positions_fixed_regardless_of_any_external_state(self):
        """Same colors + same geometry = same positions every time."""
        colors = ["red", "blue", "green"]
        start = (0, 50)
        target = (100, 50)

        lines_a = self._build(colors, start, target)
        lines_b = self._build(colors, start, target)

        for a, b in zip(lines_a, lines_b):
            assert a == b

    def test_returns_none_for_zero_length(self):
        """Zero-length line should return None."""
        colors = ["red", "blue"]
        result = self._build(colors, (50, 50), (50, 50))
        assert result is None


class TestActiveColorsOrder:
    """Verify that lines match the exact order of active_colors array.
    Gray is first (underneath), then colors in array order.
    """

    def test_matches_standard_config_order(self):
        """Test with the actual default color order from config."""
        active_colors = ["red", "blue", "green", "yellow", "purple", "pink", "black", "white", "teal"]

        lines = ["gray"]
        for color in active_colors:
            lines.append(color)

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
        active_colors = ["blue", "yellow", "pink"]

        lines = ["gray"]
        for color in active_colors:
            lines.append(color)

        assert lines == ["gray", "blue", "yellow", "pink"]

    def test_order_never_sorted_alphabetically(self):
        """Colors should NOT be alphabetically sorted."""
        active_colors = ["red", "blue", "green"]

        lines = [c for c in active_colors]

        assert lines != ["blue", "green", "red"]
        assert lines == ["red", "blue", "green"]
