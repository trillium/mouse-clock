"""
Clock letters overlay configuration.

Gets active letters and colors from mode config.
"""

from typing import List
from ...core.config import get_mode_config, get_setting, set_setting
from ...core.constants import DEFAULT_TEXT_COLOR, DEFAULT_TEXT_BG_COLOR
from .column_presets import (
    get_preset_column_types, PRESET_NAMES, PRESETS,
)


def get_text_color() -> str:
    """Get the text color for clock letter labels."""
    return get_setting("clock_letters_text_color", DEFAULT_TEXT_COLOR)


def get_text_bg_color() -> str:
    """Get the background color for clock letter labels."""
    return get_setting("clock_letters_text_bg_color", DEFAULT_TEXT_BG_COLOR)


def get_clock_letters_colors() -> List[str]:
    """Get the list of active colors (columns)."""
    return get_mode_config("clock_letters", "colors")


def get_clock_letters_letters() -> List[str]:
    """Get the list of active letters (rows)."""
    return get_mode_config("clock_letters", "letters")


def get_column_types() -> List[str]:
    """Get renderer type per color column. 'letters' or 'line'.

    Priority:
    1. Raw list override via clock_letters_column_types setting
    2. Named preset via clock_letters_column_preset setting
    3. Default: 'reference' preset
    """
    # Raw list override takes priority
    types = get_setting("clock_letters_column_types")
    if types is not None:
        return types

    # Named preset
    preset_name = get_setting("clock_letters_column_preset", "reference")
    n = len(get_clock_letters_colors())
    return get_preset_column_types(preset_name, n)


def get_current_preset() -> str:
    """Get the current preset name (or 'reference' default)."""
    return get_setting("clock_letters_column_preset", "reference")


def set_column_preset(preset_name: str):
    """Set column layout to a named preset and persist it.

    Also clears any raw column_types override so the preset takes effect.
    """
    if preset_name not in PRESETS:
        raise ValueError(f"Unknown preset: {preset_name!r}. "
                         f"Available: {PRESET_NAMES}")
    set_setting("clock_letters_column_preset", preset_name, persist=True)
    # Clear raw override so preset is used
    set_setting("clock_letters_column_types", None, persist=True)


def cycle_column_preset() -> str:
    """Cycle to the next preset. Returns the new preset name."""
    current = get_current_preset()
    try:
        idx = PRESET_NAMES.index(current)
        next_idx = (idx + 1) % len(PRESET_NAMES)
    except ValueError:
        next_idx = 0
    new_preset = PRESET_NAMES[next_idx]
    set_column_preset(new_preset)
    return new_preset
