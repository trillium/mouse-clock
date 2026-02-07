"""Color pie chart - renders mouse clock colors as a pie circle following the cursor.

Each pie slice shows a color, with cursorless hat shapes radiating outward
along that slice's direction, rendered in that color.
"""

import math
import os
import xml.etree.ElementTree as ET

from talon import Context, Module, ui, ctrl, cron, skia
from talon.canvas import Canvas
from talon.skia import Path
from talon.ui import Point2d

mod = Module()
mod.list("hat_shape", desc="Cursorless hat shape spoken forms")
mod.tag("color_pie_showing", desc="Color pie chart is visible")

_ctx_tags = Context()
_canvas = None
_poll_job = None
_fade_animator = None
_fade_alpha = 255  # 255 = full, 0 = faded
_shape_positions = {}  # {(color_name, shape_spoken_name): (x, y)}


def _on_fade_update(alpha):
    global _fade_alpha
    _fade_alpha = alpha

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

    # Pre-compute number of rings to get max radius for background
    first_dist = shape_h + 4 + spacing
    remaining = len(svg_paths)
    r = 1
    num_rings = 0
    while remaining > 0:
        remaining -= min(r, remaining)
        num_rings += 1
        r += 1
    max_dist = first_dist + (num_rings - 1) * ring_gap

    # Fade: bg 70%→0%, icons 100%→30%
    t = _fade_alpha / 255.0  # 1.0 = full, 0.0 = faded
    bg_alpha = int((0.1 + t * 0.6) * 255)  # 25→178 (10%→70%)
    icon_alpha = int(77 + t * 178)  # 77→255 (30%→100%)

    # Draw dark radial gradient background behind the pie
    bg_radius = max_dist + shape_h * 3
    bg_hex = f"000000{bg_alpha:02x}"
    c.paint.style = c.paint.Style.FILL
    c.paint.shader = skia.Shader.radial_gradient(
        Point2d(mx, my), bg_radius,
        ["00000000", bg_hex, bg_hex, "00000000"],
        [0.0, 0.12, 0.88, 1.0],
    )
    c.draw_circle(mx, my, bg_radius)
    c.paint.shader = None

    # Draw concentric rings of hat shapes
    # Ring 1: 1 per color, Ring 2: 2 per color, Ring 3: 3 per color, etc.
    shape_idx = 0
    ring_num = 1
    dist = first_dist

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
                _shape_positions[(name, shape_name)] = (cx - mx, cy - my)
                shape_path = Path.from_svg(d)
                if fill_rule == "evenodd":
                    shape_path.fill_type = Path.FillType.EVENODD

                c.save()
                c.translate(cx - (SVG_W * sc) / 2, cy - shape_h / 2)
                c.scale(sc, sc)

                c.paint.style = c.paint.Style.FILL
                c.paint.color = f"{hex_val}{icon_alpha:02x}"
                c.draw_path(shape_path)

                c.paint.style = c.paint.Style.STROKE
                c.paint.stroke_width = 0.4
                stroke_base = "ffffff" if name in ("black",) else "000000"
                c.paint.color = f"{stroke_base}{icon_alpha:02x}"
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
    global _canvas, _poll_job, _fade_animator, _fade_alpha
    from .rendering.animation import FadeAnimator
    _hide()
    _fade_alpha = 255
    _fade_animator = FadeAnimator(on_update=_on_fade_update)
    _fade_animator.set_alpha(255)
    _fade_animator.pulse(min_alpha=0, max_alpha=255,
                         fade_out_ms=4000, fade_in_ms=1000,
                         delay_at_min_ms=2000)
    screen = ui.main_screen()
    _canvas = Canvas.from_screen(screen)
    _canvas.register("draw", _on_draw)
    _canvas.freeze()
    _poll_job = cron.interval("16ms", _poll_mouse)
    _ctx_tags.tags = ["user.color_pie_showing"]


def _hide():
    global _canvas, _poll_job, _fade_animator, _fade_alpha
    _ctx_tags.tags = []
    if _fade_animator:
        _fade_animator._cancel()
        _fade_animator = None
    _fade_alpha = 255
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
        """Hide the color pie chart and hats info panel"""
        _hide()
        from .test_svg_render import _hide as _hats_hide
        _hats_hide()

    def color_pie_select(color: str, shape: str):
        """Move mouse to the specified color+shape position on the pie or info panel"""
        offset = _shape_positions.get((color, shape))
        if not offset:
            # Fall through to hats info panel
            from .test_svg_render import _select as _hats_select
            if _hats_select(color, shape):
                return
            return
        mx, my = ctrl.mouse_pos()
        ctrl.mouse_move(mx + offset[0], my + offset[1])
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
