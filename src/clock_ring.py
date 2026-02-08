"""Clock ring - renders cursorless hat shapes in concentric rings around the cursor.

Each ring segment shows shapes in a color, radiating outward with a fading
dark backdrop for readability.
"""

import math

from talon import Context, Module, actions, ui, ctrl, skia
from talon.canvas import Canvas
from talon.skia import Path
from talon.ui import Point2d

from .core.config import get_setting, on_setting_change
from .rendering.animation import FadeAnimator
from .rendering.svg_loader import load_svg_paths

mod = Module()
mod.list("hat_shape", desc="Cursorless hat shape spoken forms")
mod.tag("clock_ring_showing", desc="Color pie chart is visible")

_POLL_INTERVAL_KEY = "poll_interval_ms"
_POLL_INTERVAL_DEFAULT = 16

_ctx_tags = Context()
_canvas = None
_shape_positions = {}  # {(color_name, shape_spoken_name): (x, y)}


def _get_poll_interval():
    return int(get_setting(_POLL_INTERVAL_KEY, _POLL_INTERVAL_DEFAULT))


def _on_fade_update(alpha: int):
    """Callback from FadeAnimator — freeze canvas to trigger redraw."""
    if _canvas:
        _canvas.freeze()


_fade = FadeAnimator(on_update=_on_fade_update, frame_interval_ms=_get_poll_interval())
_fade.alpha = 255


def _on_poll_interval_change(value):
    """Restart the fade animator with the new interval if currently showing."""
    _fade.frame_interval_ms = int(value)
    if _canvas:
        _hide()
        _show()


on_setting_change(_POLL_INTERVAL_KEY, _on_poll_interval_change)

SVG_SCALE = 0.75
_SPACING_STEP = 1
SVG_W = 12  # viewBox width
SVG_H = 9   # viewBox height


def _on_draw(c):
    from .rendering.colors import COLOR_REGISTRY, DISPLAY_COLORS

    colors = [(name, COLOR_REGISTRY[name][:6]) for name in DISPLAY_COLORS]
    if not colors:
        return

    svg_paths = load_svg_paths(default_first=True)
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

    # Fade: bg and icon opacity driven by FadeAnimator
    from .core.config import get_setting
    bg_max = get_setting("clock_ring_fade_bg_max", 0.7)
    bg_min = get_setting("clock_ring_fade_bg_min", 0.1)
    icon_min = get_setting("clock_ring_fade_icon_min", 0.3)
    t = _fade.alpha / 255.0  # 1.0 = full, 0.0 = faded
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
    from .core.config import set_setting
    set_setting("clock_ring_ring_spacing", value, persist=True)


def _show():
    global _canvas
    _hide()

    from .core.config import get_setting

    screen = ui.main_screen()
    _canvas = Canvas.from_screen(screen)
    _canvas.register("draw", _on_draw)
    _canvas.freeze()

    _fade.alpha = 255
    _fade.pulse(
        min_alpha=0,
        max_alpha=255,
        fade_out_ms=int(get_setting("clock_ring_fade_out_ms", 4000)),
        fade_in_ms=int(get_setting("clock_ring_fade_in_ms", 1000)),
        delay_at_min_ms=int(get_setting("clock_ring_fade_delay_ms", 2000)),
    )
    _ctx_tags.tags = ["user.clock_ring_showing"]


def _hide():
    global _canvas
    _ctx_tags.tags = []
    _fade.stop()
    _fade.alpha = 255
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
        """Hide the clock ring and all info panels"""
        _hide()
        from .circle_info import _hide as _circle_hide
        _circle_hide()
        from .hats_info import _hide as _hats_hide
        _hats_hide()

    def clock_ring_toggle():
        """Toggle the clock ring on/off"""
        if "user.clock_ring_showing" in _ctx_tags.tags:
            actions.user.clock_ring_hide()
        else:
            actions.user.clock_ring_show()

    def clock_ring_select(color: str, shape: str):
        """Move mouse to the specified color+shape position on the pie or info panel"""
        offset = _shape_positions.get((color, shape))
        if not offset:
            # Fall through to circle info, then hats info panel
            from .circle_info import _select as _circle_select
            if _circle_select(color, shape):
                return
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
