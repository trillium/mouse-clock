"""
Dense grid overlay rendering.

Draws a small, dense rectangle of colored letters centered on the mouse:
  Columns = letters, Rows = colors, ~10px spacing.
"""

from ...rendering.colors import get_color, parse_hex_color, relative_luminance
from ...rendering.drawing import draw_text, draw_rect
from .config import get_dense_grid_colors, get_dense_grid_letters, get_dense_grid_spacing_x, get_dense_grid_spacing_y
from ..shared.alpha import apply_alpha, set_alpha
FONT_SIZE = 11
PADDING = 6
LIGHT_BG_COLOR = "ffffffaa"


def _is_dark_color(color_hex: str) -> bool:
    """Check if a color is very dark (needs light background for readability)."""
    try:
        r, g, b, _ = parse_hex_color(color_hex)
        lum = relative_luminance(r, g, b)
        return lum < 0.05
    except (ValueError, IndexError):
        return False


def draw_dense_grid_overlay(
    canvas,
    center_x: float,
    center_y: float,
    alpha: int = 255
):
    """
    Draw a small dense grid centered on (center_x, center_y).

    Args:
        canvas: Talon canvas object
        center_x: X center of the grid (mouse position)
        center_y: Y center of the grid (mouse position)
        alpha: Overall transparency (0-255) for fade effects
    """
    set_alpha("dense_grid", alpha)

    colors = get_dense_grid_colors()
    letters = get_dense_grid_letters()

    if not colors or not letters:
        return

    num_cols = len(letters)
    num_rows = len(colors)

    spacing_x = get_dense_grid_spacing_x()
    spacing_y = get_dense_grid_spacing_y()

    # Total grid size
    grid_width = (num_cols - 1) * spacing_x
    grid_height = (num_rows - 1) * spacing_y

    # Top-left of grid, centered on mouse
    grid_left = center_x - grid_width / 2
    grid_top = center_y - grid_height / 2

    # Draw background rectangle
    bg_rect = (
        grid_left - PADDING,
        grid_top - PADDING,
        grid_width + PADDING * 2,
        grid_height + PADDING * 2
    )
    draw_rect(canvas, bg_rect, apply_alpha("000000cc", "dense_grid"), thickness=0, filled=True)

    # Draw each letter in its color
    for row_idx, color_name in enumerate(colors):
        y = grid_top + row_idx * spacing_y
        raw_color = get_color(color_name)
        text_color = apply_alpha(raw_color, "dense_grid")
        needs_bg = _is_dark_color(raw_color)

        for col_idx, letter in enumerate(letters):
            x = grid_left + col_idx * spacing_x

            if needs_bg:
                box_size = FONT_SIZE + 2
                draw_rect(
                    canvas,
                    (x - box_size / 2, y - box_size / 2, box_size, box_size),
                    apply_alpha(LIGHT_BG_COLOR, "dense_grid"),
                    thickness=0,
                    filled=True
                )

            draw_text(
                canvas,
                (x, y),
                letter.upper(),
                text_color,
                font_size=FONT_SIZE,
                anchor="center"
            )
