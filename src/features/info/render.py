_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Info overlay rendering.

Draws mode-specific help panels showing config and voice commands.
Cycles through: Grid -> Boxes -> Circles
"""

from typing import Tuple, List
from talon.skia import Paint

from ...rendering.drawing import draw_text, draw_line, draw_rect
from ...core.config import (
    get_mode_config,
    get_info_panel_mode,
    get_info_panel_index,
    get_info_panel_total,
    get_info_edit_focus,
)
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
from .contrast import relative_luminance, parse_hex_color

# Color for inactive/disabled items
INACTIVE_COLOR = "666666ff"
# Color for active indicator
ACTIVE_INDICATOR = "00ff00ff"


# =============================================================================
# Command Data for Each Mode
# =============================================================================

GRID_COMMANDS = [
    ("set horizontal", "Edit horiz styles"),
    ("set vertical", "Edit vert styles"),
    ("set colors", "Edit colors"),
    ("add <item>", "Add to focused"),
    ("remove <item>", "Remove from focused"),
    ("next panel", "Next mode"),
    ("previous panel", "Prev mode"),
]

BOXES_COMMANDS = [
    ("set colors", "Edit colors (default)"),
    ("add <color>", "Add color"),
    ("remove <color>", "Remove color"),
    ("next panel", "Next mode"),
    ("previous panel", "Prev mode"),
]

CIRCLES_COMMANDS = [
    ("set colors", "Edit colors (default)"),
    ("add <color>", "Add color"),
    ("remove <color>", "Remove color"),
    ("next panel", "Next mode"),
    ("previous panel", "Prev mode"),
]


# =============================================================================
# Shared Drawing Helpers
# =============================================================================

def _get_contrast_text_color(color_hex: str) -> str:
    """Return black or white text color based on background luminance."""
    try:
        r, g, b, _ = parse_hex_color(color_hex)
        lum = relative_luminance(r, g, b)
        # Use black text on light backgrounds, white on dark
        return "000000ff" if lum > 0.5 else "ffffffff"
    except (ValueError, IndexError):
        return TEXT_COLOR


def draw_colors_section(canvas, x: float, y: float, mode: str, header: str) -> float:
    """Draw a colors section for a mode. Returns final y position."""
    active_colors = get_mode_config(mode, "colors")
    active_count = len(active_colors)
    total_count = len(COLORS)

    draw_text(canvas, (x, y), f"{header} ({active_count}/{total_count})", HEADER_COLOR, font_size=18, anchor="left")
    y += ROW_HEIGHT + 10

    for color_name, color_hex in COLORS:
        is_active = color_name in active_colors
        swatch_color = color_hex if is_active else "333333ff"
        # Use contrast-aware text color based on swatch brightness
        text_color = _get_contrast_text_color(swatch_color) if is_active else INACTIVE_COLOR

        indicator = "+" if is_active else "-"
        indicator_color = ACTIVE_INDICATOR if is_active else INACTIVE_COLOR
        draw_text(canvas, (x, y), indicator, indicator_color, font_size=14, anchor="left")

        swatch_size = 16
        draw_rect(canvas, (x + 18, y - 12, swatch_size, swatch_size), swatch_color, thickness=0, filled=True)
        draw_text(canvas, (x + 18 + swatch_size + 10, y), color_name, text_color, font_size=16, anchor="left")
        y += ROW_HEIGHT

    return y


def draw_styles_section(canvas, x: float, y: float, dimension: str, header: str, is_horizontal: bool = True) -> float:
    """Draw a styles section. Returns final y position.

    Args:
        canvas: Canvas to draw on
        x, y: Starting position
        dimension: "horizontal_styles" or "vertical_styles"
        header: Section header text
        is_horizontal: If True, draw horizontal line samples; if False, draw vertical
    """
    active_styles = get_mode_config("grid", dimension)
    active_count = len(active_styles)
    total_count = len(LINE_STYLES)

    draw_text(canvas, (x, y), f"{header} ({active_count}/{total_count})", HEADER_COLOR, font_size=18, anchor="left")
    y += ROW_HEIGHT + 10

    sample_length = 50

    for i, style in enumerate(LINE_STYLES):
        is_active = style in active_styles
        text_color = TEXT_COLOR if is_active else INACTIVE_COLOR
        style_color = "00aaffff" if is_active else "444444ff"

        indicator = "+" if is_active else "-"
        indicator_color = ACTIVE_INDICATOR if is_active else INACTIVE_COLOR
        draw_text(canvas, (x, y), indicator, indicator_color, font_size=14, anchor="left")

        draw_text(canvas, (x + 18, y), style, text_color, font_size=14, anchor="left")

        # Draw sample line
        sample_x = x + 88
        if is_horizontal:
            # Horizontal sample
            sample_y = y - 6
            draw_line(canvas, (sample_x, sample_y), (sample_x + sample_length, sample_y), "ffffffff", thickness=1, line_style="solid")
            draw_line(canvas, (sample_x, sample_y), (sample_x + sample_length, sample_y), style_color, thickness=2, line_style=style)
        else:
            # Vertical sample
            sample_y_start = y - 6 - (sample_length // 4)
            sample_y_end = y - 6 + (sample_length // 4)
            draw_line(canvas, (sample_x + 25, sample_y_start), (sample_x + 25, sample_y_end), "ffffffff", thickness=1, line_style="solid")
            draw_line(canvas, (sample_x + 25, sample_y_start), (sample_x + 25, sample_y_end), style_color, thickness=2, line_style=style)

        y += ROW_HEIGHT

    return y


def draw_letters_section(canvas, x: float, y: float) -> float:
    """Draw the letters/clock face section. Returns final y position."""
    draw_text(canvas, (x, y), "LETTERS (Clock Face)", HEADER_COLOR, font_size=18, anchor="left")
    y += ROW_HEIGHT + 10

    for letter, phonetic, number in CLOCK_FACE_LETTERS:
        line = f"{letter}  ->  {phonetic}  ({number})"
        draw_text(canvas, (x, y), line, TEXT_COLOR, font_size=16, anchor="left")
        y += ROW_HEIGHT

    return y


def draw_commands_section(canvas, x: float, y: float, commands: List[Tuple[str, str]]) -> float:
    """Draw a commands section. Returns final y position."""
    draw_text(canvas, (x, y), "COMMANDS", HEADER_COLOR, font_size=18, anchor="left")
    y += ROW_HEIGHT + 10

    for cmd, desc in commands:
        draw_text(canvas, (x, y), cmd, TEXT_COLOR, font_size=16, anchor="left")
        draw_text(canvas, (x + 180, y), desc, MUTED_COLOR, font_size=14, anchor="left")
        y += ROW_HEIGHT

    return y


# =============================================================================
# Mode-Specific Panels
# =============================================================================

def draw_grid_panel(canvas, content_top: float, left: float, padding: float):
    """Draw the Grid mode info panel."""
    col_width = 220
    col1_x = left + padding
    col2_x = col1_x + col_width
    col3_x = col2_x + col_width
    col4_x = col3_x + col_width

    # Column 1: Colors + Letters
    y = draw_colors_section(canvas, col1_x, content_top, "grid", "COLORS")
    y += SECTION_GAP // 2
    draw_letters_section(canvas, col1_x, y)

    # Column 2: Horizontal Styles
    draw_styles_section(canvas, col2_x, content_top, "horizontal_styles", "HORIZ STYLES", is_horizontal=True)

    # Column 3: Vertical Styles
    draw_styles_section(canvas, col3_x, content_top, "vertical_styles", "VERT STYLES", is_horizontal=False)

    # Column 4: Commands
    draw_commands_section(canvas, col4_x, content_top, GRID_COMMANDS)


def draw_boxes_panel(canvas, content_top: float, left: float, padding: float):
    """Draw the Boxes mode info panel."""
    col_width = 280
    col1_x = left + padding
    col2_x = col1_x + col_width + 40

    # Column 1: Colors
    draw_colors_section(canvas, col1_x, content_top, "boxes", "COLORS")

    # Column 2: Commands
    draw_commands_section(canvas, col2_x, content_top, BOXES_COMMANDS)


def draw_circles_panel(canvas, content_top: float, left: float, padding: float):
    """Draw the Circles (clock) mode info panel."""
    col_width = 280
    col1_x = left + padding
    col2_x = col1_x + col_width
    col3_x = col2_x + col_width + 40

    # Column 1: Colors
    draw_colors_section(canvas, col1_x, content_top, "circles", "COLORS")

    # Column 2: Letters
    draw_letters_section(canvas, col2_x, content_top)

    # Column 3: Commands
    draw_commands_section(canvas, col3_x, content_top, CIRCLES_COMMANDS)


# =============================================================================
# Main Entry Point
# =============================================================================

def draw_info_overlay(
    canvas,
    screen_rect: Tuple[float, float, float, float],
):
    """
    Draw the info overlay for the current panel mode.

    Args:
        canvas: Talon canvas object
        screen_rect: (left, top, right, bottom) screen bounds
    """
    left, top, right, bottom = screen_rect
    screen_width = right - left
    screen_height = bottom - top

    padding = 40

    # Draw semi-transparent background
    draw_rect(canvas, (left, top, screen_width, screen_height), BG_COLOR, thickness=0, filled=True)

    # Get current panel info
    panel_mode = get_info_panel_mode()
    panel_index = get_info_panel_index()
    panel_total = get_info_panel_total()

    # Title with mode name and index
    title_y = top + padding
    mode_title = panel_mode.upper()
    draw_text(canvas, (left + padding, title_y), f"{mode_title} MODE", HEADER_COLOR, font_size=24, anchor="left")

    # Edit focus indicator (middle)
    edit_focus = get_info_edit_focus()
    focus_text = f"editing: {edit_focus.upper()}"
    focus_color = ACTIVE_INDICATOR if edit_focus != "colors" else MUTED_COLOR
    draw_text(canvas, ((left + right) / 2, title_y), focus_text, focus_color, font_size=16, anchor="center")

    # Panel indicator on the right
    indicator_text = f"[{panel_index}/{panel_total}]"
    draw_text(canvas, (right - padding, title_y), indicator_text, MUTED_COLOR, font_size=18, anchor="right")

    content_top = title_y + 50

    # Draw the appropriate panel
    if panel_mode == "grid":
        draw_grid_panel(canvas, content_top, left, padding)
    elif panel_mode == "boxes":
        draw_boxes_panel(canvas, content_top, left, padding)
    elif panel_mode == "circles":
        draw_circles_panel(canvas, content_top, left, padding)

    # Footer with navigation hint
    footer_y = bottom - padding
    draw_text(canvas, (left + padding, footer_y), "\"next panel\" / \"previous panel\" to switch  |  \"add/remove <item>\" to configure", MUTED_COLOR, font_size=14, anchor="left")
