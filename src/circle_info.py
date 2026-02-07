"""Circle info panel - renders hat shapes in a large screen-centered circular layout.

Same ring distribution as clock_ring (ring 1 = 1 shape/color, ring 2 = 2/color, etc.)
but scaled to fill 80% of screen height for easy reference.
"""

import math
import random

from talon import Context, Module, registry, ui, ctrl, cron
from talon.canvas import Canvas
from talon.skia import Path

from .rendering.svg_loader import load_svg_paths

mod = Module()
_ctx_tags = Context()

_canvas = None
_poll_job = None
_shape_positions = {}  # {(color_name, shape_spoken_name): (dx, dy) from mouse}
_current_target = None  # (color_name, shape_name) — the prompt to display
_highlight = (None, None)  # (color_or_none, shape_or_none) — user's spoken highlight
_show_prompt = False  # reveal center text after delay
_prompt_job = None
_show_error = False  # flash red circle on wrong answer
_error_job = None
_mode = "game"  # "game" or "learn"
_learn_count = 0  # how many targets shown in learn mode
_learn_queue = []  # pre-built sequence for first 10 learn items
_weights = {}  # {(color, shape): float} — spaced repetition weights
_LEARN_INTRO_COUNT = 10
_LEARN_STREAK_TARGET = 20
_streak = 0  # consecutive correct answers after intro
_done = False  # user completed the session

# Base dimensions matching clock_ring proportions
_BASE_SC = 0.75
_BASE_SVG_H = 9
_BASE_SVG_W = 12
_BASE_SHAPE_H = _BASE_SVG_H * _BASE_SC       # 6.75
_BASE_RING_GAP = _BASE_SHAPE_H + 6            # 12.75
_BASE_FIRST_DIST = _BASE_SHAPE_H + 4          # 10.75


def _get_spoken_color(color_name):
    """Find shortest spoken form for a color from the talon registry."""
    color_list = (registry.lists.get("user.color") or [{}])[0]
    spoken_forms = [k for k, v in color_list.items() if v == color_name]
    return min(spoken_forms, key=len) if spoken_forms else color_name


def _draw_background(c, center_x, center_y, bg_radius):
    """Solid dark circular background shared by both modes."""
    c.paint.style = c.paint.Style.FILL
    c.paint.color = "000000cc"
    c.draw_circle(center_x, center_y, bg_radius)


def _draw_prompt_text(c, center_x, center_y, color_name, shape_name, color_hex):
    """Draw color + shape name text at a position."""
    display_color = _get_spoken_color(color_name)
    c.paint.style = c.paint.Style.FILL
    # Color name — outline for readability on dark bg
    cw, _ = c.paint.measure_text(display_color)
    c.paint.style = c.paint.Style.STROKE
    c.paint.stroke_width = 3
    c.paint.color = "000000" if color_name not in ("black", "center") else "ffffff"
    c.draw_text(display_color, center_x - cw / 2, center_y)
    c.paint.style = c.paint.Style.FILL
    c.paint.color = color_hex
    c.draw_text(display_color, center_x - cw / 2, center_y)
    # Shape name below
    sw, _ = c.paint.measure_text(shape_name)
    c.paint.color = "ffffffcc"
    c.draw_text(shape_name, center_x - sw / 2, center_y + 20)


def _on_draw(c):
    from .rendering.colors import COLOR_REGISTRY, DISPLAY_COLORS

    colors = [(name, COLOR_REGISTRY[name][:6]) for name in DISPLAY_COLORS]
    if not colors:
        return

    svg_paths = load_svg_paths(default_first=True)
    if not svg_paths:
        return

    screen = ui.main_screen()
    screen_h = screen.rect.height
    center_x = screen.rect.x + screen.rect.width / 2
    center_y = screen.rect.y + screen_h / 2
    bg_radius = 0.475 * screen_h

    _draw_background(c, center_x, center_y, bg_radius)

    if _mode == "learn":
        _draw_learn(c, center_x, center_y, bg_radius, colors, svg_paths)
    else:
        _draw_game(c, center_x, center_y, bg_radius, colors, svg_paths)


def _draw_learn(c, center_x, center_y, bg_radius, colors, svg_paths):
    """Learn mode: one large shape centered with text below."""
    # Done screen
    if _done:
        c.paint.style = c.paint.Style.FILL
        c.paint.textsize = 36
        c.paint.color = "00ff00ff"
        text = "Done!"
        tw, _ = c.paint.measure_text(text)
        c.draw_text(text, center_x - tw / 2, center_y)
        return

    if not _current_target:
        return

    color_name, shape_name = _current_target
    color_hex = dict(colors).get(color_name, "ffffff")

    # Find the SVG path data for the target shape
    d = None
    fill_rule = "nonzero"
    for sname, sdata, srule in svg_paths:
        if sname == shape_name:
            d = sdata
            fill_rule = srule
            break
    if not d:
        return

    # Large shape: scale to ~40% of bg_radius
    learn_sc = (bg_radius * 0.4) / _BASE_SVG_H
    shape_w = _BASE_SVG_W * learn_sc
    shape_h = _BASE_SVG_H * learn_sc
    shape_x = center_x - shape_w / 2
    shape_y = center_y - shape_h / 2 - 30  # shift up to make room for text

    shape_path = Path.from_svg(d)
    if fill_rule == "evenodd":
        shape_path.fill_type = Path.FillType.EVENODD

    c.save()
    c.translate(shape_x, shape_y)
    c.scale(learn_sc, learn_sc)

    c.paint.style = c.paint.Style.FILL
    c.paint.color = color_hex
    c.draw_path(shape_path)

    c.paint.style = c.paint.Style.STROKE
    c.paint.stroke_width = 0.2
    stroke_base = "ffffff" if color_name in ("black",) else "000000"
    c.paint.color = stroke_base
    c.draw_path(shape_path)

    c.restore()

    # Error ring around shape area
    if _show_error:
        c.paint.style = c.paint.Style.STROKE
        c.paint.stroke_width = 3
        c.paint.color = "ff0000ff"
        c.draw_circle(center_x, center_y - 30, max(shape_w, shape_h) * 0.7)

    # Text below shape
    text_y = center_y + shape_h / 2 + 10
    c.paint.textsize = 28
    if _show_prompt:
        _draw_prompt_text(c, center_x, text_y, color_name, shape_name, color_hex)

    # Progress counter below text
    c.paint.style = c.paint.Style.FILL
    c.paint.textsize = 16
    c.paint.color = "ffffff88"
    in_intro = _learn_count <= _LEARN_INTRO_COUNT
    if in_intro:
        progress = f"{_learn_count}/{_LEARN_INTRO_COUNT}"
    else:
        progress = f"{_streak}/{_LEARN_STREAK_TARGET}"
    pw, _ = c.paint.measure_text(progress)
    c.draw_text(progress, center_x - pw / 2, text_y + 50)


def _draw_game(c, center_x, center_y, bg_radius, colors, svg_paths):
    """Game mode: concentric rings with highlighting."""
    _shape_positions.clear()

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

    scale_factor = bg_radius / (base_outer_edge + 2)
    sc = _BASE_SC * scale_factor * 0.70
    shape_h = _BASE_SVG_H * sc
    ring_gap = _BASE_RING_GAP * scale_factor
    first_dist = _BASE_FIRST_DIST * scale_factor

    mx, my = ctrl.mouse_pos()

    # Center circle with prompt text
    center_r = (first_dist - shape_h * 0.8) * 0.9
    c.paint.style = c.paint.Style.STROKE
    c.paint.stroke_width = 3 if _show_error else 2
    c.paint.color = "ff0000ff" if _show_error else "ffffffcc"
    c.draw_circle(center_x, center_y, center_r)

    if _current_target and _show_prompt:
        color_name, shape_name = _current_target
        color_hex = dict(colors).get(color_name, "ffffff")
        c.paint.textsize = 18
        _draw_prompt_text(c, center_x, center_y - 4, color_name, shape_name, color_hex)

    # Highlighting driven by user voice input
    hl_color, hl_shape = _highlight

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

                is_target = _current_target and (name, shape_name) == _current_target
                color_match = (hl_color is not None and name == hl_color)
                shape_match = (hl_shape is not None and shape_name == hl_shape)
                if is_target:
                    highlighted = True
                elif hl_color is None and hl_shape is None:
                    highlighted = False
                elif hl_color is not None and hl_shape is not None:
                    highlighted = color_match and shape_match
                else:
                    highlighted = color_match or shape_match
                alpha = "ff" if highlighted else "40"

                c.save()
                c.translate(sx - (_BASE_SVG_W * sc) / 2, sy - shape_h / 2)
                c.scale(sc, sc)

                c.paint.style = c.paint.Style.FILL
                c.paint.color = f"{hex_val}{alpha}"
                c.draw_path(shape_path)

                c.paint.style = c.paint.Style.STROKE
                c.paint.stroke_width = 0.2
                stroke_base = "ffffff" if name in ("black",) else "000000"
                c.paint.color = f"{stroke_base}{alpha}"
                c.draw_path(shape_path)

                c.restore()

                # Target indicator circle
                if _current_target and (name, shape_name) == _current_target:
                    indicator_r = max(shape_h, _BASE_SVG_W * sc) * 0.8
                    c.paint.style = c.paint.Style.STROKE
                    c.paint.stroke_width = 2
                    c.paint.color = "ffffffcc"
                    c.draw_circle(sx, sy, indicator_r)

        shape_idx += shapes_this_ring
        ring_num += 1
        dist += ring_gap


def _poll_mouse():
    if _canvas:
        _canvas.freeze()


def _reveal_prompt():
    global _show_prompt, _prompt_job
    _show_prompt = True
    _prompt_job = None
    if _canvas:
        _canvas.freeze()


def _pick_target():
    global _current_target, _show_prompt, _prompt_job, _learn_count
    if _prompt_job:
        cron.cancel(_prompt_job)
    _show_prompt = False

    if _mode == "learn":
        _learn_count += 1

    # During learn intro: pull from pre-built queue
    if _mode == "learn" and _learn_queue:
        _current_target = _learn_queue.pop(0)
        _show_prompt = True
        return

    # Otherwise: weighted random selection
    from .rendering.colors import DISPLAY_COLORS
    svg_paths = load_svg_paths(default_first=True)
    if not svg_paths or not DISPLAY_COLORS:
        return
    shape_names = [s[0] for s in svg_paths]
    combos = [(col, sh) for col in DISPLAY_COLORS for sh in shape_names]
    weights = [_weights.get(k, 1.0) for k in combos]
    _current_target = random.choices(combos, weights=weights, k=1)[0]
    _prompt_job = cron.after("3s", _reveal_prompt)


def _build_learn_queue():
    """Build first 10 items ensuring every color and every shape appears."""
    from .rendering.colors import DISPLAY_COLORS
    shape_names = [s[0] for s in load_svg_paths(default_first=True)]
    if not DISPLAY_COLORS or not shape_names:
        return []

    colors = list(DISPLAY_COLORS)
    shapes = list(shape_names)
    random.shuffle(colors)
    random.shuffle(shapes)

    queue = []
    # Pair up colors and shapes to maximize coverage
    for i in range(_LEARN_INTRO_COUNT):
        color = colors[i % len(colors)]
        shape = shapes[i % len(shapes)]
        queue.append((color, shape))
    random.shuffle(queue)
    return queue


def _show(mode="game"):
    global _canvas, _poll_job, _highlight, _mode, _learn_count, _learn_queue, _streak, _done
    _hide()
    _mode = mode
    _learn_count = 0
    _streak = 0
    _done = False
    _learn_queue = _build_learn_queue() if mode == "learn" else []
    _highlight = (None, None)
    _pick_target()
    screen = ui.main_screen()
    _canvas = Canvas.from_screen(screen)
    _canvas.register("draw", _on_draw)
    _canvas.freeze()
    _poll_job = cron.interval("16ms", _poll_mouse)
    _ctx_tags.tags = ["user.clock_ring_showing"]


def _hide():
    global _canvas, _poll_job, _prompt_job, _error_job, _show_error
    _ctx_tags.tags = []
    if _error_job:
        cron.cancel(_error_job)
        _error_job = None
    _show_error = False
    if _prompt_job:
        cron.cancel(_prompt_job)
        _prompt_job = None
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


def _set_highlight(color=None, shape=None):
    global _highlight
    _highlight = (color, shape)
    if _canvas:
        _canvas.freeze()


def _flash_error():
    global _show_error, _error_job
    _show_error = True
    if _error_job:
        cron.cancel(_error_job)
    _error_job = cron.after("500ms", _clear_error)
    if _canvas:
        _canvas.freeze()


def _clear_error():
    global _show_error, _error_job
    _show_error = False
    _error_job = None
    if _canvas:
        _canvas.freeze()


def _show_error_persistent():
    """Show red error state — stays until user says the correct answer."""
    global _show_error, _show_prompt
    _show_error = True
    _show_prompt = True  # reveal the answer so they can correct
    if _error_job:
        cron.cancel(_error_job)
    if _canvas:
        _canvas.freeze()


def _adjust_weight(combo, delta):
    """Adjust spaced repetition weight for a combo. Min 0.1."""
    _weights[combo] = max(0.1, _weights.get(combo, 1.0) + delta)


def _select(color: str, shape: str):
    """Highlight a color+shape combo, or advance if it matches the target."""
    global _streak, _done, _learn_count, _learn_queue
    if not _canvas or _done:
        return False
    if _current_target and (color, shape) == _current_target:
        if _show_error:
            _clear_error()  # was in error state — correct answer clears it
        elif not _show_prompt:
            _adjust_weight(_current_target, -0.3)
        # Track streak after intro phase
        if _mode == "learn" and _learn_count > _LEARN_INTRO_COUNT:
            _streak += 1
            if _streak >= _LEARN_STREAK_TARGET:
                _done = True
                if _canvas:
                    _canvas.freeze()
                return True
        _pick_target()
        _set_highlight(None, None)
    else:
        # Wrong — boost target weight, reset streak, stay on same target
        if _current_target:
            _adjust_weight(_current_target, 0.5)
        if _mode == "learn" and _learn_count <= _LEARN_INTRO_COUNT:
            _learn_count = 0
            _learn_queue = _build_learn_queue()
        elif _mode == "learn":
            _streak = 0
        _show_error_persistent()
        _set_highlight(color, shape)
    return True


@mod.action_class
class Actions:
    def circle_info_show():
        """Show the circle info game panel"""
        _show("game")

    def circle_info_learn():
        """Show the circle info learn panel"""
        _show("learn")

    def circle_info_hide():
        """Hide the circle info panel"""
        _hide()

    def circle_info_highlight_color(color: str):
        """Highlight all shapes of a given color (partial = wrong in learn mode)"""
        if _mode == "learn" and _canvas and _current_target:
            # Partial command in learn mode counts as wrong
            _select(color, "")
        else:
            _set_highlight(color=color)

    def circle_info_highlight_shape(shape: str):
        """Highlight all instances of a given shape (partial = wrong in learn mode)"""
        if _mode == "learn" and _canvas and _current_target:
            _select("", shape)
        else:
            _set_highlight(shape=shape)
