_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Vertical line overlay components.

Draws color-coded vertical lines for intersection targeting.
Every color can use any of the 18 line styles.

Layout:
    Red     Red     Red     ...     Blue    Blue    Blue    ...
    dash    dot     tick    ...     dash    dot     tick    ...
"""

from typing import List, Tuple, Optional, Literal, Dict

from ...core.config import get_setting, get_mode_config
from ...rendering.drawing import draw_line, LineStyle


# Colors for vertical lines
VERTICAL_COLORS = [
    "ff0000ff",  # red
    "0000ffff",  # blue
    "00ff00ff",  # green
    "ffd700ff",  # yellow
    "800080ff",  # purple
    "ff00ffff",  # pink
    "000000ff",  # black
    "ffffffff",  # white
    "008080ff",  # teal
]

# Color names corresponding to VERTICAL_COLORS
COLOR_NAMES = ["red", "blue", "green", "yellow", "purple", "pink", "black", "white", "teal"]

# All possible line styles (for reference/validation)
ALL_POSSIBLE_STYLES: List[LineStyle] = [
    "dash", "dot", "tick", "blip", "long", "morse",
    "twin", "chain", "wave", "zig", "barb", "rail",
    "cross", "link", "bead", "spike", "hash", "saw",
]


def get_active_styles() -> List[LineStyle]:
    """Get currently active styles from grid mode config."""
    return get_mode_config("grid", "styles")


def get_color_style_map() -> Dict[str, List[LineStyle]]:
    """Get color-to-styles mapping using active styles."""
    styles = get_active_styles()
    return {name: list(styles) for name in COLOR_NAMES}


def get_style_suffixes() -> Dict[str, str]:
    """Get style suffix mapping for active styles."""
    return {style: f" {style}" for style in get_active_styles()}


# For backwards compatibility
LINE_STYLES: List[LineStyle] = ALL_POSSIBLE_STYLES


def get_color_count() -> int:
    """Get number of colors (each color has 18 style variants)."""
    return get_setting("line_overlay_colors", len(COLOR_NAMES))


def get_vertical_count() -> int:
    """Get total number of vertical lines (colors × active styles)."""
    return len(COLOR_NAMES) * len(get_active_styles())


def get_vertical_x_positions(screen_width: float, num_colors: int = None) -> List[Tuple[str, float, str, LineStyle]]:
    """
    Calculate X positions for color-coded vertical lines with style variants.

    Each color gets 3 styles from COLOR_STYLE_MAP.

    Args:
        screen_width: Width of screen in pixels
        num_colors: Number of colors (each gets 3 style variants)

    Returns:
        List of (color_name, x_position, color_hex, line_style) tuples
    """
    if num_colors is None:
        num_colors = get_color_count()

    # Get dynamic style mappings
    color_style_map = get_color_style_map()
    style_suffixes = get_style_suffixes()
    active_styles = get_active_styles()

    print(f"[DEBUG get_vertical_x_positions] num_colors={num_colors}, active_styles={len(active_styles)}, screen_width={screen_width}")

    positions = []
    # Count total lines based on styles per color
    total_lines = sum(len(color_style_map.get(COLOR_NAMES[i], [])) for i in range(num_colors))
    segment_width = screen_width / (total_lines + 1)

    print(f"[DEBUG get_vertical_x_positions] total_lines={total_lines}, segment_width={segment_width:.1f}")

    line_index = 0
    for color_idx in range(num_colors):
        color_name = COLOR_NAMES[color_idx % len(COLOR_NAMES)]
        color_hex = VERTICAL_COLORS[color_idx % len(VERTICAL_COLORS)]
        styles_for_color = color_style_map.get(color_name, active_styles[:3] if active_styles else ["dash"])

        for style in styles_for_color:
            x = segment_width * (line_index + 1)
            # Create full name with style suffix (e.g., "red dash", "blue morse")
            full_name = color_name + style_suffixes.get(style, f" {style}")
            positions.append((full_name, x, color_hex, style))
            line_index += 1

    return positions


def get_x_for_color(color_name: str, screen_width: float, line_style: LineStyle = "dash") -> Optional[float]:
    """
    Get X position for a specific color vertical with optional style.

    Args:
        color_name: Color name (red, blue, etc.)
        screen_width: Width of screen
        line_style: Style for this color (must be one assigned to that color)

    Returns:
        X coordinate or None if invalid color/style
    """
    positions = get_vertical_x_positions(screen_width)

    # Build the full name to search for
    style_suffixes = get_style_suffixes()
    suffix = style_suffixes.get(line_style, f" {line_style}")
    search_name = color_name.lower() + suffix

    for name, x, _, _ in positions:
        if name == search_name:
            return x

    return None


def draw_vertical_line(
    canvas,
    x: float,
    screen_height: float,
    color: str,
    thickness: float = None,
    line_style: LineStyle = "line"
):
    """
    Draw a vertical line from top to bottom.

    Args:
        canvas: Talon canvas object
        x: X coordinate for the line
        screen_height: Height of screen
        color: Line color hex
        thickness: Line thickness
        line_style: One of 19 styles
    """
    if thickness is None:
        thickness = get_setting("line_overlay_thickness", 2)

    print(f"[DEBUG draw_vertical_line] x={x:.0f}, style={line_style}, color={color[:6]}")
    draw_line(canvas, (x, 0), (x, screen_height), color, thickness, line_style=line_style)


def draw_all_verticals(
    canvas,
    screen_width: float,
    screen_height: float,
    thickness: float = None
):
    """
    Draw all color-coded vertical lines with style variants.

    Args:
        canvas: Talon canvas object
        screen_width: Width of screen
        screen_height: Height of screen
        thickness: Line thickness
    """
    positions = get_vertical_x_positions(screen_width)
    print(f"[DEBUG draw_all_verticals] drawing {len(positions)} vertical lines")
    for name, x, color_hex, style in positions:
        print(f"[DEBUG draw_all_verticals] {name}: x={x:.0f}, style={style}")
        draw_vertical_line(canvas, x, screen_height, color_hex, thickness, line_style=style)
