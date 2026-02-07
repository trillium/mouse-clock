"""Clock ring - renders cursorless hat shapes in concentric rings around the cursor.

Each ring segment shows shapes in a color, radiating outward with a fading
dark backdrop for readability.
"""

import math
import os
import time
import xml.etree.ElementTree as ET

from talon import Context, Module, ui, ctrl, cron, skia
from talon.canvas import Canvas
from talon.skia import Path
from talon.ui import Point2d

mod = Module()
mod.list("hat_shape", desc="Cursorless hat shape spoken forms")
mod.tag("clock_ring_showing", desc="Color pie chart is visible")

_ctx_tags = Context()
_canvas = None
_poll_job = None
_shape_positions = {}  # {(color_name, shape_spoken_name): (x, y)}

# Fade state machine — single-timer driven
_fade_alpha = 255       # current alpha 0-255
_fade_state = "idle"    # "fade_out", "delay", "fade_in"
_fade_start_time = 0.0
_fade_start_alpha = 255
_fade_target_alpha = 0
_fade_duration_ms = 4000

SVG_SCALE = 0.75
_SPACING_STEP = 1
SVG_W = 12  # viewBox width
SVG_H = 9   # viewBox height
_SVG_DIR = os.path.join(os.path.dirname(__file__), "svg")


def _fade_tick():
    """Update fade alpha, then freeze canvas. Single 16ms timer for everything."""
    global _fade_alpha, _fade_state, _fade_start_time, _fade_start_alpha
    global _fade_target_alpha, _fade_duration_ms

    if _fade_state in ("fade_out", "fade_in"):
        elapsed = (time.time() - _fade_start_time) * 1000
        progress = min(elapsed / _fade_duration_ms, 1.0)
        _fade_alpha = int(_fade_start_alpha + (_fade_target_alpha - _fade_start_alpha) * progress)

        if progress >= 1.0:
            _fade_alpha = _fade_target_alpha
            if _fade_state == "fade_out":
                # Transition to delay at min
                from .core.config import get_setting
                _fade_state = "delay"
                _fade_start_time = time.time()
                _fade_duration_ms = int(get_setting("clock_ring_fade_delay_ms", 2000))
            else:
                # fade_in complete → start fade_out
                from .core.config import get_setting
                _fade_state = "fade_out"
                _fade_start_time = time.time()
                _fade_start_alpha = _fade_alpha
                _fade_target_alpha = 0
                _fade_duration_ms = int(get_setting("clock_ring_fade_out_ms", 4000))

    elif _fade_state == "delay":
        elapsed = (time.time() - _fade_start_time) * 1000
        if elapsed >= _fade_duration_ms:
            # Delay complete → start fade_in
            from .core.config import get_setting
            _fade_state = "fade_in"
            _fade_start_time = time.time()
            _fade_start_alpha = _fade_alpha
            _fade_target_alpha = 255
            _fade_duration_ms = int(get_setting("clock_ring_fade_in_ms", 1000))

    if _canvas:
        _canvas.freeze()


def _load_svg_paths():
    """Parse SVG files, returning (spoken_name, path_data, fill_rule) tuples.

    "default" is returned first, then the rest alphabetically.
    """
    from .core.constants import HAT_NAMES

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

    # Fade: bg and icon opacity driven by _fade_alpha
    from .core.config import get_setting
    bg_max = get_setting("clock_ring_fade_bg_max", 0.7)
    bg_min = get_setting("clock_ring_fade_bg_min", 0.1)
    icon_min = get_setting("clock_ring_fade_icon_min", 0.3)
    t = _fade_alpha / 255.0  # 1.0 = full, 0.0 = faded
    bg_alpha = int((bg_min + t * (bg_max - bg_min)) * 255)
    icon_alpha = int((icon_min + t * (1.0 - icon_min)) * 255)

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


def _get_ring_spacing():
    from .core.config import get_setting
    return get_setting("clock_ring_ring_spacing", 0.0)


def _set_ring_spacing(value):
    from .core.config import set_setting, _auto_save
    set_setting("clock_ring_ring_spacing", value)
    _auto_save()


def _show():
    global _canvas, _poll_job
    global _fade_alpha, _fade_state, _fade_start_time, _fade_start_alpha
    global _fade_target_alpha, _fade_duration_ms
    _hide()

    # Init fade state machine
    from .core.config import get_setting
    _fade_alpha = 255
    _fade_state = "fade_out"
    _fade_start_time = time.time()
    _fade_start_alpha = 255
    _fade_target_alpha = 0
    _fade_duration_ms = int(get_setting("clock_ring_fade_out_ms", 4000))

    screen = ui.main_screen()
    _canvas = Canvas.from_screen(screen)
    _canvas.register("draw", _on_draw)
    _canvas.freeze()
    _poll_job = cron.interval("16ms", _fade_tick)
    _ctx_tags.tags = ["user.clock_ring_showing"]


def _hide():
    global _canvas, _poll_job, _fade_alpha, _fade_state
    _ctx_tags.tags = []
    _fade_state = "idle"
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
    def clock_ring_show():
        """Show the clock ring"""
        _show()

    def clock_ring_hide():
        """Hide the clock ring and hats info panel"""
        _hide()
        from .hats_info import _hide as _hats_hide
        _hats_hide()

    def clock_ring_select(color: str, shape: str):
        """Move mouse to the specified color+shape position on the pie or info panel"""
        offset = _shape_positions.get((color, shape))
        if not offset:
            # Fall through to hats info panel
            from .hats_info import _select as _hats_select
            if _hats_select(color, shape):
                return
            return
        mx, my = ctrl.mouse_pos()
        ctrl.mouse_move(mx + offset[0], my + offset[1])
        if _canvas:
            _canvas.freeze()

    def clock_ring_widen(steps: int = 1):
        """Increase spacing between rings"""
        _set_ring_spacing(_get_ring_spacing() + _SPACING_STEP * steps)
        if _canvas:
            _canvas.freeze()

    def clock_ring_narrow(steps: int = 1):
        """Decrease spacing between rings"""
        _set_ring_spacing(max(0, _get_ring_spacing() - _SPACING_STEP * steps))
        if _canvas:
            _canvas.freeze()
