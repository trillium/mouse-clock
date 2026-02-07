"""
Color utilities for mouse clock overlay rendering.

Color definitions live in core/constants.py (single source of truth).
This module re-exports them and provides color manipulation utilities.
"""

from typing import Tuple

from ..core.constants import COLORS, DISPLAY_COLORS  # noqa: F401 — re-export DISPLAY_COLORS

# Derived from COLORS: lowercase-keyed registry for rendering lookups
COLOR_REGISTRY = {k.lower(): v for k, v in COLORS.items()}


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


def parse_hex_color(hex_str: str) -> Tuple[float, float, float, float]:
    """Parse an 8-digit RGBA hex string to (r, g, b, a) floats in 0-1 range."""
    if len(hex_str) != 8:
        raise ValueError(f"Expected 8-char RGBA hex string, got '{hex_str}'")
    r = int(hex_str[0:2], 16) / 255.0
    g = int(hex_str[2:4], 16) / 255.0
    b = int(hex_str[4:6], 16) / 255.0
    a = int(hex_str[6:8], 16) / 255.0
    return (r, g, b, a)


def _linearize(c: float) -> float:
    """Convert sRGB channel value (0-1) to linear RGB."""
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(r: float, g: float, b: float) -> float:
    """Calculate WCAG relative luminance from sRGB values (0-1)."""
    return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)
