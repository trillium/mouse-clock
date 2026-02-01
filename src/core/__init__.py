"""
Core mouse clock logic, independent of Talon.

This module contains the core business logic for the mouse clock system,
including configuration, geometry calculations, and mouse positioning.
"""

from .animation import RadiusAnimator, exponential_lerp_factor
from .voice_parsing import flip_letter_to_opposite, parse_voice_inputs
from .mouse_clock import MouseClockCore
