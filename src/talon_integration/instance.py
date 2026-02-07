"""
Singleton instance management for MouseClockTalonAdapter.

Also sets up the Talon module and context for mouse clock.

NOTE: Imports from .adapter and ..core.logger are deferred to function
bodies to prevent Talon cold-start [ ] cascade.
"""

import time
from talon import Context, Module

# Module and context setup
mod = Module()
mod.tag("use_mouse_clock", desc="Tag enables using mouse clock")
mod.tag("mouse_clock_showing", desc="Tag indicates whether the mouse clock is showing")

# Context for lists (requires use_mouse_clock)
ctx = Context()
ctx.lists["user.mouse"] = ["mouse"]
ctx.matches = r"""
tag: user.use_mouse_clock
"""

# Note: ctx_tags for dynamic tag management is now in actions_core.py
# This follows the Talon pattern of keeping Context in same file as actions that modify it

# Global instance - using factory function for better control
_mouse_clock_instance = None


def get_mouse_clock_instance():
    """Get the global mouse clock instance, recreating on module reload."""
    from .adapter import MouseClockTalonAdapter
    from ..core.logger import log_info
    global _mouse_clock_instance
    # Recreate instance if adapter class changed (module was reloaded)
    if _mouse_clock_instance is not None:
        if type(_mouse_clock_instance) is not MouseClockTalonAdapter:
            log_info("Adapter class changed - recreating MouseClockTalonAdapter instance")
            # Close old instance to clean up canvases
            old_instance = _mouse_clock_instance
            _mouse_clock_instance = None
            try:
                # Force close canvases directly if close() fails
                if hasattr(old_instance, 'canvases') and old_instance.canvases:
                    for c in old_instance.canvases:
                        try:
                            c.unregister("draw", old_instance.draw)
                        except Exception:
                            pass
                        try:
                            c.close()
                        except Exception:
                            pass
                old_instance.close()
            except Exception as e:
                log_info(f"Error closing old instance: {e}")
    if _mouse_clock_instance is None:
        _mouse_clock_instance = MouseClockTalonAdapter()
    return _mouse_clock_instance


def get_context() -> Context:
    """Get the mouse clock context."""
    return ctx


def get_module() -> Module:
    """Get the mouse clock module."""
    return mod
