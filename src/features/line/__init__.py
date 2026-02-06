_V = "0.0.2"; print(f"[v{_V}] {__name__}")
"""
Lettered Line Intersection Overlay.

Divides the screen into horizontal bands labeled with letters,
allowing voice-driven cursor positioning via line intersections.
"""

_LAZY_IMPORTS = {
    # horizontal
    'LineOverlayConfig': '.horizontal',
    'BAND_LETTERS': '.horizontal',
    'get_band_count': '.horizontal',
    'get_band_y_positions': '.horizontal',
    'get_y_for_letter': '.horizontal',
    'draw_horizontal_line': '.horizontal',
    'draw_band_labels': '.horizontal',
    'draw_all_lines': '.horizontal',
    'draw_single_line': '.horizontal',
    # vertical
    'VERTICAL_COLORS': '.vertical',
    'COLOR_NAMES': '.vertical',
    'LINE_STYLES': '.vertical',
    'get_color_count': '.vertical',
    'get_vertical_count': '.vertical',
    'get_vertical_x_positions': '.vertical',
    'get_x_for_color': '.vertical',
    'draw_vertical_line': '.vertical',
    'draw_all_verticals': '.vertical',
    # composite
    'draw_intersection_markers': '.composite',
    'draw_line_with_verticals': '.composite',
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
