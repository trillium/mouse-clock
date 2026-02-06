"""
Configuration and constants for the mouse clock system.

This module centralizes all constants, colors, and configuration values used
throughout the mouse clock application.
"""

# Clock configuration
CLOCK_LETTERS = "abcdefghijkl"

# Radius configuration
DEFAULT_RADIUS = 300
RADIUS_INCREMENT = 5
MIN_RADIUS = 20

# Color names (note: 7 colors including center, not 5 as in original design doc)
COLOR_NAMES = "center red blue green yellow purple pink black white teal"

# Color hex values (8-digit RGBA format for Talon/Skia)
COLORS = {
    "GRAY": "9999995f",        # Background color
    "GREEN": "00ff00ff",       # Text color
    "RED": "ff0000ff",         # Dot and active grid color
    "LIGHT_GREEN": "00ff007f", # Cross color
    "BLACK": "000000ff",       # Black
    "WHITE": "ffffffff",       # White
    "TEAL": "008080ff",        # Teal
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

# Default settings file path (in the mouse-clock directory)
_SETTINGS_FILE = Path(__file__).parent.parent / "settings.json"

# All available line styles
# Disabled: morse, barb, spike, saw (asymmetric), zig, wave
ALL_LINE_STYLES = [
    "solid", "dash", "dot", "tick", "blip", "long",
    "twin", "chain", "rail", "cross", "link", "bead", "hash",
]

# All available color names (excluding "center" which is a special position)
ALL_COLORS = ["red", "blue", "green", "yellow", "purple", "pink", "black", "white", "teal"]

# All available letters
ALL_LETTERS = list("abcdefghijkl")

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
    "active_colors": list(ALL_COLORS),
    "active_styles": list(ALL_LINE_STYLES),
    "active_letters": list(ALL_LETTERS),
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


def _auto_save():
    """Save settings to the default file (called after mode config changes)."""
    save_settings(str(_SETTINGS_FILE))


def load_default_settings() -> bool:
    """Load settings from the default file on startup."""
    return load_settings(str(_SETTINGS_FILE))


# =============================================================================
# Active Configuration Accessors
# =============================================================================

def get_active_colors() -> list:
    """Get the list of currently active color names."""
    return get_setting("active_colors", ALL_COLORS)


def get_active_styles() -> list:
    """Get the list of currently active line style names."""
    return get_setting("active_styles", ALL_LINE_STYLES)


def get_active_letters() -> list:
    """Get the list of currently active letters."""
    return get_setting("active_letters", ALL_LETTERS)


# =============================================================================
# Per-Display-Mode Configuration
# =============================================================================

CONFIGURABLE_MODES = ["circles", "boxes", "grid", "clock_letters"]

# Info panel modes (which mode's config/commands to display)
INFO_PANEL_MODES = ["grid", "boxes", "circles"]

# Map dimension names to their global getter and validation set
_DIMENSION_INFO = {
    "colors": {"global_key": "active_colors", "all_items": ALL_COLORS},
    "styles": {"global_key": "active_styles", "all_items": ALL_LINE_STYLES},
    "horizontal_styles": {"global_key": "active_styles", "all_items": ALL_LINE_STYLES},
    "vertical_styles": {"global_key": "active_styles", "all_items": ALL_LINE_STYLES},
    "letters": {"global_key": "active_letters", "all_items": ALL_LETTERS},
}


def _mode_key(mode: str, dimension: str) -> str:
    """Build the settings key for a per-mode dimension."""
    return f"{mode}_active_{dimension}"


def get_mode_config(mode: str, dimension: str) -> list:
    """Get the active items for a mode+dimension, falling back to global.

    Args:
        mode: One of CONFIGURABLE_MODES
        dimension: "colors", "styles", or "letters"

    Returns:
        List of active items for this mode, or the global list if no override.
    """
    key = _mode_key(mode, dimension)
    per_mode = get_setting(key)
    if per_mode is not None:
        return list(per_mode)
    info = _DIMENSION_INFO.get(dimension)
    if info:
        return list(get_setting(info["global_key"], info["all_items"]))
    return []


def set_mode_config(mode: str, dimension: str, items: list):
    """Set the full list of active items for a mode+dimension.

    Args:
        mode: One of CONFIGURABLE_MODES
        dimension: "colors", "styles", or "letters"
        items: The new list of items
    """
    set_setting(_mode_key(mode, dimension), list(items))
    _auto_save()


def add_mode_item(mode: str, dimension: str, item: str) -> bool:
    """Add an item to a mode's dimension list (copy-on-write from global).

    Validates against the full set of allowed items for this dimension.

    Args:
        mode: One of CONFIGURABLE_MODES
        dimension: "colors", "styles", or "letters"
        item: Item to add

    Returns:
        True if added, False if invalid or already present.
    """
    info = _DIMENSION_INFO.get(dimension)
    if not info or item not in info["all_items"]:
        return False
    current = get_mode_config(mode, dimension)
    if item in current:
        return False
    current.append(item)
    set_mode_config(mode, dimension, current)
    return True


def remove_mode_item(mode: str, dimension: str, item: str) -> bool:
    """Remove an item from a mode's dimension list (copy-on-write from global).

    Args:
        mode: One of CONFIGURABLE_MODES
        dimension: "colors", "styles", or "letters"
        item: Item to remove

    Returns:
        True if removed, False if not present.
    """
    current = get_mode_config(mode, dimension)
    if item not in current:
        return False
    current.remove(item)
    set_mode_config(mode, dimension, current)
    return True


def reset_mode_config(mode: str, dimension: str):
    """Delete the per-mode override, restoring fallback to global.

    Args:
        mode: One of CONFIGURABLE_MODES
        dimension: "colors", "styles", or "letters"
    """
    key = _mode_key(mode, dimension)
    if key in _settings:
        del _settings[key]
        _auto_save()


# =============================================================================
# Info Panel State
# =============================================================================

# Edit focus modes for the info panel
INFO_EDIT_FOCUSES = ["colors", "horizontal", "vertical"]


def get_info_panel_mode() -> str:
    """Get the currently displayed info panel mode."""
    return get_setting("info_panel_mode", INFO_PANEL_MODES[0])


def get_info_edit_focus() -> str:
    """Get the current edit focus (colors, horizontal, or vertical)."""
    return get_setting("info_edit_focus", "colors")


def set_info_edit_focus(focus: str):
    """Set the edit focus for add/remove commands."""
    if focus in INFO_EDIT_FOCUSES:
        set_setting("info_edit_focus", focus)
        # Don't auto-save - this is session state, not persistent config


def set_info_panel_mode(mode: str):
    """Set which mode's info panel to display."""
    if mode in INFO_PANEL_MODES:
        set_setting("info_panel_mode", mode)
        _auto_save()


def cycle_info_panel_next() -> str:
    """Cycle to the next info panel mode. Returns the new mode."""
    current = get_info_panel_mode()
    try:
        idx = INFO_PANEL_MODES.index(current)
        next_idx = (idx + 1) % len(INFO_PANEL_MODES)
    except ValueError:
        next_idx = 0
    new_mode = INFO_PANEL_MODES[next_idx]
    set_info_panel_mode(new_mode)
    return new_mode


def cycle_info_panel_previous() -> str:
    """Cycle to the previous info panel mode. Returns the new mode."""
    current = get_info_panel_mode()
    try:
        idx = INFO_PANEL_MODES.index(current)
        prev_idx = (idx - 1) % len(INFO_PANEL_MODES)
    except ValueError:
        prev_idx = 0
    new_mode = INFO_PANEL_MODES[prev_idx]
    set_info_panel_mode(new_mode)
    return new_mode


def get_info_panel_index() -> int:
    """Get the 1-based index of the current info panel (for display)."""
    current = get_info_panel_mode()
    try:
        return INFO_PANEL_MODES.index(current) + 1
    except ValueError:
        return 1


def get_info_panel_total() -> int:
    """Get the total number of info panels."""
    return len(INFO_PANEL_MODES)
