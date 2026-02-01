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
mod.list("line_style", desc="Line styles (solid, dashed, dotted)")
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


@mod.capture(rule="{user.line_style}")
def line_style(match) -> str:
    """Capture a line style (solid, dashed, dotted)"""
    return match.line_style


@mod.capture(rule="[{user.line_style}] ({user.clock_face} | {user.color})")
def styled_target(match) -> str:
    """Capture an optional line style followed by a letter or color.

    Returns: "style:target" or just "target" if no style.
    Example: "dash air" -> "dashed:a", "red" -> "red"
    """
    parts = list(match)
    if len(parts) == 2:
        return f"{parts[0]}:{parts[1]}"
    else:
        return str(parts[0])


@mod.capture(rule="<user.styled_target>+")
def letters_colors(match) -> list[str]:
    """Capture any number of styled targets.

    Each target is optionally preceded by a line style.
    Example: "dash air red" -> ["dashed:a", "red"]
    Example: "dash air dot red" -> ["dashed:a", "dotted:red"]
    """
    return list(match.styled_target_list)
