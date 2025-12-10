import math
from typing import Any

from talon import Context, Module

mod = Module()
ctx = Context()

mod.list("clock_face", desc="Clock face positions (a-l)")
mod.list("color", desc="Colors for mouse clock navigation")
mod.list("mouse", desc="The word mouse")
ctx.lists["user.mouse"] = ["mouse"]

@mod.capture(rule="{user.clock_face}")
def clock_face(m) -> str:
    """Capture a single clock face letter"""
    print("[clock_face]", m.clock_face)
    return m.clock_face

@mod.capture(rule="{user.color}")
def color(m) -> str:
    """Capture a color"""
    return m.color

@mod.capture(rule="{user.mouse}")
def mouse(m) -> str:
    """Capture the word mouse"""
    return m.mouse

@mod.capture(rule="({user.mouse} | {user.color} | {user.clock_face} | {user.ordinals})+")
def letters_colors(m) -> list[str]:
    """Capture any number of letters, colors, and ordinal multipliers.

    Ordinals following a letter or color will multiply that item.
    Example: "red third air" -> ["red", "third", "a"]
    """
    return [str(word) for word in m]
