"""
Singleton instance management for MouseClockTalonAdapter.

Also sets up the Talon module and context for mouse clock.
"""

import time
from talon import Context, Module

from .adapter import MouseClockTalonAdapter
from ..core.logger import log_info

# Module and context setup
ctx = Context()
ctx.lists["user.mouse"] = ["mouse"]

mod = Module()
mod.tag("use_mouse_clock", desc="Tag enables using mouse clock")
mod.tag("mouse_clock_showing", desc="Tag indicates whether the mouse clock is showing")

# Only use if tag is active
ctx.matches = r"""
tag: user.use_mouse_clock
"""

# Global instance - using factory function for better control
_mouse_clock_instance = None
_module_load_time = time.time()  # Track when module loaded


def get_mouse_clock_instance() -> MouseClockTalonAdapter:
    """Get the global mouse clock instance, recreating on module reload."""
    global _mouse_clock_instance
    # Recreate instance if module was reloaded (stale instance)
    if _mouse_clock_instance is not None:
        if not hasattr(_mouse_clock_instance, '_created_at') or _mouse_clock_instance._created_at < _module_load_time:
            log_info("Module reloaded - recreating MouseClockTalonAdapter instance")
            _mouse_clock_instance = None
    if _mouse_clock_instance is None:
        _mouse_clock_instance = MouseClockTalonAdapter()
        _mouse_clock_instance._created_at = _module_load_time
    return _mouse_clock_instance


def get_context() -> Context:
    """Get the mouse clock context."""
    return ctx


def get_module() -> Module:
    """Get the mouse clock module."""
    return mod
