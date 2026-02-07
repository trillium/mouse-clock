"""
Cursorless hat shape constants.

Maps SVG filename stems to their one-syllable spoken forms (chrysalis names).
"""

# SVG filename stem -> one-syllable spoken form
HAT_NAMES = {
    "bolt": "bolt",
    "crosshairs": "cross",
    "curve": "curve",
    "default": "dot",
    "ex": "ex",
    "eye": "eye",
    "fox": "fox",
    "frame": "frame",
    "hole": "hole",
    "play": "play",
    "wing": "wing",
}

# Just the spoken forms (excluding "dot"/default which is the base hat shape)
HAT_SHAPES = [name for name in HAT_NAMES.values() if name != "dot"]

# Spoken form -> spoken form, suitable for a talon-list
HAT_SHAPE_LIST = {v: v for v in HAT_NAMES.values()}
