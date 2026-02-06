"""
Voice input parsing utilities for mouse clock commands.

Parses letters, colors, and ordinal multipliers from voice input.
"""

from typing import List

from . import config


def flip_letter_to_opposite(letter: str) -> str:
    """
    Flip a clock letter to its opposite position (180 degrees).

    Clock positions:
    A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9, J=10, K=11, L=12

    Opposites (add 6 positions, wrap around):
    A↔G, B↔H, C↔I, D↔J, E↔K, F↔L

    Args:
        letter: A clock letter (a-l, case insensitive)

    Returns:
        The opposite clock letter
    """
    letter_index = config.CLOCK_LETTERS.index(letter.lower())
    opposite_index = (letter_index + 6) % 12
    return config.CLOCK_LETTERS[opposite_index]


def parse_voice_inputs(words: List[str]) -> dict:
    """
    Parse voice input words into letters, colors, directions, and apply ordinal multipliers.

    Words can have "@direction" suffix (e.g., "a@top" or "red@left").
    Ordinals following a letter or color will multiply that item.

    Args:
        words: List of voice command words

    Returns:
        Dictionary with keys 'letters', 'colors', 'directions', 'unknowns'

    Example:
        ["red", "3", "a", "pink"] ->
        {"letters": ["a"], "colors": ["red", "red", "red", "pink"], "directions": [], "unknowns": []}

        ["red@left", "a@top"] ->
        {"letters": ["a"], "colors": ["red"], "directions": ["left", "top"], "unknowns": []}
    """
    letters_list = []
    colors_list = []
    directions_list = []
    unknowns_list = []

    i = 0
    while i < len(words):
        val = str(words[i]).lower()

        # Check for @direction suffix
        direction = None
        if "@" in val:
            val, direction = val.split("@", 1)
            if direction in config.DIRECTIONS:
                directions_list.append(direction)
            else:
                direction = None  # Invalid direction, ignore

        # Check if this is a numeric string (ordinals come through as "1", "2", "3" etc)
        is_ordinal = False
        multiplier = 0
        try:
            multiplier = int(val)
            if 1 <= multiplier <= 99:  # Valid ordinal range
                is_ordinal = True
        except ValueError:
            is_ordinal = False

        if is_ordinal:
            # This is an ordinal - it should apply to the previous item
            # Repeat the last added letter or color that many times
            if letters_list:
                # Repeat the last letter (multiplier - 1) more times
                last_letter = letters_list[-1]
                for _ in range(multiplier - 1):
                    letters_list.append(last_letter)
            elif colors_list:
                # Repeat the last color (multiplier - 1) more times
                last_color = colors_list[-1]
                for _ in range(multiplier - 1):
                    colors_list.append(last_color)

        elif val in config.CLOCK_LETTERS:
            letters_list.append(val)
        elif val == "mouse":
            # "mouse" means center point
            colors_list.append("center")
        elif val == "half":
            # "half" means halfway to screen edge from last color
            colors_list.append("half")
        elif val in config.COLOR_MAP:
            colors_list.append(val)
        elif val:  # Only add non-empty unknowns
            unknowns_list.append(val)

        i += 1

    return {
        "letters": letters_list,
        "colors": colors_list,
        "directions": directions_list,
        "unknowns": unknowns_list
    }
