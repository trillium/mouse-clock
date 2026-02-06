"""
Clock letters targeting functions.

Calculate target positions from letter+color combinations.
"""

print("reloaded clock_letters/targeting.py")

from typing import Tuple

from .config import get_clock_letters_colors, get_clock_letters_letters
from .layout import calculate_row_positions, calculate_column_positions


def get_clock_letters_target(
    screen_rect: Tuple[float, float, float, float],
    letter: str,
    color: str,
    directions: list = None
) -> Tuple[float, float]:
    """
    Get the (x, y) position for a letter+color target.

    Args:
        screen_rect: (left, top, right, bottom) screen bounds
        letter: Target letter (a-z)
        color: Target color name
        directions: Optional list of offset directions (top, bottom, left, right)
                   Multiple directions combine (e.g., ["top", "left"] = top-left corner)

    Returns:
        (x, y) coordinates of the target
    """
    left, top, right, bottom = screen_rect
    print(f"[clock_letters targeting] get_clock_letters_target called: letter={letter}, color={color}, directions={directions}")

    colors = get_clock_letters_colors()
    letters = get_clock_letters_letters()
    print(f"[clock_letters targeting] colors={colors}, letters={letters}")

    # Find indices
    letter_lower = letter.lower()
    color_lower = color.lower()

    try:
        letter_idx = letters.index(letter_lower)
    except ValueError:
        letter_idx = 0
        print(f"[clock_letters targeting] WARNING: letter '{letter_lower}' not found, using idx 0")

    try:
        color_idx = colors.index(color_lower)
    except ValueError:
        color_idx = 0
        print(f"[clock_letters targeting] WARNING: color '{color_lower}' not found, using idx 0")

    print(f"[clock_letters targeting] letter_idx={letter_idx}, color_idx={color_idx}")

    row_positions = calculate_row_positions(top, bottom, len(letters))
    col_positions = calculate_column_positions(left, right, len(colors))

    x = col_positions[color_idx] if color_idx < len(col_positions) else left
    y = row_positions[letter_idx] if letter_idx < len(row_positions) else top

    # Apply directional offsets (can combine multiple)
    if directions:
        # Calculate cell spacing for offset
        row_spacing = (bottom - top) / (len(letters) + 1)
        col_spacing = (right - left) / (len(colors) + 1)
        # Offset by ~40% of cell size to get near edge but not at boundary
        offset_factor = 0.4

        for direction in directions:
            if direction == 'top':
                y -= row_spacing * offset_factor
            elif direction == 'bottom':
                y += row_spacing * offset_factor
            elif direction == 'left':
                x -= col_spacing * offset_factor
            elif direction == 'right':
                x += col_spacing * offset_factor

        print(f"[clock_letters targeting] applied directions: {directions}")

    print(f"[clock_letters targeting] result: ({x}, {y})")
    return (x, y)
