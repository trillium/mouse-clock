"""
Spiral Nudge Navigation.

Provides fine-grained cursor movement in an expanding spiral pattern,
useful for targeting small UI elements near the current cursor position.
"""

import math
from typing import Tuple, Optional
from dataclasses import dataclass

from ..core.config import get_setting


@dataclass
class SpiralState:
    """Tracks current state of spiral navigation."""
    origin: Tuple[float, float]
    current_position: Tuple[float, float]
    step_count: int = 0
    active: bool = False


# Global spiral state
_state = SpiralState(origin=(0, 0), current_position=(0, 0))


def get_step_size() -> float:
    """Get spiral step size in pixels."""
    return get_setting("spiral_step_size", 10)


def get_growth_rate() -> float:
    """Get spiral growth rate (expansion per revolution)."""
    return get_setting("spiral_growth_rate", 5)


def get_max_radius() -> float:
    """Get maximum spiral radius."""
    return get_setting("spiral_max_radius", 100)


def is_clockwise() -> bool:
    """Get spiral direction."""
    return get_setting("spiral_clockwise", True)


def calculate_spiral_point(step: int, origin: Tuple[float, float]) -> Tuple[float, float]:
    """
    Calculate position on Archimedean spiral.

    Args:
        step: Step number (0 = origin)
        origin: Center point of spiral

    Returns:
        (x, y) position on spiral
    """
    if step == 0:
        return origin

    step_size = get_step_size()
    growth_rate = get_growth_rate()
    clockwise = is_clockwise()

    # Archimedean spiral: r = a + b*theta
    # theta increases with each step
    theta = step * 0.5  # Adjust for tighter/looser spiral

    # Radius grows with angle
    radius = step_size + growth_rate * theta

    # Clamp to max radius
    max_radius = get_max_radius()
    if radius > max_radius:
        radius = max_radius

    # Direction
    direction = 1 if clockwise else -1

    # Calculate position
    ox, oy = origin
    x = ox + radius * math.cos(direction * theta)
    y = oy + radius * math.sin(direction * theta)

    return (x, y)


def start_spiral(origin: Tuple[float, float]):
    """
    Start a new spiral navigation from origin.

    Args:
        origin: Starting point (current cursor position)
    """
    global _state
    _state = SpiralState(
        origin=origin,
        current_position=origin,
        step_count=0,
        active=True
    )


def nudge_forward() -> Optional[Tuple[float, float]]:
    """
    Move to next point on spiral.

    Returns:
        New position (x, y) or None if spiral not active
    """
    global _state

    if not _state.active:
        return None

    _state.step_count += 1
    _state.current_position = calculate_spiral_point(_state.step_count, _state.origin)

    return _state.current_position


def nudge_backward() -> Optional[Tuple[float, float]]:
    """
    Move to previous point on spiral.

    Returns:
        New position (x, y) or None if at origin or not active
    """
    global _state

    if not _state.active or _state.step_count <= 0:
        return None

    _state.step_count -= 1
    _state.current_position = calculate_spiral_point(_state.step_count, _state.origin)

    return _state.current_position


def reset_spiral() -> Tuple[float, float]:
    """
    Reset to spiral origin.

    Returns:
        Origin position (x, y)
    """
    global _state

    _state.step_count = 0
    _state.current_position = _state.origin

    return _state.origin


def stop_spiral():
    """Stop spiral navigation."""
    global _state
    _state.active = False


def get_spiral_state() -> SpiralState:
    """Get current spiral state."""
    return _state


def is_spiral_active() -> bool:
    """Check if spiral navigation is active."""
    return _state.active


def get_current_position() -> Tuple[float, float]:
    """Get current position on spiral."""
    return _state.current_position


def get_origin() -> Tuple[float, float]:
    """Get spiral origin."""
    return _state.origin
