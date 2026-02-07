_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Grid overlay rendering.

Drawing functions for the letter/color grid overlay.
Uses active colors, styles, and letters from settings.
"""

from typing import Tuple, List

from ...rendering.colors import get_color, with_alpha
from ...rendering.drawing import draw_line, draw_text, draw_rect
from .config import get_text_color, get_text_bg_color, get_grid_colors, get_horizontal_styles, get_vertical_styles, get_grid_letters
from .layout import calculate_row_positions, calculate_column_positions
from ..shared.alpha import apply_alpha, set_alpha


def draw_grid_overlay(
    canvas,
    screen_rect: Tuple[float, float, float, float],
    swap_axes: bool = False,
    alpha: int = 255
):
    """
    Draw the letter/color grid overlay.

    Args:
        canvas: Talon canvas object
        screen_rect: (left, top, right, bottom) screen bounds
        swap_axes: If True, colors on Y-axis and letters on X-axis
        alpha: Overall transparency (0-255) for fade effects
    """
    set_alpha("grid", alpha)

    left, top, right, bottom = screen_rect

    colors = get_grid_colors()
    h_styles = get_horizontal_styles()
    v_styles = get_vertical_styles()
    letters = get_grid_letters()

    if swap_axes:
        # Colors on Y, Letters on X
        row_positions = calculate_row_positions(top, bottom, len(colors) * len(h_styles))
        row_labels = []
        row_styles = []
        for color in colors:
            for style in h_styles:
                row_labels.append(color)
                row_styles.append(style)

        col_positions = calculate_column_positions(left, right, len(letters) * len(v_styles))
        col_labels = []
        col_styles = []
        for letter in letters:
            for style in v_styles:
                col_labels.append(letter)
                col_styles.append(style)
    else:
        # Letters on Y, Colors on X (default)
        row_positions = calculate_row_positions(top, bottom, len(letters) * len(h_styles))
        row_labels = []
        row_styles = []
        for letter in letters:
            for style in h_styles:
                row_labels.append(letter)
                row_styles.append(style)

        col_positions = calculate_column_positions(left, right, len(colors) * len(v_styles))
        col_labels = []
        col_styles = []
        for color in colors:
            for style in v_styles:
                col_labels.append(color)
                col_styles.append(style)

    # Draw horizontal lines (rows)
    _draw_row_lines(canvas, row_positions, row_labels, row_styles, left, right, swap_axes, h_styles)

    # Draw vertical lines (columns)
    _draw_column_lines(canvas, col_positions, col_labels, col_styles, top, bottom, swap_axes, v_styles)

    # Draw intersection markers
    _draw_intersections(canvas, row_positions, col_positions, row_labels, col_labels, swap_axes)


def _draw_row_lines(
    canvas,
    positions: List[float],
    labels: List[str],
    styles: List[str],
    left: float,
    right: float,
    swap_axes: bool,
    active_styles: List[str]
):
    """Draw horizontal lines with labels."""
    label_margin = 30
    text_color = apply_alpha(get_text_color(), "grid")
    bg_color = apply_alpha(get_text_bg_color(), "grid")
    first_style = active_styles[0] if active_styles else None

    for y, label, style in zip(positions, labels, styles):
        # Get line color
        if swap_axes:
            # Label is a color name
            line_color = apply_alpha(get_color(label), "grid")
        else:
            # Label is a letter, use white
            line_color = apply_alpha("ffffff99", "grid")  # Semi-transparent white

        # Draw the horizontal line
        draw_line(canvas, (left + label_margin, y), (right, y), line_color, thickness=1, line_style=style)

        # Draw the label with background (only for first style to avoid clutter)
        if style == first_style:
            label_text = label.upper() if not swap_axes else label.capitalize()
            draw_rect(canvas, (left + 2, y - 8, 22, 18), bg_color, thickness=0, filled=True)
            draw_text(canvas, (left + 5, y + 5), label_text, text_color, font_size=14, anchor="left")


def _draw_column_lines(
    canvas,
    positions: List[float],
    labels: List[str],
    styles: List[str],
    top: float,
    bottom: float,
    swap_axes: bool,
    active_styles: List[str]
):
    """Draw vertical lines with labels."""
    text_color = apply_alpha(get_text_color(), "grid")
    bg_color = apply_alpha(get_text_bg_color(), "grid")

    for i, (x, label, style) in enumerate(zip(positions, labels, styles)):
        # Get line color
        if swap_axes:
            # Label is a letter, use white
            line_color = apply_alpha("ffffff99", "grid")
            label_margin = 25
        else:
            # Label is a color name - no label needed, colors are self-explanatory
            line_color = apply_alpha(get_color(label), "grid")
            label_margin = 0

        # Draw the vertical line
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
