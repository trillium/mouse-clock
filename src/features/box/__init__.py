"""
Concentric Box Targeting Overlay.

Renders axis-aligned rectangular boxes centered at cursor,
each with distinct color for targeting via voice commands.
"""

# Configuration
from .config import (
    get_box_count,
    get_box_spacing,
    get_progression_mode,
    calculate_box_sizes,
    get_box_colors,
)

# Rendering
from .render import (
    draw_concentric_boxes,
    get_ray_length,
    draw_directional_rays,
    draw_intersection_markers,
    draw_boxes_with_guides,
)

# Targeting
from .targeting import (
    get_size_for_color,
    get_target_position,
    get_target_from_letter,
)

__all__ = [
    # config
    "get_box_count",
    "get_box_spacing",
    "get_progression_mode",
    "calculate_box_sizes",
    "get_box_colors",
    # render
    "draw_concentric_boxes",
    "get_ray_length",
    "draw_directional_rays",
    "draw_intersection_markers",
    "draw_boxes_with_guides",
    # targeting
    "get_size_for_color",
    "get_target_position",
    "get_target_from_letter",
]
