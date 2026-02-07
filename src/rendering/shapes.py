_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Cursorless hat shape constants.

Maps SVG filename stems to their one-syllable spoken forms (chrysalis names).
"""

# SVG filename stem -> one-syllable spoken form
HAT_NAMES = {
    "bolt": "bolt",
    "crosshairs": "cross",
    "curve": "curve",
    "default": "default",
    "ex": "ex",
    "eye": "eye",
    "fox": "fox",
    "frame": "frame",
    "hole": "hole",
    "play": "play",
    "wing": "wing",
}

# Just the spoken forms (excluding "default" which has no distinct shape name)
HAT_SHAPES = [name for name in HAT_NAMES.values() if name != "default"]

# Spoken form -> spoken form, suitable for a talon-list
HAT_SHAPE_LIST = {v: v for v in HAT_NAMES.values()}
