"""Shared SVG loading for hat shape rendering.

Parses SVG files from the svg/ directory and returns path data
for drawing with Talon's Skia canvas.
"""

import os
import xml.etree.ElementTree as ET

from ..core.constants import HAT_NAMES

_SVG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "svg")


def load_svg_paths(default_first=False):
    """Parse SVG files, returning (spoken_name, path_data, fill_rule) tuples.

    Args:
        default_first: If True, place the "default" shape first in results.
    """
    results = []
    default_entry = None
    for fname in sorted(os.listdir(_SVG_DIR)):
        if not fname.endswith(".svg"):
            continue
        tree = ET.parse(os.path.join(_SVG_DIR, fname))
        root = tree.getroot()
        ns = {"svg": "http://www.w3.org/2000/svg"}
        key = fname.replace(".svg", "")
        spoken_name = HAT_NAMES.get(key, key)
        for path_el in root.findall(".//svg:path", ns):
            d = path_el.get("d", "")
            fill_rule = path_el.get("fill-rule", "nonzero")
            if d:
                entry = (spoken_name, d, fill_rule)
                if default_first and key == "default":
                    default_entry = entry
                else:
                    results.append(entry)
    if default_entry:
        results.insert(0, default_entry)
    return results
