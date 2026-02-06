_V = "0.0.2"; print(f"[v{_V}] {__name__}")
"""
Concentric Box Targeting Overlay.

Renders axis-aligned rectangular boxes centered at cursor,
each with distinct color for targeting via voice commands.
"""

_LAZY_IMPORTS = {
    # config
    'get_box_count': '.config',
    'get_box_spacing': '.config',
    'get_progression_mode': '.config',
    'calculate_box_sizes': '.config',
    'get_box_colors': '.config',
    # render
    'draw_concentric_boxes': '.render',
    'get_ray_length': '.render',
    'draw_directional_rays': '.render',
    'draw_intersection_markers': '.render',
    'draw_boxes_with_guides': '.render',
    # targeting
    'get_size_for_color': '.targeting',
    'get_target_position': '.targeting',
    'get_target_from_letter': '.targeting',
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
