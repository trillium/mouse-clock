"""Dense grid overlay feature."""

_LAZY_IMPORTS = {
    'draw_dense_grid_overlay': '.render',
    'get_dense_grid_target': '.targeting',
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
