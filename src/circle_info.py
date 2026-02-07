"""Circle info panel - renders hat shapes in a large screen-centered circular layout.

Same ring distribution as clock_ring (ring 1 = 1 shape/color, ring 2 = 2/color, etc.)
but scaled to fill 80% of screen height for easy reference.
"""

import math

from talon import Context, Module, ui, ctrl, cron
from talon.canvas import Canvas
from talon.skia import Path

from .rendering.svg_loader import load_svg_paths

mod = Module()
_ctx_tags = Context()

_canvas = None
_poll_job = None
_shape_positions = {}  # {(color_name, shape_spoken_name): (dx, dy) from mouse}

# Base dimensions matching clock_ring proportions
_BASE_SC = 0.75
_BASE_SVG_H = 9
_BASE_SVG_W = 12
_BASE_SHAPE_H = _BASE_SVG_H * _BASE_SC       # 6.75
_BASE_RING_GAP = _BASE_SHAPE_H + 6            # 12.75
_BASE_FIRST_DIST = _BASE_SHAPE_H + 4          # 10.75


def _on_draw(c):
    from .rendering.colors import COLOR_REGISTRY, DISPLAY_COLORS

    colors = [(name, COLOR_REGISTRY[name][:6]) for name in DISPLAY_COLORS]
    if not colors:
        return

    svg_paths = load_svg_paths(default_first=True)
    if not svg_paths:
        return

    _shape_positions.clear()

    screen = ui.main_screen()
    screen_w = screen.rect.width
    screen_h = screen.rect.height
    center_x = screen.rect.x + screen_w / 2
    center_y = screen.rect.y + screen_h / 2

    num_colors = len(colors)
    sweep = 360.0 / num_colors

    # Count rings (same algorithm as clock_ring)
    remaining = len(svg_paths)
    r = 1
    num_rings = 0
    while remaining > 0:
        remaining -= min(r, remaining)
        num_rings += 1
        r += 1

    # Outermost shape edge in base units (ring center + half a shape)
    base_outer_edge = (_BASE_FIRST_DIST
                       + (num_rings - 1) * _BASE_RING_GAP
                       + _BASE_SHAPE_H / 2)

    # Background fills 80% of screen height; shapes scale to reach its edge
    bg_radius = 0.475 * screen_h
    scale_factor = bg_radius / (base_outer_edge + 2)  # +2 base-unit margin
    sc = _BASE_SC * scale_factor * 0.70
    shape_h = _BASE_SVG_H * sc
    ring_gap = _BASE_RING_GAP * scale_factor
    first_dist = _BASE_FIRST_DIST * scale_factor

    mx, my = ctrl.mouse_pos()

    # Solid dark circular background
    c.paint.style = c.paint.Style.FILL
    c.paint.color = "000000cc"
    c.draw_circle(center_x, center_y, bg_radius)

    # Draw concentric rings of hat shapes
    shape_idx = 0
    ring_num = 1
    dist = first_dist

    while shape_idx < len(svg_paths):
        shapes_this_ring = min(ring_num, len(svg_paths) - shape_idx)

        for i, (name, hex_val) in enumerate(colors):
            start_deg = i * sweep

            for k in range(shapes_this_ring):
                angle_deg = start_deg + (k + 0.5) * sweep / shapes_this_ring
                angle_rad = math.radians(angle_deg)
                sx = center_x + dist * math.cos(angle_rad)
                sy = center_y + dist * math.sin(angle_rad)

                shape_name, d, fill_rule = svg_paths[shape_idx + k]
                _shape_positions[(name, shape_name)] = (sx - mx, sy - my)
                shape_path = Path.from_svg(d)
                if fill_rule == "evenodd":
                    shape_path.fill_type = Path.FillType.EVENODD

                c.save()
                c.translate(sx - (_BASE_SVG_W * sc) / 2, sy - shape_h / 2)
                c.scale(sc, sc)

                c.paint.style = c.paint.Style.FILL
                c.paint.color = hex_val
                c.draw_path(shape_path)

                c.paint.style = c.paint.Style.STROKE
                c.paint.stroke_width = 0.4
                stroke_color = "ffffff" if name in ("black",) else "000000"
                c.paint.color = stroke_color
                c.draw_path(shape_path)

                c.restore()

        shape_idx += shapes_this_ring
        ring_num += 1
        dist += ring_gap


def _poll_mouse():
    if _canvas:
        _canvas.freeze()


def _show():
    global _canvas, _poll_job
    _hide()
    screen = ui.main_screen()
    _canvas = Canvas.from_screen(screen)
    _canvas.register("draw", _on_draw)
    _canvas.freeze()
    _poll_job = cron.interval("16ms", _poll_mouse)
    _ctx_tags.tags = ["user.clock_ring_showing"]


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


def _select(color: str, shape: str):
    """Move mouse to a color+shape position on the circle info panel."""
    offset = _shape_positions.get((color, shape))
    if not offset:
        return False
    mx, my = ctrl.mouse_pos()
    ctrl.mouse_move(mx + offset[0], my + offset[1])
    if _canvas:
        _canvas.freeze()
    return True


@mod.action_class
class Actions:
    def circle_info_show():
        """Show the circle info panel"""
        _show()

    def circle_info_hide():
        """Hide the circle info panel"""
        _hide()
