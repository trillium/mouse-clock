"""
Clock notation conversions for the mouse clock system.

Functions for converting between clock hours (1-12), letters (A-L),
and angles in degrees.
"""

from .angles import normalize_angle


def number_to_angle(hour: int) -> float:
    """
    Convert a clock hour (1-12) to degrees.

    Clock hours map to angles: 1=30°, 2=60°, 3=90°, ..., 12=0°/360°.

    Args:
        hour: Clock hour from 1 to 12

    Returns:
        Angle in degrees

    Examples:
        number_to_angle(1) -> 30
        number_to_angle(3) -> 90
        number_to_angle(12) -> 0
    """
    return (hour * 30) % 360


def letter_to_angle(letter: str) -> float:
    """
    Convert a clock letter (A-L) to degrees.

    Clock letters map to angles: A=30°, B=60°, C=90°, ..., L=0°/360°.

    Args:
        letter: Clock letter A-L (case insensitive)

    Returns:
        Angle in degrees

    Examples:
        letter_to_angle('A') -> 30
        letter_to_angle('C') -> 90
        letter_to_angle('L') -> 0
    """
    position = ord(letter.upper()) - ord("A") + 1
    return (position * 30) % 360


def angle_to_letter(degrees: float) -> str:
    """
    Return the nearest clock letter for any angle.

    Maps angles to the nearest of 12 clock positions (A-L).

    Args:
        degrees: Angle in degrees

    Returns:
        Nearest clock letter (A-L)

    Examples:
        angle_to_letter(30) -> 'A'
        angle_to_letter(45) -> 'B' (rounds to nearest)
        angle_to_letter(0) -> 'L'
        angle_to_letter(350) -> 'L'
    """
    normalized = normalize_angle(degrees)
    # Each letter spans 30 degrees, centered on its position
    # A is centered at 30°, B at 60°, etc.
    # Round to nearest 30-degree increment
    position = round(normalized / 30)
    if position == 0 or position == 12:
        return "L"
    return chr(ord("A") + position - 1)


def letter_to_position(letter: str) -> int:
    """
    Return the position of a letter in the alphabet (1-indexed).

    Args:
        letter: A letter A-Z (case insensitive)

    Returns:
        Position number (A=1, B=2, ..., Z=26)
    """
    return ord(letter.upper()) - ord("A") + 1


def letter_to_clock_angle(letter_position: int) -> float:
    """
    Given a letter position (1-12 for A-L), return the corresponding clock angle in degrees.

    Args:
        letter_position: Position of letter (1=A at 12 o'clock, 2=B, ..., 12=L)

    Returns:
        Angle in degrees (0° = 3 o'clock, 90° = 6 o'clock, -90° = 12 o'clock)

    Examples:
        1 (A) at 12 o'clock -> 30° (after modulo)
        4 (D) at 3 o'clock  -> 120° (after modulo)
    """
    return (30 * letter_position) % 360
