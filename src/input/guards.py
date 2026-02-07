"""
Overlay state guards for sound-triggered actions.

Provides guard functions and decorators to ensure actions only
fire when the appropriate overlay is active.
"""

from typing import Optional, Set


class OverlayStateManager:
    """
    Manages overlay activation state.

    Tracks which overlays are currently active and provides
    query methods for guard conditions.
    """

    def __init__(self):
        self._active_overlays: Set[str] = set()

    def set_active(self, overlay_name: str):
        """Mark an overlay as active."""
        self._active_overlays.add(overlay_name)

    def set_inactive(self, overlay_name: str):
        """Mark an overlay as inactive."""
        self._active_overlays.discard(overlay_name)

    def is_overlay_active(self, overlay_name: str) -> bool:
        """
        Check if a specific overlay is showing.

        Args:
            overlay_name: Name of overlay to check

        Returns:
            True if overlay is active
        """
        return overlay_name in self._active_overlays

    def any_overlay_active(self) -> bool:
        """
        Check if any mouse overlay is active.

        Returns:
            True if at least one overlay is active
        """
        return len(self._active_overlays) > 0

    def get_active_overlay(self) -> Optional[str]:
        """
        Get name of currently active overlay.

        Returns:
            Name of first active overlay, or None if none active
        """
        if self._active_overlays:
            return next(iter(self._active_overlays))
        return None

    def get_all_active(self) -> Set[str]:
        """Get set of all active overlay names."""
        return self._active_overlays.copy()

    def clear_all(self):
        """Mark all overlays as inactive."""
        self._active_overlays.clear()


# Global state manager
_state_manager = OverlayStateManager()


def set_overlay_active(overlay_name: str):
    """Mark overlay as active in global state."""
    _state_manager.set_active(overlay_name)


def set_overlay_inactive(overlay_name: str):
    """Mark overlay as inactive in global state."""
    _state_manager.set_inactive(overlay_name)


def is_overlay_active(overlay_name: str) -> bool:
    """Check if specific overlay is active."""
    return _state_manager.is_overlay_active(overlay_name)


def any_overlay_active() -> bool:
    """Check if any overlay is active."""
    return _state_manager.any_overlay_active()


def get_active_overlay() -> Optional[str]:
    """Get name of current active overlay."""
    return _state_manager.get_active_overlay()

