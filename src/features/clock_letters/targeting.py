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
    color: str
) -> Tuple[float, float]:
    """
    Get the (x, y) position for a letter+color target.

    Args:
        screen_rect: (left, top, right, bottom) screen bounds
        letter: Target letter (a-l)
        color: Target color name

    Returns:
        (x, y) coordinates of the letter
    """
    left, top, right, bottom = screen_rect
    print(f"[clock_letters targeting] get_clock_letters_target called: letter={letter}, color={color}")

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

    print(f"[clock_letters targeting] result: ({x}, {y})")
    return (x, y)
