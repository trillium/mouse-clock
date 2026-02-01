"""
Canvas drawing and rendering utilities for the mouse clock.

This module handles all visual rendering of the mouse clock, including
concentric rings, dots, clock letters, and edge-distance visualization.
"""

# Utility functions
from .utils import (
    get_screen_dimensions,
    setup_paint,
    calculate_ring_radius,
    calculate_clock_position,
)

# Ring drawing
from .rings import (
    draw_concentric_rings,
    draw_clock_position_dots,
)

# Edge distance
from .edge import (
    calculate_edge_distance,
    draw_edge_distance_dots,
)

# Main clock rendering
from .clock import (
    draw_clock_letters,
    draw_mouse_clock,
)

__all__ = [
    # utils
    "get_screen_dimensions",
    "setup_paint",
    "calculate_ring_radius",
    "calculate_clock_position",
    # rings
    "draw_concentric_rings",
    "draw_clock_position_dots",
    # edge
    "calculate_edge_distance",
    "draw_edge_distance_dots",
    # clock
    "draw_clock_letters",
    "draw_mouse_clock",
]
