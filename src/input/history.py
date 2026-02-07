"""
Position history stack for navigation systems.

Provides undo/reset functionality by tracking cursor positions
for MouseClock go_back and Spiral Nudge reset operations.
"""

from typing import Tuple, Optional, List


class PositionHistory:
    """
    Stack-based position history tracker.

    Maintains a history of cursor positions for undo operations
    and tracks the session origin for reset functionality.
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize position history.

        Args:
            max_size: Maximum positions to store (oldest dropped when exceeded)
        """
        self._stack: List[Tuple[float, float]] = []
        self._origin: Optional[Tuple[float, float]] = None
        self._max_size = max_size

    def push_position(self, position: Tuple[float, float]):
        """
        Add position to history stack.

        Args:
            position: Position (x, y) to store
        """
        # Set origin on first push
        if self._origin is None:
            self._origin = position

        self._stack.append(position)

        # Trim if exceeded max size
        if len(self._stack) > self._max_size:
            self._stack = self._stack[-self._max_size:]

    def pop_position(self) -> Optional[Tuple[float, float]]:
        """
        Remove and return last position.

        Returns:
            Last position (x, y) or None if empty
        """
        if self._stack:
            return self._stack.pop()
        return None

    def peek_position(self) -> Optional[Tuple[float, float]]:
        """
        View last position without removing.

        Returns:
            Last position (x, y) or None if empty
        """
        if self._stack:
            return self._stack[-1]
        return None

    def clear_history(self):
        """Clear all stored positions and reset origin."""
        self._stack.clear()
        self._origin = None

    def get_origin(self) -> Optional[Tuple[float, float]]:
        """
        Get starting position for current session.

        Returns:
            Origin position (x, y) or None if no history
        """
        return self._origin

    def set_origin(self, position: Tuple[float, float]):
        """
        Explicitly set the session origin.

        Args:
            position: Position (x, y) to use as origin
        """
        self._origin = position

    def __len__(self) -> int:
        """Return number of positions in history."""
        return len(self._stack)

    def is_empty(self) -> bool:
        """Check if history is empty."""
        return len(self._stack) == 0
