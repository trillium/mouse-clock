_V = "0.0.2"; print(f"[v{_V}] {__name__}")
"""
Grid Overlay for MouseClock.

Renders a letter/color grid for precise targeting:
- Y-axis: Letters with horizontal lines
- X-axis: Colors with vertical lines
- Intersections provide target points
"""

_LAZY_IMPORTS = {
    # config
    'DEFAULT_TEXT_COLOR': '.config',
    'DEFAULT_TEXT_BG_COLOR': '.config',
    'get_text_color': '.config',
    'get_text_bg_color': '.config',
    'get_grid_colors': '.config',
    'get_grid_styles': '.config',
    'get_horizontal_styles': '.config',
    'get_vertical_styles': '.config',
    'get_grid_letters': '.config',
    'get_column_spacing': '.config',
    # state
    'get_column_offset': '.state',
    'get_target_offset': '.state',
    'set_column_offset': '.state',
    'shift_columns_left': '.state',
    'shift_columns_right': '.state',
    'reset_column_offset': '.state',
    'reset_grid_state': '.state',
    'end_hiss_session': '.state',
    'end_shush_session': '.state',
    'grid_hiss': '.state',
    'grid_shush': '.state',
    'get_hiss_direction': '.state',
    'get_shush_mode': '.state',
    'update_offset_animation': '.state',
    # layout
    'get_visible_letters': '.layout',
    'calculate_row_positions': '.layout',
    'calculate_column_positions': '.layout',
    # render
    'draw_grid_overlay': '.render',
    # targeting
    'get_grid_target': '.targeting',
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
