"""Clock settings overlay — DismissibleOverlay-based settings panel."""

from talon import ui
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.ui import Rect

from trillium.utils.overlay_kit import (
    DismissibleOverlay, draw_dim_backdrop, draw_panel_frame, draw_separator,
)
from .core.config import (
    get_setting, set_setting, get_active_colors, get_active_letters,
    get_active_styles, _DEFAULTS,
)
from .core.constants import DISPLAY_MODES
from .features.clock_letters.config import set_column_preset
from .features.clock_letters.column_presets import PRESET_NAMES

# ── Style constants ──
DIM_BG, PANEL_BG, PANEL_BORDER = "000000cc", "1a2e2eee", "4a8a7a"
CORNER_RADIUS, PANEL_PAD = 16, 40
TEXT_COLOR, DIM_COLOR, ACCENT = "ffffffff", "aaaaaa", "5ab5a0"
HEADER_COLOR, LINE_COLOR, VALUE_COLOR = "ffffffff", "3a5a5a", "aa44ffff"
HEADER_SIZE, ROW_HEIGHT, FONT_SIZE = 28, 28, 15
NUM_SIZE, HINT_SIZE, LABEL_SIZE = 16, 13, 13
NUM_COL_W, LABEL_COL_W = 32, 180

# Formatters
_fi = lambda v: str(int(v))
_ff = lambda v: f"{v:.1f}"
_fm = lambda v: f"{int(v)}ms"
_fs = lambda v: str(v)

# Settings spec: tuples of (key, label, default, increment, format_fn)
# or section headers as plain strings
SETTINGS_SPEC = [
    "General",
    ("display_mode",            "Display Mode", "dense_grid", DISPLAY_MODES, _fs),
    ("default_radius",          "Radius",         300,          50,    _fi),
    ("min_radius",              "Min Radius",      20,           5,    _fi),
    ("debounce_interval_ms",    "Debounce",       150,          25,    _fm),
    ("line_thickness",          "Line Thickness",    2,           1,    _fi),
    ("dot_radius",              "Dot Size",          5,           1,    _fi),
    "Dense Grid",
    ("dense_grid_spacing_x",   "Spacing X",        14,           1,    _fi),
    ("dense_grid_spacing_y",   "Spacing Y",        14,           1,    _fi),
    "Clock Ring",
    ("clock_ring_ring_spacing", "Ring Spacing",   18.0,         2.0,  _ff),
    ("clock_ring_fade_out_ms",  "Fade Out",       4000,         500,  _fm),
    ("clock_ring_fade_in_ms",   "Fade In",        1000,         250,  _fm),
    ("clock_ring_fade_delay_ms","Fade Delay",     2000,         500,  _fm),
    ("clock_ring_fade_bg_max",  "BG Max",          0.7,         0.1,  _ff),
    ("clock_ring_fade_bg_min",  "BG Min",          0.1,         0.1,  _ff),
    ("clock_ring_fade_icon_min","Icon Min",        0.3,         0.1,  _ff),
    "Clock Letters",
    ("clock_letters_column_preset", "Column Layout", "reference", PRESET_NAMES, _fs),
]

# Build flat list of adjustable settings (excluding section headers) for indexing
_ADJUSTABLE = [s for s in SETTINGS_SPEC if isinstance(s, tuple)]


def _get_default(key, spec_default):
    """Get default from _DEFAULTS if available, else use spec default."""
    return _DEFAULTS.get(key, spec_default)


def _cycle_list(current, values, direction):
    """Cycle through a list of values."""
    try:
        idx = values.index(current)
    except ValueError:
        idx = 0
    return values[(idx + direction) % len(values)]


_CUSTOM_SETTERS = {
    "clock_letters_column_preset": lambda value: set_column_preset(value),
}


def adjust(index: int, direction: int):
    """Adjust setting at 1-based index. direction: 1=increase, -1=decrease."""
    if index < 1 or index > len(_ADJUSTABLE):
        return
    key, _, default, increment, _ = _ADJUSTABLE[index - 1]
    current = get_setting(key, _get_default(key, default))
    if isinstance(increment, list):
        new_val = _cycle_list(current, increment, direction)
    else:
        new_val = current + increment * direction
        if isinstance(default, float):
            new_val = round(new_val, 2)
        elif isinstance(default, int):
            new_val = int(new_val)
    if key in _CUSTOM_SETTERS:
        _CUSTOM_SETTERS[key](new_val)
    else:
        set_setting(key, new_val, persist=True)
    _overlay.freeze()


def reset(index: int):
    """Reset setting at 1-based index to its default."""
    if index < 1 or index > len(_ADJUSTABLE):
        return
    key, _, default, _, _ = _ADJUSTABLE[index - 1]
    set_setting(key, _get_default(key, default), persist=True)
    _overlay.freeze()


# ── Drawing ──

def _on_draw(c: SkiaCanvas, overlay: DismissibleOverlay):
    screen = ui.main_screen()
    sr = screen.rect
    draw_dim_backdrop(c, sr, DIM_BG)

    section_count = sum(1 for s in SETTINGS_SPEC if isinstance(s, str))
    row_count = len(_ADJUSTABLE)
    panel_w = sr.width * 0.40
    panel_h = (
        PANEL_PAD + HEADER_SIZE + 12 + ROW_HEIGHT
        + ROW_HEIGHT * row_count + ROW_HEIGHT * section_count + 16
        + ROW_HEIGHT * 3 + 12 + HINT_SIZE + PANEL_PAD
    )
    panel_x = sr.x + (sr.width - panel_w) / 2
    panel_y = sr.y + (sr.height - panel_h) / 2
    panel_rect = Rect(panel_x, panel_y, panel_w, panel_h)
    overlay.set_panel_rect(panel_rect)
    draw_panel_frame(c, panel_rect, CORNER_RADIUS, PANEL_BG, PANEL_BORDER)

    c.save()
    c.clip_rect(panel_rect)
    cx = panel_x + PANEL_PAD
    cy = panel_y + PANEL_PAD
    content_w = panel_w - PANEL_PAD * 2

    # Header
    c.paint.textsize = HEADER_SIZE
    c.paint.color = HEADER_COLOR
    c.draw_text("Clock Settings", cx, cy + HEADER_SIZE)
    overlay.draw_close_hint(c, panel_x, panel_y, panel_w, PANEL_PAD)
    cy += HEADER_SIZE + 12

    # Column headers
    c.paint.textsize = FONT_SIZE
    c.paint.color = DIM_COLOR
    c.draw_text("#", cx, cy + FONT_SIZE)
    c.draw_text("Setting", cx + NUM_COL_W, cy + FONT_SIZE)
    c.draw_text("Value", cx + NUM_COL_W + LABEL_COL_W, cy + FONT_SIZE)
    cy += ROW_HEIGHT
    draw_separator(c, cx, cx + content_w, cy - 6, LINE_COLOR)

    # Setting rows with section headers
    row_num = 0
    for entry in SETTINGS_SPEC:
        if isinstance(entry, str):
            # Section header
            cy += 6
            c.paint.textsize = LABEL_SIZE
            c.paint.color = ACCENT
            c.paint.font.embolden = True
            c.draw_text(f"── {entry} ──", cx, cy + LABEL_SIZE)
            c.paint.font.embolden = False
            cy += ROW_HEIGHT
            continue
        key, label, default, _inc, fmt_fn = entry
        row_num += 1
        current = get_setting(key, _get_default(key, default))
        # Row number
        c.paint.textsize = NUM_SIZE
        c.paint.color = ACCENT
        c.paint.font.embolden = True
        c.draw_text(str(row_num), cx, cy + FONT_SIZE)
        c.paint.font.embolden = False
        # Label
        c.paint.textsize = FONT_SIZE
        c.paint.color = TEXT_COLOR
        c.draw_text(label, cx + NUM_COL_W, cy + FONT_SIZE)
        # Value (highlighted if non-default)
        is_default = current == _get_default(key, default)
        c.paint.color = DIM_COLOR if is_default else VALUE_COLOR
        c.paint.font.embolden = not is_default
        c.draw_text(fmt_fn(current), cx + NUM_COL_W + LABEL_COL_W, cy + FONT_SIZE)
        c.paint.font.embolden = False
        cy += ROW_HEIGHT

    # Separator before list counts
    cy += 4
    draw_separator(c, cx, cx + content_w, cy, LINE_COLOR)
    cy += 12

    # Read-only list counts
    for name, count in [
        ("Active Colors", len(get_active_colors())),
        ("Active Letters", len(get_active_letters())),
        ("Active Styles", len(get_active_styles())),
    ]:
        c.paint.textsize = LABEL_SIZE
        c.paint.color = DIM_COLOR
        c.draw_text(f"{name}: {count}", cx, cy + LABEL_SIZE)
        cy += ROW_HEIGHT

    # Command hint
    cy += 4
    c.paint.textsize = HINT_SIZE
    c.paint.color = DIM_COLOR
    c.draw_text(
        '"increase/decrease/reset <n>"  \u00b7  "clock settings close" or esc',
        cx, cy + HINT_SIZE,
    )
    c.restore()


_on_hide_callback = None
_overlay = DismissibleOverlay(
    on_draw=_on_draw, auto_hide="60s",
    on_hide=lambda: _on_hide_callback and _on_hide_callback(),
)


def set_on_hide(callback):
    """Register a callback for when the overlay is dismissed."""
    global _on_hide_callback
    _on_hide_callback = callback


def show():
    _overlay.show()

def hide():
    _overlay.hide()

def is_showing() -> bool:
    return _overlay.is_showing
