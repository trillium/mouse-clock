"""
Talon captures and actions for mouse clock voice commands.

This module defines the Talon captures that extract clock face letters,
colors, and ordinal multipliers from voice input.
"""

from typing import Any
from talon import Context, Module
from ..core.logger import log_debug

mod = Module()
ctx = Context()

mod.list("clock_face", desc="Clock face positions (a-l)")
mod.list("color", desc="Colors for mouse clock navigation")
mod.list("mouse", desc="The word mouse")
ctx.lists["user.mouse"] = ["mouse"]


@mod.capture(rule="{user.clock_face}")
def clock_face(match) -> str:
    """Capture a single clock face letter"""
    log_debug(f"[clock_face] {match.clock_face}")
    return match.clock_face


@mod.capture(rule="{user.color}")
def color(match) -> str:
    """Capture a color"""
    return match.color


@mod.capture(rule="{user.mouse}")
def mouse(match) -> str:
    """Capture the word mouse"""
    return match.mouse


@mod.capture(rule="({user.mouse} | {user.color} | {user.clock_face} | {user.ordinals})+")
def letters_colors(match) -> list[str]:
    """Capture any number of letters, colors, and ordinal multipliers.

    Ordinals following a letter or color will multiply that item.
    Example: "red third air" -> ["red", "third", "a"]
    """
    return [str(word) for word in match]
