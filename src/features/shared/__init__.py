_V = "0.0.2"; print(f"[v{_V}] {__name__}")
"""
Shared utilities for feature modules.

Common functions extracted from grid, clock_letters, and box features.
"""

_LAZY_IMPORTS = {
    'calculate_row_positions': '.layout',
    'calculate_column_positions': '.layout',
    'apply_alpha': '.alpha',
    'set_alpha': '.alpha',
    'get_alpha': '.alpha',
    'safe_index': '.utils',
    'safe_index_or_none': '.utils',
    'DEFAULT_TEXT_COLOR': '.config',
    'DEFAULT_TEXT_BG_COLOR': '.config',
}

def __getattr__(name):
    if name in _LAZY_IMPORTS:
        from importlib import import_module
        mod = import_module(_LAZY_IMPORTS[name], __name__)
        val = getattr(mod, name)
        globals()[name] = val
        return val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
