"""
Talon integration layer for the mouse clock.

This module provides the bridge between Talon voice commands and the core
mouse clock functionality.
"""

# Import all modules to ensure Talon registers the actions
from .adapter import (
    MouseClockTalonAdapter,
    DISPLAY_MODE_CIRCLES,
    DISPLAY_MODE_BOXES,
    DISPLAY_MODE_HYBRID,
    DISPLAY_MODE_GRID,
)
from .instance import (
    get_mouse_clock_instance,
    get_context,
    get_module,
    mod,
    ctx,
)

# Import action modules to register them with Talon
from . import actions  # List declarations and captures
from . import actions_core
from . import actions_move
from . import actions_debug
from . import actions_display
from . import parrot_actions

# Backwards compatibility - re-export from old talon_bridge location
# These can be removed once all imports are updated
