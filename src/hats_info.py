"""Hats info panel - renders cursorless hat SVGs with mouse clock colors."""

from talon import Context, Module, ui, ctrl, cron
from talon.canvas import Canvas
from talon.skia import Path, RoundRect
from talon.ui import Rect

from .rendering.svg_loader import load_svg_paths

mod = Module()
_ctx_tags = Context()

_canvas = None
_poll_job = None
_shape_positions = {}  # {(color_name, shape_spoken_name): (x, y)}


def _on_draw(c):
    svg_paths = load_svg_paths()
    if not svg_paths:
        c.paint.color = "ff0000"
        c.paint.textsize = 24
        c.draw_text("No SVGs found", 100, 100)
        return

    scale = 0.75
    svg_w = 12
    svg_h = 9
    spacing = 10
    row_gap = 20

    from .rendering.colors import COLOR_REGISTRY, DISPLAY_COLORS
    colors = [(name, COLOR_REGISTRY[name][:6]) for name in DISPLAY_COLORS]
    _shape_positions.clear()

    mx, my = ctrl.mouse_pos()
    scatter_step = 12
    header_height = 3 * scatter_step + 8  # staggered headers + gap

    # Calculate total grid dimensions to center on mouse
    col_step = svg_w * scale + spacing
    row_step = svg_h * scale + row_gap
    total_w = len(colors) * col_step
    total_h = header_height + len(svg_paths) * row_step

    start_x = mx - total_w / 2
    start_y = my - total_h / 2

    # Draw staggered color names at the top
    for col_i, (color_name, color_hex) in enumerate(colors):
        col_x = start_x + col_i * col_step
        scatter_y = start_y + (col_i % 3) * scatter_step
        c.paint.textsize = 11
        c.paint.style = c.paint.Style.FILL
        text_w, _ = c.paint.measure_text(color_name)
        bg_color = "ddddddcc" if color_name == "black" else "222222cc"
        c.paint.color = bg_color
        c.draw_rrect(RoundRect.from_rect(
            Rect(col_x - 2, scatter_y - 1, text_w + 4, 13),
            x=2, y=2,
        ))
        c.paint.color = color_hex
        c.draw_text(color_name, col_x, scatter_y + 10)

    # Shapes start below the header area
    shapes_y = start_y + header_height

    for row_i, (name, d, fill_rule) in enumerate(svg_paths):
        y = shapes_y + row_i * (svg_h * scale + row_gap)

        # Draw one shape per color along the line
        shape_x = start_x
        for col_i, (color_name, color_hex) in enumerate(colors):
            path = Path.from_svg(d)
            if fill_rule == "evenodd":
                path.fill_type = Path.FillType.EVENODD
            _shape_positions[(color_name, name)] = (shape_x + svg_w * scale / 2 - mx, y + svg_h * scale / 2 - my)
            c.save()
            c.translate(shape_x, y)
            c.scale(scale, scale)
            c.paint.color = color_hex
            c.paint.style = c.paint.Style.FILL
            c.draw_path(path)
            # Stroke outline
            c.paint.color = "ffffff" if color_name in ("black", "center") else "000000"
            c.paint.style = c.paint.Style.STROKE
            c.paint.stroke_width = 0.4
            c.draw_path(path)
            c.restore()
            shape_x += svg_w * scale + spacing

        # Label after shapes
        c.paint.textsize = 14
        c.paint.style = c.paint.Style.FILL
        text_w, _ = c.paint.measure_text(name)
        c.paint.color = "222222cc"
        c.draw_rrect(RoundRect.from_rect(
            Rect(shape_x - 4, y - 2, text_w + 8, 16),
            x=3, y=3,
        ))
        c.paint.color = "00ddff"
        c.draw_text(name, shape_x, y + 11)



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
    """Move mouse to a color+shape position on the info panel."""
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
    def hats_info_show():
        """Show the hats info panel"""
        _show()

    def hats_info_hide():
        """Hide the hats info panel"""
        _hide()
