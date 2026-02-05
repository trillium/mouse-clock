"""
Talon integration layer for the mouse clock.

This module provides the bridge between Talon voice commands and the core
mouse clock functionality.
"""

# Load saved settings on startup (before other imports that may use config)
from ..core.config import load_default_settings
if load_default_settings():
    print("mouse-clock: loaded settings from settings.json")

# Import all modules to ensure Talon registers the actions
from .adapter import (
    MouseClockTalonAdapter,
    DISPLAY_MODE_CIRCLES,
    DISPLAY_MODE_BOXES,
    DISPLAY_MODE_GRID,
    DISPLAY_MODE_INFO,
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
from . import actions_mode_config
from . import parrot_actions

# Backwards compatibility - re-export from old talon_bridge location
# These can be removed once all imports are updated
