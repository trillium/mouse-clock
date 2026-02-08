"""Shared SVG loading for hat shape rendering.

Parses SVG files from the svg/ directory and returns path data
for drawing with Talon's Skia canvas.

Results are cached at module level since SVG assets are static.
"""

import os
import xml.etree.ElementTree as ET

from ..core.constants import HAT_NAMES

_SVG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "svg")

# Module-level cache: keyed by default_first boolean
_cache = {}


def _parse_svg_entries():
    """Parse all SVG files and return (key, spoken_name, path_data, fill_rule) tuples.

    This is the raw parse step, called once. Results include the filename key
    so callers can reorder by default_first without re-parsing.
    """
    entries = []
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
                entries.append((key, spoken_name, d, fill_rule))
    return entries


def _build_result(entries, default_first):
    """Build the public result list from raw entries, applying ordering."""
    results = []
    default_entry = None
    for key, spoken_name, d, fill_rule in entries:
        entry = (spoken_name, d, fill_rule)
        if default_first and key == "default":
            default_entry = entry
        else:
            results.append(entry)
    if default_entry:
        results.insert(0, default_entry)
    return results


def load_svg_paths(default_first=False):
    """Parse SVG files, returning (spoken_name, path_data, fill_rule) tuples.

    Results are cached after first call. SVG files are static assets that
    never change at runtime, so re-parsing on every frame is unnecessary.

    Args:
        default_first: If True, place the "default" shape first in results.
    """
    if default_first not in _cache:
        # Parse once, then build both variants from the same parse
        if not _cache:
            entries = _parse_svg_entries()
            _cache[True] = _build_result(entries, default_first=True)
            _cache[False] = _build_result(entries, default_first=False)
        else:
            # Shouldn't happen (both keys set together), but be safe
            entries = _parse_svg_entries()
            _cache[default_first] = _build_result(entries, default_first)
    return _cache[default_first]
