"""
Singleton instance management for MouseClockTalonAdapter.

Also sets up the Talon module and context for mouse clock.
"""

import time
from talon import Context, Module

from .adapter import MouseClockTalonAdapter
from ..core.logger import log_info

# Module and context setup
mod = Module()
mod.tag("use_mouse_clock", desc="Tag enables using mouse clock")
mod.tag("mouse_clock_showing", desc="Tag indicates whether the mouse clock is showing")
mod.tag("mouse_clock_info_mode", desc="Tag indicates info panel is active (for command overrides)")

# Context for lists (requires use_mouse_clock)
ctx = Context()
ctx.lists["user.mouse"] = ["mouse"]
ctx.matches = r"""
tag: user.use_mouse_clock
"""

# Separate context for dynamic tags - NO matches clause so tags are always active when set
ctx_tags = Context()

# Global instance - using factory function for better control
_mouse_clock_instance = None


def get_mouse_clock_instance() -> MouseClockTalonAdapter:
    """Get the global mouse clock instance, recreating on module reload."""
    global _mouse_clock_instance
    # Recreate instance if adapter class changed (module was reloaded)
    if _mouse_clock_instance is not None:
        if type(_mouse_clock_instance) is not MouseClockTalonAdapter:
            log_info("Adapter class changed - recreating MouseClockTalonAdapter instance")
            # Close old instance to clean up canvases
            try:
                _mouse_clock_instance.close()
            except Exception:
                pass
            _mouse_clock_instance = None
    if _mouse_clock_instance is None:
        _mouse_clock_instance = MouseClockTalonAdapter()
    return _mouse_clock_instance


def get_context() -> Context:
    """Get the mouse clock context."""
    return ctx


def get_module() -> Module:
    """Get the mouse clock module."""
    return mod
