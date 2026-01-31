"""
Configuration and constants for the mouse clock system.

This module centralizes all constants, colors, and configuration values used
throughout the mouse clock application.
"""

# Clock configuration
CLOCK_LETTERS = "abcdefghijkl"

# Radius configuration
DEFAULT_RADIUS = 300
RADIUS_INCREMENT = 20
MIN_RADIUS = 20

# Color names (note: 7 colors including center, not 5 as in original design doc)
COLOR_NAMES = "center red blue green yellow purple pink"

# Color hex values (8-digit RGBA format for Talon/Skia)
COLORS = {
    "GRAY": "9999995f",        # Background color
    "GREEN": "00ff00ff",       # Text color
    "RED": "ff0000ff",         # Dot and active grid color
    "LIGHT_GREEN": "00ff007f", # Cross color
    "BLACK": "000000ff",       # Inactive grid color
    "BLUE": "0000ffff",        # Blue ring color
    "PINK": "ff00ffff",        # Pink ring color
    "ORANGE": "ffa500ff",      # Orange color (unused currently)
    "YELLOW": "FFD700ff",      # Gold-like bright yellow
    "PURPLE": "800080ff",      # Classic purple
    "CENTER": "000000ff",      # Center color (black)
}

# Semantic color aliases
COLOR_BACKGROUND = COLORS["GRAY"]
COLOR_TEXT = COLORS["GREEN"]
COLOR_DOT = COLORS["RED"]
COLOR_CROSS = COLORS["LIGHT_GREEN"]
COLOR_ACTIVE = COLORS["RED"]
COLOR_INACTIVE = COLORS["BLACK"]

# Color lists and mappings
COLOR_LIST = [COLORS[color.upper()] for color in COLOR_NAMES.split() if color.upper() in COLORS]
COLOR_MAP = {color: COLORS[color.upper()] for color in COLOR_NAMES.split()}
COLOR_POS = {color.lower(): index for index, color in enumerate(COLOR_MAP.keys())}

# Screen dimensions fallback
DEFAULT_SCREEN_WIDTH = 1920
DEFAULT_SCREEN_HEIGHT = 1080

# Drawing configuration
DEFAULT_STROKE_WIDTH = 2
DEFAULT_DOT_RADIUS = 5

# =============================================================================
# Settings Management
# =============================================================================

import json
from typing import Any, Dict, Optional
from pathlib import Path

# Default settings registry
_DEFAULTS: Dict[str, Any] = {
    "default_radius": DEFAULT_RADIUS,
    "radius_increment": RADIUS_INCREMENT,
    "min_radius": MIN_RADIUS,
    "debounce_interval_ms": 150,
    "spiral_step_size": 10,
    "spiral_max_radius": 100,
    "line_thickness": DEFAULT_STROKE_WIDTH,
    "dot_radius": DEFAULT_DOT_RADIUS,
    "dashed_line_pattern": [5, 3],
}

# Runtime settings (can be modified)
_settings: Dict[str, Any] = _DEFAULTS.copy()


def get_setting(name: str, default: Any = None) -> Any:
    """
    Retrieve a setting value.

    Args:
        name: Setting name
        default: Fallback if setting not found

    Returns:
        Setting value or default
    """
    if name in _settings:
        return _settings[name]
    if name in _DEFAULTS:
        return _DEFAULTS[name]
    return default


def set_setting(name: str, value: Any):
    """
    Update a setting at runtime.

    Args:
        name: Setting name
        value: New value
    """
    _settings[name] = value


def reset_setting(name: str):
    """
    Restore a setting to its default value.

    Args:
        name: Setting name
    """
    if name in _DEFAULTS:
        _settings[name] = _DEFAULTS[name]
    elif name in _settings:
        del _settings[name]


def reset_all_settings():
    """Restore all settings to defaults."""
    _settings.clear()
    _settings.update(_DEFAULTS)


def get_all_settings() -> Dict[str, Any]:
    """Get copy of all current settings."""
    return _settings.copy()


def load_settings(file_path: str) -> bool:
    """
    Load settings from JSON file.

    Args:
        file_path: Path to settings file

    Returns:
        True if loaded successfully, False otherwise
    """
    try:
        path = Path(file_path)
        if path.exists():
            with open(path, 'r') as f:
                loaded = json.load(f)
                _settings.update(loaded)
            return True
    except Exception:
        pass
    return False


def save_settings(file_path: str) -> bool:
    """
    Persist current settings to JSON file.

    Args:
        file_path: Path to settings file

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(_settings, f, indent=2)
        return True
    except Exception:
        pass
    return False
