"""
Info overlay rendering.

Draws a help/cheat sheet showing available voice commands.
"""

from typing import Tuple
from talon.skia import Paint

from ...rendering.drawing import draw_text, draw_line, draw_rect
from ...core.config import get_mode_config
from .data import (
    BG_COLOR,
    CLOCK_FACE_LETTERS,
    COLORS,
    HEADER_COLOR,
    LINE_STYLES,
    MUTED_COLOR,
    ROW_HEIGHT,
    SECTION_GAP,
    TEXT_COLOR,
)

# Color for inactive/disabled items
INACTIVE_COLOR = "666666ff"
# Color for active indicator
ACTIVE_INDICATOR = "00ff00ff"


def draw_letters_section(canvas, x: float, y: float) -> float:
    """Draw the letters/clock face section. Returns final y position."""
    draw_text(canvas, (x, y), "LETTERS (Clock Face)", HEADER_COLOR, font_size=18, anchor="left")
    y += ROW_HEIGHT + 10

    for letter, phonetic, number in CLOCK_FACE_LETTERS:
        line = f"{letter}  ->  {phonetic}  ({number})"
        draw_text(canvas, (x, y), line, TEXT_COLOR, font_size=16, anchor="left")
        y += ROW_HEIGHT

    return y


def draw_grid_colors_section(canvas, x: float, y: float) -> float:
    """Draw the grid colors section. Returns final y position."""
    active_colors = get_mode_config("grid", "colors")
    active_count = len(active_colors)
    total_count = len(COLORS)

    draw_text(canvas, (x, y), f"GRID COLORS ({active_count}/{total_count})", HEADER_COLOR, font_size=18, anchor="left")
    y += ROW_HEIGHT + 10

    for color_name, color_hex in COLORS:
        is_active = color_name in active_colors
        text_color = TEXT_COLOR if is_active else INACTIVE_COLOR
        # Dim the swatch for inactive colors
        swatch_color = color_hex if is_active else "333333ff"

        # Active indicator
        indicator = "+" if is_active else "-"
        indicator_color = ACTIVE_INDICATOR if is_active else INACTIVE_COLOR
        draw_text(canvas, (x, y), indicator, indicator_color, font_size=14, anchor="left")

        swatch_size = 16
        draw_rect(canvas, (x + 18, y - 12, swatch_size, swatch_size), swatch_color, thickness=0, filled=True)
        draw_text(canvas, (x + 18 + swatch_size + 10, y), color_name, text_color, font_size=16, anchor="left")
        y += ROW_HEIGHT

    return y


def draw_clock_colors_section(canvas, x: float, y: float) -> float:
    """Draw the clock (circles) colors section. Returns final y position."""
    active_colors = get_mode_config("circles", "colors")
    active_count = len(active_colors)
    total_count = len(COLORS)

    draw_text(canvas, (x, y), f"CLOCK COLORS ({active_count}/{total_count})", HEADER_COLOR, font_size=18, anchor="left")
    y += ROW_HEIGHT + 10

    for color_name, color_hex in COLORS:
        is_active = color_name in active_colors
        text_color = TEXT_COLOR if is_active else INACTIVE_COLOR
        swatch_color = color_hex if is_active else "333333ff"

        indicator = "+" if is_active else "-"
        indicator_color = ACTIVE_INDICATOR if is_active else INACTIVE_COLOR
        draw_text(canvas, (x, y), indicator, indicator_color, font_size=14, anchor="left")

        swatch_size = 16
        draw_rect(canvas, (x + 18, y - 12, swatch_size, swatch_size), swatch_color, thickness=0, filled=True)
        draw_text(canvas, (x + 18 + swatch_size + 10, y), color_name, text_color, font_size=16, anchor="left")
        y += ROW_HEIGHT

    return y


def draw_box_colors_section(canvas, x: float, y: float) -> float:
    """Draw the box colors section. Returns final y position."""
    active_colors = get_mode_config("boxes", "colors")
    active_count = len(active_colors)
    total_count = len(COLORS)

    draw_text(canvas, (x, y), f"BOX COLORS ({active_count}/{total_count})", HEADER_COLOR, font_size=18, anchor="left")
    y += ROW_HEIGHT + 10

    for color_name, color_hex in COLORS:
        is_active = color_name in active_colors
        text_color = TEXT_COLOR if is_active else INACTIVE_COLOR
        swatch_color = color_hex if is_active else "333333ff"

        indicator = "+" if is_active else "-"
        indicator_color = ACTIVE_INDICATOR if is_active else INACTIVE_COLOR
        draw_text(canvas, (x, y), indicator, indicator_color, font_size=14, anchor="left")

        swatch_size = 16
        draw_rect(canvas, (x + 18, y - 12, swatch_size, swatch_size), swatch_color, thickness=0, filled=True)
        draw_text(canvas, (x + 18 + swatch_size + 10, y), color_name, text_color, font_size=16, anchor="left")
        y += ROW_HEIGHT

    return y


def draw_commands_section(canvas, x: float, y: float) -> float:
    """Draw the commands section. Returns final y position."""
    draw_text(canvas, (x, y), "COMMANDS", HEADER_COLOR, font_size=18, anchor="left")
    y += ROW_HEIGHT + 10

    commands = [
        ("widen", "Increase radius"),
        ("narrow", "Decrease radius"),
        ("recenter", "Move clock to mouse"),
        ("touch", "Click and close"),
        ("reverse", "Opposite of last"),
    ]

    # Indent to match color names (swatch_size 16 + 10 gap = 26)
    indent = 26
    for cmd, desc in commands:
        draw_text(canvas, (x + indent, y), cmd, TEXT_COLOR, font_size=16, anchor="left")
        draw_text(canvas, (x + indent + 100, y), desc, MUTED_COLOR, font_size=14, anchor="left")
        y += ROW_HEIGHT

    return y


def draw_line_styles_section(canvas, x: float, y: float) -> float:
    """Draw the line styles section. Returns final y position."""
    active_styles = get_mode_config("grid", "styles")
    active_count = len(active_styles)
    total_count = len(LINE_STYLES)

    draw_text(canvas, (x, y), f"GRID STYLES ({active_count}/{total_count})", HEADER_COLOR, font_size=18, anchor="left")
    y += ROW_HEIGHT + 10

    h_line_length = 50
    v_line_length = 22  # Shorter to fit within row height
    v_stagger_step = 25  # Horizontal offset between stagger positions

    for i, style in enumerate(LINE_STYLES):
        is_active = style in active_styles
        text_color = TEXT_COLOR if is_active else INACTIVE_COLOR
        style_color = "00aaffff" if is_active else "444444ff"  # Dim inactive styles

        # Active indicator
        indicator = "+" if is_active else "-"
        indicator_color = ACTIVE_INDICATOR if is_active else INACTIVE_COLOR
        draw_text(canvas, (x, y), indicator, indicator_color, font_size=14, anchor="left")

        # Style name
        draw_text(canvas, (x + 18, y), style, text_color, font_size=14, anchor="left")

        # Horizontal sample
        h_start_x = x + 88
        h_y = y - 6
        # White base line showing click area
        draw_line(canvas, (h_start_x, h_y), (h_start_x + h_line_length, h_y), "ffffffff", thickness=1, line_style="solid")
        # Styled line on top
        draw_line(canvas, (h_start_x, h_y), (h_start_x + h_line_length, h_y), style_color, thickness=2, line_style=style)

        # Vertical sample - staggered horizontally in 3-step pattern
        stagger_offset = (i % 3) * v_stagger_step
        v_x = h_start_x + h_line_length + 20 + stagger_offset
        v_start_y = y - 6 - (v_line_length // 2)
        v_end_y = y - 6 + (v_line_length // 2)
        # White base line showing click area
        draw_line(canvas, (v_x, v_start_y), (v_x, v_end_y), "ffffffff", thickness=1, line_style="solid")
        # Styled line on top
        draw_line(canvas, (v_x, v_start_y), (v_x, v_end_y), style_color, thickness=2, line_style=style)

        y += ROW_HEIGHT

    return y


def draw_info_overlay(
    canvas,
    screen_rect: Tuple[float, float, float, float],
):
    """
    Draw the info/help overlay showing available voice commands.

    Args:
        canvas: Talon canvas object
        screen_rect: (left, top, right, bottom) screen bounds
    """
    left, top, right, bottom = screen_rect
    screen_width = right - left
    screen_height = bottom - top

    # Layout
    padding = 40
    col_width = 340

    # Draw semi-transparent background
    draw_rect(canvas, (left, top, screen_width, screen_height), BG_COLOR, thickness=0, filled=True)

    # Title
    title_y = top + padding
    draw_text(canvas, (left + padding, title_y), "MOUSE CLOCK COMMANDS", HEADER_COLOR, font_size=24, anchor="left")

    content_top = title_y + 50

    # Column positions (4 columns)
    col_width = 280
    col1_x = left + padding
    col2_x = col1_x + col_width
    col3_x = col2_x + col_width + 40  # Extra gap before styles
    col4_x = col3_x + col_width

    # Column 1: Letters + Commands
    y = draw_letters_section(canvas, col1_x, content_top)
    y += SECTION_GAP
    draw_commands_section(canvas, col1_x, y)

    # Column 2: All color configs stacked
    y = draw_grid_colors_section(canvas, col2_x, content_top)
    y += SECTION_GAP // 2
    y = draw_clock_colors_section(canvas, col2_x, y)
    y += SECTION_GAP // 2
    draw_box_colors_section(canvas, col2_x, y)

    # Column 3: Grid Styles (takes more space)
    draw_line_styles_section(canvas, col3_x, content_top)

    # Footer
    footer_y = bottom - padding
    draw_text(canvas, (left + padding, footer_y), "Press super-w to cycle display modes", MUTED_COLOR, font_size=14, anchor="left")
