"""
Shared alpha blending utilities for fade animations.

Provides thread-safe alpha state management and color blending.
"""

from typing import Dict
from ...rendering.colors import with_alpha

# Module-level alpha storage keyed by feature name
_alpha_state: Dict[str, int] = {}


def set_alpha(feature: str, alpha: int) -> None:
    """Set the current alpha value for a feature."""
    _alpha_state[feature] = alpha


def get_alpha(feature: str) -> int:
    """Get the current alpha value for a feature (default 255)."""
    return _alpha_state.get(feature, 255)


def apply_alpha(color_hex: str, feature: str = None, alpha: int = None) -> str:
    """
    Apply alpha blending to a color.

    Args:
        color_hex: Hex color string (6 or 8 chars, e.g., "ff0000" or "ff0000aa")
        feature: Feature name to look up alpha (if alpha not provided)
        alpha: Direct alpha value to use (overrides feature lookup)

    Returns:
        Color with alpha applied
    """
    if alpha is None:
        alpha = _alpha_state.get(feature, 255) if feature else 255

    if alpha >= 255:
        return color_hex

    # Blend the existing alpha with fade alpha
    existing_alpha = int(color_hex[6:8], 16) if len(color_hex) >= 8 else 255
    new_alpha = (existing_alpha * alpha) // 255
    return with_alpha(color_hex, new_alpha)
