"""
Centralized color management for mouse clock overlay systems.

Provides a color registry and utilities for looking up, modifying,
and computing colors used across all rendering components.
"""

from typing import Optional


# Color registry mapping names to 8-digit RGBA hex values
COLOR_REGISTRY = {
    "red": "ff0000ff",
    "blue": "0000ffff",
    "green": "00ff00ff",
    "yellow": "ffd700ff",
    "purple": "800080ff",
    "pink": "ff00ffff",
    "gold": "ffa500ff",
    "center": "000000ff",
    "black": "000000ff",
    "white": "ffffffff",
    "gray": "9999995f",
    "light_green": "00ff007f",
}

# Ordered list for ring/box indexing (center is index 0)
COLOR_ORDER = ["center", "red", "blue", "green", "yellow", "purple", "pink"]


def get_color(name: str) -> str:
    """
    Look up hex color by name.

    Args:
        name: Color name (case insensitive)

    Returns:
        8-digit RGBA hex string

    Raises:
        KeyError: If color name not found

    Examples:
        get_color("red") -> "ff0000ff"
        get_color("CENTER") -> "000000ff"
    """
    return COLOR_REGISTRY[name.lower()]


def get_color_index(name: str) -> int:
    """
    Get numeric index for a color (for ring/box ordering).

    Args:
        name: Color name (case insensitive)

    Returns:
        Index in COLOR_ORDER (0 = center, 1 = red, etc.)

    Raises:
        ValueError: If color not in ordering

    Examples:
        get_color_index("center") -> 0
        get_color_index("red") -> 1
        get_color_index("blue") -> 2
    """
    try:
        return COLOR_ORDER.index(name.lower())
    except ValueError:
        raise ValueError(f"Color '{name}' not in ring/box ordering")


def index_to_color(index: int) -> str:
    """
    Reverse lookup from index to color name.

    Args:
        index: Index in COLOR_ORDER

    Returns:
        Color name

    Raises:
        IndexError: If index out of range

    Examples:
        index_to_color(0) -> "center"
        index_to_color(1) -> "red"
    """
    return COLOR_ORDER[index]


def with_alpha(color_hex: str, alpha: int) -> str:
    """
    Modify the alpha channel of a color.

    Args:
        color_hex: 8-digit RGBA hex string
        alpha: New alpha value (0-255)

    Returns:
        Modified 8-digit RGBA hex string

    Examples:
        with_alpha("ff0000ff", 128) -> "ff000080"
        with_alpha("00ff00ff", 0) -> "00ff0000"
    """
    if len(color_hex) != 8:
        raise ValueError(f"Expected 8-digit hex, got '{color_hex}'")
    rgb = color_hex[:6]
    return f"{rgb}{alpha:02x}"


def contrasting_color(color_hex: str) -> str:
    """
    Return a high-contrast color for text/markers on the given background.

    Uses luminance calculation to determine if white or black provides
    better contrast.

    Args:
        color_hex: 8-digit RGBA hex string

    Returns:
        "ffffffff" (white) or "000000ff" (black)

    Examples:
        contrasting_color("000000ff") -> "ffffffff"  # White on black
        contrasting_color("ffffffff") -> "000000ff"  # Black on white
        contrasting_color("ff0000ff") -> "ffffffff"  # White on red
    """
    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)

    # Relative luminance formula (ITU-R BT.709)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b

    return "000000ff" if luminance > 128 else "ffffffff"
