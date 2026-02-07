_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Voice actions for per-display-mode configuration.

Allows adding/removing colors, styles, and letters for individual display modes.
"""

from talon import Module
from ..core.config import (
    CONFIGURABLE_MODES,
    get_mode_config,
    set_mode_config,
    add_mode_item,
    remove_mode_item,
    reset_mode_config,
)

mod = Module()


def _get_instance():
    from .instance import get_mouse_clock_instance
    return get_mouse_clock_instance()


def _refresh_if_active():
    """Refresh the display if the clock is currently active."""
    _get_instance().refresh_canvases()


@mod.action_class
class ModeConfigActions:
    def mouse_clock_config_add(mode: str, dimension: str, item: str):
        """Add an item to a display mode's configuration."""
        before = get_mode_config(mode, dimension)
        print(f"[DEBUG] {mode} {dimension} BEFORE add: {len(before)} items")
        if add_mode_item(mode, dimension, item):
            after = get_mode_config(mode, dimension)
            print(f"[DEBUG] {mode} {dimension} AFTER add: {len(after)} items")
            print(f"✓ Added {item} to {mode} {dimension}")
            _refresh_if_active()
        else:
            print(f"✗ Could not add {item} to {mode} {dimension} (already present or invalid)")

    def mouse_clock_config_remove(mode: str, dimension: str, item: str):
        """Remove an item from a display mode's configuration."""
        before = get_mode_config(mode, dimension)
        print(f"[DEBUG] {mode} {dimension} BEFORE remove: {len(before)} items - {before}")
        if remove_mode_item(mode, dimension, item):
            after = get_mode_config(mode, dimension)
            print(f"[DEBUG] {mode} {dimension} AFTER remove: {len(after)} items - {after}")
            print(f"✓ Removed {item} from {mode} {dimension}")
            _refresh_if_active()
        else:
            print(f"✗ Could not remove {item} from {mode} {dimension} (not present)")

    def mouse_clock_config_reset(mode: str, dimension: str):
        """Reset a display mode's dimension to global defaults."""
        reset_mode_config(mode, dimension)
        print(f"Reset {mode} {dimension} to defaults")
        _refresh_if_active()

    def mouse_clock_config_only(mode: str, dimension: str, item: str):
        """Set a display mode's dimension to only a single item."""
        set_mode_config(mode, dimension, [item])
        print(f"Set {mode} {dimension} to only {item}")
        _refresh_if_active()

    def mouse_clock_config_add_all(dimension: str, item: str):
        """Add an item to all configurable modes."""
        for mode in CONFIGURABLE_MODES:
            add_mode_item(mode, dimension, item)
        print(f"Added {item} to all modes {dimension}")
        _refresh_if_active()

    def mouse_clock_config_remove_all(dimension: str, item: str):
        """Remove an item from all configurable modes."""
        for mode in CONFIGURABLE_MODES:
            remove_mode_item(mode, dimension, item)
        print(f"Removed {item} from all modes {dimension}")
        _refresh_if_active()

    def mouse_clock_config_reset_all(dimension: str):
        """Reset a dimension to global defaults for all modes."""
        for mode in CONFIGURABLE_MODES:
            reset_mode_config(mode, dimension)
        print(f"Reset all modes {dimension} to defaults")
        _refresh_if_active()
