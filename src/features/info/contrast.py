_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
WCAG contrast ratio utilities.

Pure-function module (no Talon dependencies) for calculating
color contrast ratios per WCAG 2.1 guidelines.
"""

from typing import Tuple


def parse_hex_color(hex_str: str) -> Tuple[float, float, float, float]:
    """Parse an 8-digit RGBA hex string to (r, g, b, a) floats in 0-1 range."""
    if len(hex_str) != 8:
        raise ValueError(f"Expected 8-char RGBA hex string, got '{hex_str}'")
    r = int(hex_str[0:2], 16) / 255.0
    g = int(hex_str[2:4], 16) / 255.0
    b = int(hex_str[4:6], 16) / 255.0
    a = int(hex_str[6:8], 16) / 255.0
    return (r, g, b, a)


def blend_alpha(
    fg_rgba: Tuple[float, float, float, float],
    bg_rgba: Tuple[float, float, float, float],
) -> Tuple[float, float, float]:
    """Alpha-composite foreground over background, returning opaque (r, g, b)."""
    fr, fg, fb, fa = fg_rgba
    br, bg_, bb, ba = bg_rgba
    # Composite: fg over bg (both may have alpha)
    out_a = fa + ba * (1 - fa)
    if out_a == 0:
        return (0.0, 0.0, 0.0)
    out_r = (fr * fa + br * ba * (1 - fa)) / out_a
    out_g = (fg * fa + bg_ * ba * (1 - fa)) / out_a
    out_b = (fb * fa + bb * ba * (1 - fa)) / out_a
    return (out_r, out_g, out_b)


def _linearize(c: float) -> float:
    """Convert sRGB channel value (0-1) to linear RGB."""
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(r: float, g: float, b: float) -> float:
    """Calculate WCAG relative luminance from linear sRGB values (0-1)."""
    return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)


def contrast_ratio(
    color1_rgb: Tuple[float, float, float],
    color2_rgb: Tuple[float, float, float],
) -> float:
    """Calculate WCAG contrast ratio between two opaque RGB colors."""
    l1 = relative_luminance(*color1_rgb)
    l2 = relative_luminance(*color2_rgb)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def check_aa(fg_hex: str, bg_hex: str, font_size: float = 14.0) -> bool:
    """Check if a foreground/background pair passes WCAG AA.

    Large text (>=18pt) requires ratio >= 3:1.
    Normal text (<18pt) requires ratio >= 4.5:1.
    """
    fg_rgba = parse_hex_color(fg_hex)
    bg_rgba = parse_hex_color(bg_hex)
    fg_rgb = blend_alpha(fg_rgba, bg_rgba)
    bg_rgb = (bg_rgba[0], bg_rgba[1], bg_rgba[2])
    ratio = contrast_ratio(fg_rgb, bg_rgb)
    threshold = 3.0 if font_size >= 18 else 4.5
    return ratio >= threshold
