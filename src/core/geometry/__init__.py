_V = "0.0.2"; print(f"[v{_V}] {__name__}")
"""
Geometric calculations for the mouse clock system.

This module provides pure mathematical functions for angle conversions,
averaging, and coordinate transformations used in mouse positioning.
"""

_LAZY_IMPORTS = {
    # angles
    'to_radians': '.angles',
    'to_cartesian': '.angles',
    'to_angle': '.angles',
    'normalize_angle': '.angles',
    'opposite_angle': '.angles',
    # clock
    'number_to_angle': '.clock',
    'letter_to_angle': '.clock',
    'angle_to_letter': '.clock',
    'letter_to_position': '.clock',
    'letter_to_clock_angle': '.clock',
    # averaging
    'average_coordinates': '.averaging',
    'average_angles': '.averaging',
    'calculate_mean': '.averaging',
    'average_clock_angles': '.averaging',
    # coordinates
    'move_in_direction': '.coordinates',
    'distance_between': '.coordinates',
    'point_on_circle': '.coordinates',
    'clamp_to_bounds': '.coordinates',
    # intersections
    'ray_line_intersection': '.intersections',
    'ray_circle_intersection': '.intersections',
    'ray_rect_intersection': '.intersections',
    # parallel lines
    'build_parallel_lines': '.parallel_lines',
}

def __getattr__(name):
    if name in _LAZY_IMPORTS:
        from importlib import import_module
        mod = import_module(_LAZY_IMPORTS[name], __name__)
        val = getattr(mod, name)
        globals()[name] = val
        return val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = list(_LAZY_IMPORTS.keys())
