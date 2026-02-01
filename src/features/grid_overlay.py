"""
Grid Overlay for MouseClock.

Renders a letter/color grid for precise targeting:
- Y-axis: Letters (A-Z) with horizontal lines
- X-axis: Colors with vertical lines
- Intersections provide target points
"""

from typing import List, Tuple
from ..core.config import get_setting
from ..rendering.colors import get_color
from ..rendering.drawing import draw_line, draw_text, draw_rect


# Default colors for columns (can be configured)
DEFAULT_GRID_COLORS = ["red", "blue", "green", "yellow", "purple"]

# Letters for rows
GRID_LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# Default text styling
DEFAULT_TEXT_COLOR = "00ff00ff"      # Bright green
DEFAULT_TEXT_BG_COLOR = "000000aa"   # Semi-transparent black


def get_text_color() -> str:
    """Get the text color for grid labels."""
    return get_setting("grid_text_color", DEFAULT_TEXT_COLOR)


def get_text_bg_color() -> str:
    """Get the background color for grid labels."""
    return get_setting("grid_text_bg_color", DEFAULT_TEXT_BG_COLOR)

# Grid state - horizontal offset for columns (current and target for animation)
_column_offset_x: float = 0.0
_target_offset_x: float = 0.0

# Grid mode toggle states
_hiss_direction: int = 1      # 1 = right, -1 = left
_shush_mode: int = 1          # 1 = widen, -1 = narrow
_hiss_session_active: bool = False  # Track if we're in a continuous hiss
_shush_session_active: bool = False  # Track if we're in a continuous shush


def get_column_offset() -> float:
    """Get current horizontal offset for columns."""
    return _column_offset_x


def get_target_offset() -> float:
    """Get target horizontal offset for columns."""
    return _target_offset_x


def set_column_offset(offset: float):
    """Set horizontal offset for columns (immediate, no animation)."""
    global _column_offset_x, _target_offset_x
    _column_offset_x = offset
    _target_offset_x = offset


def shift_columns_left(amount: float = 10):
    """Shift columns left by amount pixels (sets target for animation)."""
    global _target_offset_x
    _target_offset_x -= amount


def shift_columns_right(amount: float = 10):
    """Shift columns right by amount pixels (sets target for animation)."""
    global _target_offset_x
    _target_offset_x += amount


def reset_column_offset():
    """Reset column offset to center."""
    global _column_offset_x, _target_offset_x
    _column_offset_x = 0.0
    _target_offset_x = 0.0


def reset_grid_state():
    """Reset all grid state including toggles."""
    global _column_offset_x, _target_offset_x, _hiss_direction, _shush_mode
    global _hiss_session_active, _shush_session_active
    _column_offset_x = 0.0
    _target_offset_x = 0.0
    _hiss_direction = 1
    _shush_mode = 1
    _hiss_session_active = False
    _shush_session_active = False


def end_hiss_session():
    """Call when hiss stops (gap detected) to toggle direction for next session."""
    global _hiss_direction, _hiss_session_active
    if _hiss_session_active:
        old_dir = "right" if _hiss_direction == 1 else "left"
        _hiss_direction *= -1
        new_dir = "right" if _hiss_direction == 1 else "left"
        print(f"🕐 hiss session ended: {old_dir} -> {new_dir}")
        _hiss_session_active = False


def end_shush_session():
    """Call when shush stops (gap detected) to toggle mode for next session."""
    global _shush_mode, _shush_session_active
    if _shush_session_active:
        old_mode = "widen" if _shush_mode == 1 else "narrow"
        _shush_mode *= -1
        new_mode = "widen" if _shush_mode == 1 else "narrow"
        print(f"🕐 shush session ended: {old_mode} -> {new_mode}")
        _shush_session_active = False


def grid_hiss(increment: float):
    """
    Handle hiss in grid mode - shifts columns in current direction.
    Direction toggles only when session ends (gap detected).

    Args:
        increment: Amount to shift (from animator)
    """
    global _hiss_session_active, _target_offset_x

    _hiss_session_active = True
    # Apply shift in current direction
    _target_offset_x += increment * _hiss_direction


def grid_shush(increment: float):
    """
    Handle shush in grid mode - widens or narrows spacing.
    Mode toggles only when session ends (gap detected).

    Args:
        increment: Amount to change (from animator)

    Returns:
        "widen" or "narrow" indicating what action was taken
    """
    global _shush_session_active

    _shush_session_active = True
    # Determine action based on current mode
    if _shush_mode == 1:
        return "widen"
    else:
        return "narrow"


def get_hiss_direction() -> str:
    """Get current hiss direction as string."""
    return "right" if _hiss_direction == 1 else "left"


def get_shush_mode() -> str:
    """Get current shush mode as string."""
    return "widen" if _shush_mode == 1 else "narrow"


def update_offset_animation(lerp_factor: float = 0.2) -> bool:
    """
    Interpolate offset toward target.

    Args:
        lerp_factor: Interpolation factor (0-1)

    Returns:
        True if still animating, False if complete
    """
    global _column_offset_x

    if abs(_column_offset_x - _target_offset_x) < 0.5:
        _column_offset_x = _target_offset_x
        return False

    _column_offset_x += (_target_offset_x - _column_offset_x) * lerp_factor
    return True


def get_grid_colors() -> List[str]:
    """Get the list of colors for grid columns."""
    return get_setting("grid_colors", DEFAULT_GRID_COLORS)


def get_visible_letters(screen_height: float, row_spacing: float) -> List[str]:
    """
    Get letters that fit on screen given spacing.

    Args:
        screen_height: Available height in pixels
        row_spacing: Pixels between rows

    Returns:
        List of letters that fit
    """
    max_rows = int(screen_height / row_spacing)
    return GRID_LETTERS[:min(max_rows, len(GRID_LETTERS))]


def calculate_row_positions(
    screen_top: float,
    screen_bottom: float,
    num_rows: int
) -> List[float]:
    """
    Calculate Y positions for each letter row.

    Args:
        screen_top: Top of screen
        screen_bottom: Bottom of screen
        num_rows: Number of rows to position

    Returns:
        List of Y coordinates for each row
    """
    if num_rows <= 1:
        return [(screen_top + screen_bottom) / 2]

    spacing = (screen_bottom - screen_top) / (num_rows + 1)
    return [screen_top + spacing * (i + 1) for i in range(num_rows)]


def get_column_spacing() -> float:
    """Get spacing between color columns in pixels."""
    return get_setting("grid_column_spacing", 20)


def calculate_column_positions(
    screen_left: float,
    screen_right: float,
    num_cols: int,
    center_x: float = None,
    offset_x: float = None
) -> List[float]:
    """
    Calculate X positions for each color column.

    Args:
        screen_left: Left edge of screen
        screen_right: Right edge of screen
        num_cols: Number of columns to position
        center_x: Center point for columns (defaults to screen center)
        offset_x: Horizontal offset to apply (defaults to global offset)

    Returns:
        List of X coordinates for each column
    """
    spacing = get_column_spacing()

    if center_x is None:
        center_x = (screen_left + screen_right) / 2

    if offset_x is None:
        offset_x = _column_offset_x

    # Calculate total width of all columns
    total_width = spacing * (num_cols - 1)
    start_x = center_x - total_width / 2 + offset_x

    return [start_x + spacing * i for i in range(num_cols)]


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

    if swap_axes:
        # Colors on Y, Letters on X
        row_positions = calculate_row_positions(top, bottom, len(colors))
        col_positions = calculate_column_positions(left, right, len(letters))
        row_labels = colors
        col_labels = letters
    else:
        # Letters on Y, Colors on X (default)
        row_positions = calculate_row_positions(top, bottom, len(letters))
        col_positions = calculate_column_positions(left, right, len(colors))
        row_labels = letters
        col_labels = colors

    # Draw horizontal lines (rows)
    _draw_row_lines(canvas, row_positions, row_labels, left, right, swap_axes)

    # Draw vertical lines (columns)
    _draw_column_lines(canvas, col_positions, col_labels, top, bottom, swap_axes)

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
    top: float,
    bottom: float,
    swap_axes: bool
):
    """Draw vertical lines with labels."""
    label_margin = 25
    text_color = get_text_color()
    bg_color = get_text_bg_color()

    for x, label in zip(positions, labels):
        # Get line color
        if swap_axes:
            # Label is a letter, use white
            line_color = "ffffff99"
        else:
            # Label is a color name
            line_color = get_color(label)

        # Draw the vertical line
        draw_line(canvas, (x, top + label_margin), (x, bottom), line_color, thickness=1)

        # Draw the label at top with background
        label_text = label.capitalize() if not swap_axes else label.upper()
        # Draw background rect
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


def get_grid_target(
    screen_rect: Tuple[float, float, float, float],
    letter: str,
    color: str,
    swap_axes: bool = False
) -> Tuple[float, float]:
    """
    Get the (x, y) position for a letter+color target.

    Args:
        screen_rect: (left, top, right, bottom) screen bounds
        letter: Target letter (A-Z)
        color: Target color name
        swap_axes: If True, colors on Y and letters on X

    Returns:
        (x, y) coordinates of the intersection
    """
    left, top, right, bottom = screen_rect

    colors = get_grid_colors()
    row_spacing = get_setting("grid_row_spacing", 40)
    screen_height = bottom - top
    letters = get_visible_letters(screen_height, row_spacing)

    # Find indices
    letter_upper = letter.upper()
    color_lower = color.lower()

    try:
        letter_idx = letters.index(letter_upper)
    except ValueError:
        letter_idx = 0

    try:
        color_idx = colors.index(color_lower)
    except ValueError:
        color_idx = 0

    if swap_axes:
        row_positions = calculate_row_positions(top, bottom, len(colors))
        col_positions = calculate_column_positions(left, right, len(letters))
        x = col_positions[letter_idx] if letter_idx < len(col_positions) else left
        y = row_positions[color_idx] if color_idx < len(row_positions) else top
    else:
        row_positions = calculate_row_positions(top, bottom, len(letters))
        col_positions = calculate_column_positions(left, right, len(colors))
        x = col_positions[color_idx] if color_idx < len(col_positions) else left
        y = row_positions[letter_idx] if letter_idx < len(row_positions) else top

    return (x, y)
