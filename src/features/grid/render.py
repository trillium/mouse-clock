"""
Grid overlay rendering.

Drawing functions for the letter/color grid overlay.
"""

print("reloaded trillium/mouse-clock/src/features/grid/render.py 2")

from typing import Tuple, List

from ...core.config import get_setting
from ...rendering.colors import get_color
from ...rendering.drawing import draw_line, draw_text, draw_rect
from .config import get_text_color, get_text_bg_color, get_grid_colors
from .layout import get_visible_letters, calculate_row_positions, calculate_column_positions


def draw_grid_overlay(
    canvas,
    screen_rect: Tuple[float, float, float, float],
    swap_axes: bool = False
):
    """
    Draw the letter/color grid overlay.

    Args:
        canvas: Talon canvas object
        screen_rect: (left, top, right, bottom) screen bounds
        swap_axes: If True, colors on Y-axis and letters on X-axis
    """
    left, top, right, bottom = screen_rect

    colors = get_grid_colors()

    # Calculate how many letters fit
    row_spacing = get_setting("grid_row_spacing", 40)
    screen_height = bottom - top
    letters = get_visible_letters(screen_height, row_spacing)

    # Line styles for each color (3 lines per color)
    line_styles = ["solid", "dashed", "dotted"]

    if swap_axes:
        # Colors on Y, Letters on X
        row_positions = calculate_row_positions(top, bottom, len(colors))
        col_positions = calculate_column_positions(left, right, len(letters))
        row_labels = colors
        col_labels = letters
        col_styles = ["solid"] * len(letters)
    else:
        # Letters on Y, Colors on X (default)
        # 3 lines per color: solid, dashed, dotted
        row_positions = calculate_row_positions(top, bottom, len(letters))
        col_positions = calculate_column_positions(left, right, len(colors) * 3)
        # Expand colors and styles: [red, red, red, blue, blue, blue, ...]
        col_labels = []
        col_styles = []
        for color in colors:
            for style in line_styles:
                col_labels.append(color)
                col_styles.append(style)
        row_labels = letters

    # Draw horizontal lines (rows)
    _draw_row_lines(canvas, row_positions, row_labels, left, right, swap_axes)

    # Draw vertical lines (columns)
    _draw_column_lines(canvas, col_positions, col_labels, col_styles, top, bottom, swap_axes)

    # Draw intersection markers
    _draw_intersections(canvas, row_positions, col_positions, row_labels, col_labels, swap_axes)


def _draw_row_lines(
    canvas,
    positions: List[float],
    labels: List[str],
    left: float,
    right: float,
    swap_axes: bool
):
    """Draw horizontal lines with labels."""
    label_margin = 30
    text_color = get_text_color()
    bg_color = get_text_bg_color()

    for y, label in zip(positions, labels):
        # Get line color
        if swap_axes:
            # Label is a color name
            line_color = get_color(label)
        else:
            # Label is a letter, use white
            line_color = "ffffff99"  # Semi-transparent white

        # Draw the horizontal line
        print(f"[DEBUG _draw_row_lines] label={label}, y={y:.0f}, color={line_color[:6]}")
        draw_line(canvas, (left + label_margin, y), (right, y), line_color, thickness=1)

        # Draw the label with background
        label_text = label.upper() if not swap_axes else label.capitalize()
        # Draw background rect
        draw_rect(canvas, (left + 2, y - 8, 22, 18), bg_color, thickness=0, filled=True)
        draw_text(canvas, (left + 5, y + 5), label_text, text_color, font_size=14, anchor="left")


def _draw_column_lines(
    canvas,
    positions: List[float],
    labels: List[str],
    styles: List[str],
    top: float,
    bottom: float,
    swap_axes: bool
):
    """Draw vertical lines with labels (only for letters, not colors)."""
    text_color = get_text_color()
    bg_color = get_text_bg_color()

    for x, label, style in zip(positions, labels, styles):
        # Get line color
        if swap_axes:
            # Label is a letter, use white
            line_color = "ffffff99"
            label_margin = 25
        else:
            # Label is a color name - no label needed, colors are self-explanatory
            line_color = get_color(label)
            label_margin = 0

        # Draw the vertical line
        print(f"[DEBUG _draw_column_lines] label={label}, x={x:.0f}, color={line_color[:6]}, style={style}")
        draw_line(canvas, (x, top + label_margin), (x, bottom), line_color, thickness=1, line_style=style)

        # Only draw labels for letters (swap_axes mode), not colors
        if swap_axes:
            label_text = label.upper()
            text_width = len(label_text) * 7 + 6
            draw_rect(canvas, (x - text_width/2, top + 5, text_width, 18), bg_color, thickness=0, filled=True)
            draw_text(canvas, (x, top + 18), label_text, text_color, font_size=12, anchor="center")


def _draw_intersections(
    canvas,
    row_positions: List[float],
    col_positions: List[float],
    row_labels: List[str],
    col_labels: List[str],
    swap_axes: bool
):
    """Draw markers at grid intersections."""
    # TODO: Add intersection markers/dots
    pass
