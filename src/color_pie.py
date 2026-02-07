"""Color pie chart - renders mouse clock colors as a pie circle following the cursor.

Each pie slice shows a color, with cursorless hat shapes radiating outward
along that slice's direction, rendered in that color.
"""

import math
import os
import xml.etree.ElementTree as ET

from talon import Context, Module, ui, ctrl, cron
from talon.canvas import Canvas
from talon.skia import Path

mod = Module()
mod.list("hat_shape", desc="Cursorless hat shape spoken forms")
mod.tag("color_pie_showing", desc="Color pie chart is visible")

_ctx_tags = Context()
_canvas = None
_poll_job = None
_shape_positions = {}  # {(color_name, shape_spoken_name): (x, y)}

SVG_SCALE = 0.75
_SPACING_STEP = 1
SVG_W = 12  # viewBox width
SVG_H = 9   # viewBox height
_SVG_DIR = os.path.join(os.path.dirname(__file__), "svg")


def _load_svg_paths():
    """Parse SVG files, returning (spoken_name, path_data, fill_rule) tuples.

    "default" is returned first, then the rest alphabetically.
    """
    from .rendering.shapes import HAT_NAMES

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
                if key == "default":
                    default_entry = entry
                else:
                    results.append(entry)
    # Default first
    if default_entry:
        results.insert(0, default_entry)
    return results


def _on_draw(c):
    from .rendering.colors import COLOR_REGISTRY, DISPLAY_COLORS

    colors = [(name, COLOR_REGISTRY[name][:6]) for name in DISPLAY_COLORS]
    if not colors:
        return

    svg_paths = _load_svg_paths()
    _shape_positions.clear()

    mx, my = ctrl.mouse_pos()
    num = len(colors)
    sweep = 360.0 / num
    sc = SVG_SCALE
    shape_h = SVG_H * sc
    spacing = _get_ring_spacing()
    ring_gap = shape_h + 6 + spacing  # radial spacing between rings

    # Draw concentric rings of hat shapes
    # Ring 1: 1 per color, Ring 2: 2 per color, Ring 3: 3 per color, etc.
    shape_idx = 0
    ring_num = 1
    dist = shape_h + 4 + spacing  # first ring distance from center

    while shape_idx < len(svg_paths):
        shapes_this_ring = min(ring_num, len(svg_paths) - shape_idx)

        for i, (name, hex_val) in enumerate(colors):
            start_deg = i * sweep

            for k in range(shapes_this_ring):
                # Evenly distribute within this color's slice
                angle_deg = start_deg + (k + 0.5) * sweep / shapes_this_ring
                angle_rad = math.radians(angle_deg)
                cx = mx + dist * math.cos(angle_rad)
                cy = my + dist * math.sin(angle_rad)

                shape_name, d, fill_rule = svg_paths[shape_idx + k]
                _shape_positions[(name, shape_name)] = (cx, cy)
                shape_path = Path.from_svg(d)
                if fill_rule == "evenodd":
                    shape_path.fill_type = Path.FillType.EVENODD

                c.save()
                c.translate(cx - (SVG_W * sc) / 2, cy - shape_h / 2)
                c.scale(sc, sc)

                c.paint.style = c.paint.Style.FILL
                c.paint.color = hex_val
                c.draw_path(shape_path)

                c.paint.style = c.paint.Style.STROKE
                c.paint.stroke_width = 0.4
                c.paint.color = "ffffff" if name in ("black",) else "000000"
                c.draw_path(shape_path)

                c.restore()

        shape_idx += shapes_this_ring
        ring_num += 1
        dist += ring_gap


def _poll_mouse():
    if _canvas:
        _canvas.freeze()


def _get_ring_spacing():
    from .core.config import get_setting
    return get_setting("color_pie_ring_spacing", 0.0)


def _set_ring_spacing(value):
    from .core.config import set_setting, _auto_save
    set_setting("color_pie_ring_spacing", value)
    _auto_save()


def _show():
    global _canvas, _poll_job
    _hide()
    screen = ui.main_screen()
    _canvas = Canvas.from_screen(screen)
    _canvas.register("draw", _on_draw)
    _canvas.freeze()
    _poll_job = cron.interval("16ms", _poll_mouse)
    _ctx_tags.tags = ["user.color_pie_showing"]


def _hide():
    global _canvas, _poll_job
    _ctx_tags.tags = []
    if _poll_job:
        cron.cancel(_poll_job)
        _poll_job = None
    if _canvas:
        try:
            _canvas.unregister("draw", _on_draw)
        except Exception:
            pass
        _canvas.close()
        _canvas = None


@mod.capture(rule="{user.hat_shape}")
def hat_shape(match) -> str:
    """Capture a hat shape spoken form"""
    return match.hat_shape


@mod.action_class
class Actions:
    def color_pie_show():
        """Show the color pie chart"""
        _show()

    def color_pie_hide():
        """Hide the color pie chart"""
        _hide()

    def color_pie_select(color: str, shape: str):
        """Move mouse to the specified color+shape position on the pie"""
        global _poll_job
        pos = _shape_positions.get((color, shape))
        if not pos:
            return
        if _poll_job:
            cron.cancel(_poll_job)
            _poll_job = None
        ctrl.mouse_move(pos[0], pos[1])
        if _canvas:
            _canvas.freeze()

    def color_pie_widen(steps: int = 1):
        """Increase spacing between rings"""
        _set_ring_spacing(_get_ring_spacing() + _SPACING_STEP * steps)
        if _canvas:
            _canvas.freeze()

    def color_pie_narrow(steps: int = 1):
        """Decrease spacing between rings"""
        _set_ring_spacing(max(0, _get_ring_spacing() - _SPACING_STEP * steps))
        if _canvas:
            _canvas.freeze()
