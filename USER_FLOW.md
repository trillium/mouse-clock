# Mouse Clock - User Flow Documentation

## Overview

Mouse Clock is a voice-controlled mouse positioning overlay for Talon. This document describes the complete code flow from voice command to screen rendering.

---

## Tags & Contexts

### Tags Defined (`instance.py`)

| Tag | Purpose |
|-----|---------|
| `user.use_mouse_clock` | Enables the mouse clock plugin (set externally) |
| `user.mouse_clock_showing` | Set when overlay is visible |

### Context Activation

```
mouse_clock_always.talon
  └─ tag: user.use_mouse_clock
     (Always active when plugin enabled)

mouse_clock_active.talon
  └─ tag: user.use_mouse_clock
     AND tag: user.mouse_clock_showing
     AND NOT tag: user.mouse_grid_showing
     (Only when clock is visible)

mode_config.talon
  └─ tag: user.use_mouse_clock
     AND tag: user.mouse_clock_showing
     (Mode-specific configuration when visible)
```

---

## Display Modes

Defined in `adapter.py`:

| Constant | Mode | Description |
|----------|------|-------------|
| `DISPLAY_MODE_CIRCLES` | circles | Concentric colored circles |
| `DISPLAY_MODE_GRID` | grid | Letter rows + color columns |
| `DISPLAY_MODE_CLOCK_LETTERS` | clock_letters | Letters at clock positions |

Rotation order: circles → grid → clock_letters → (repeat)

---

## Core User Flows

### Flow 1: "mouse clock" - Activate Display

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ USER SAYS: "mouse clock"                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ TALON FILE: mouse_clock_always.talon                                        │
│ CONTEXT: tag: user.use_mouse_clock                                          │
│ COMMAND: ^mouse clock$                                                       │
│ ACTION: user.mouse_clock_close() → sleep(50ms) → user.mouse_clock_activate()│
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│ actions_core.py               │   │ actions_core.py               │
│ mouse_clock_close()           │   │ mouse_clock_activate()        │
│                               │   │                               │
│ 1. ctx_tags.tags = []         │   │ 1. if not active_canvas:      │
│ 2. adapter.close()            │   │      adapter.setup()          │
│    └─ fade_out(300ms)         │   │ 2. adapter.show()             │
│    └─ _on_fade_out_complete() │   │    └─ register("draw")        │
│       └─ close canvases       │   │    └─ pulse animation start   │
│       └─ active = False       │   │ 3. clear_state()              │
└───────────────────────────────┘   │ 4. ctx_tags.tags = [showing]  │
                                    └───────────────────────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ RESULT: Clock overlay displayed, centered on mouse position                  │
│ STATE: active=True, tags=[user.mouse_clock_showing]                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 2: "clock letters" - Switch Display Mode

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ USER SAYS: "clock letters"                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ TALON FILE: mouse_clock_always.talon                                        │
│ CONTEXT: tag: user.use_mouse_clock                                          │
│ COMMAND: clock letters                                                       │
│ ACTION: user.mouse_clock_mode_clock_letters()                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ actions_display.py                                                           │
│ mouse_clock_mode_clock_letters()                                            │
│                                                                              │
│ → _set_mode_and_refresh(DISPLAY_MODE_CLOCK_LETTERS)                         │
│                                                                              │
│   1. adapter.set_display_mode("clock_letters")                              │
│      └─ saves to settings.json                                              │
│                                                                              │
│   2. if not active:                                                          │
│        adapter.setup() → adapter.show()                                      │
│        ctx_tags.tags = [showing]                                            │
│      else:                                                                   │
│        canvas.freeze() → triggers redraw                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ adapter.py - draw(canvas_obj)                                               │
│                                                                              │
│ elif self._display_mode == DISPLAY_MODE_CLOCK_LETTERS:                      │
│     rect = canvas_obj.rect                                                   │
│     screen_rect = (rect.x, rect.y, rect.x + rect.width, rect.y + rect.height)│
│     draw_clock_letters_overlay(canvas_obj, screen_rect, alpha=self._alpha)  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ features/clock_letters/render.py                                            │
│ draw_clock_letters_overlay(canvas, screen_rect, alpha)                      │
│                                                                              │
│ 1. Get colors from get_clock_letters_colors()                               │
│ 2. Get letters from get_clock_letters_letters()                             │
│ 3. Calculate row_positions (letters on Y axis)                              │
│ 4. Calculate col_positions (colors on X axis)                               │
│ 5. For each letter/color: draw_rect() + draw_text()                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ RESULT: Letters displayed in colored grid                                    │
│ STATE: _display_mode="clock_letters"                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 3: "clock off" - Close Display

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ USER SAYS: "clock off"                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ TALON FILE: mouse_clock_always.talon                                        │
│ CONTEXT: tag: user.use_mouse_clock                                          │
│ COMMAND: clock off                                                           │
│ ACTION: user.mouse_clock_close()                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ actions_core.py                                                              │
│ mouse_clock_close()                                                          │
│                                                                              │
│ 1. ctx_tags.tags = []  ← Clears showing + info_mode tags                    │
│ 2. adapter.close()                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ adapter.py - close()                                                         │
│                                                                              │
│ 1. _fade_animator._pulsing = False  ← Stop pulse animation                  │
│ 2. _fade_animator.fade_out(300ms, on_complete=_on_fade_out_complete)        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ (after 300ms fade)
┌─────────────────────────────────────────────────────────────────────────────┐
│ adapter.py - _on_fade_out_complete()                                        │
│                                                                              │
│ for canvas_obj in self.canvases:                                            │
│     canvas_obj.unregister("draw", self.draw)                                │
│     canvas_obj.close()                                                       │
│ self.canvases = []                                                           │
│ self.active_canvas = None                                                    │
│ self.active = False                                                          │
│ set_overlay_inactive("mouse_clock")                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ RESULT: Overlay hidden with fade animation                                   │
│ STATE: active=False, canvases=[], tags=[]                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## File Reference

### Talon Command Files

| File | Context | Purpose |
|------|---------|---------|
| `mouse_clock_always.talon` | `tag: user.use_mouse_clock` | Always-active commands (activate, mode switch, close) |
| `mouse_clock_active.talon` | `+ tag: user.mouse_clock_showing` | Movement, clicks, radius adjustment |
| `mode_config.talon` | `+ tag: user.mouse_clock_showing` | Mode-specific configuration |

### Python Files

| File | Purpose |
|------|---------|
| `instance.py` | Tag definitions, singleton instance management |
| `adapter.py` | Canvas management, display state, draw callback |
| `actions_core.py` | activate(), close(), toggle(), radius actions |
| `actions_move.py` | Movement logic, repeat detection, opposite |
| `actions_display.py` | Mode switching, display cycling |
| `actions_grid.py` | Grid-specific targeting actions |

### Rendering Files

| File | Purpose |
|------|---------|
| `features/clock_letters/render.py` | Clock letters overlay drawing |
| `features/grid/render.py` | Grid overlay drawing |
| `rendering/canvas.py` | Circles mode drawing |
| `rendering/animation.py` | FadeAnimator for fade effects |

---

## State Machine

```
                    ┌─────────────┐
                    │  INACTIVE   │
                    │ active=False│
                    │ canvases=[] │
                    │ tags=[]     │
                    └──────┬──────┘
                           │ activate()
                           ▼
                    ┌─────────────┐
                    │ FADING IN   │
                    │ (pulse)     │
                    │ alpha: 255→0│
                    │ →255 (loop) │
                    └──────┬──────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────┐
│                      ACTIVE                           │
│  active=True                                          │
│  tags=[user.mouse_clock_showing, ...]                │
│  draw() called per frame                              │
│                                                       │
│  ┌─────────┬─────────┬─────────┐                     │
│  │ circles │  grid   │ letters │                     │
│  └─────────┴─────────┴─────────┘                     │
│        (mode switching via set_mode)                  │
└──────────────────────────┬───────────────────────────┘
                           │ close()
                           ▼
                    ┌─────────────┐
                    │ FADING OUT  │
                    │ (300ms)     │
                    │ alpha→0     │
                    └──────┬──────┘
                           │ _on_fade_out_complete()
                           ▼
                    ┌─────────────┐
                    │  INACTIVE   │
                    └─────────────┘
```

---

## Voice Commands Quick Reference

### Always Available (when plugin enabled)

| Command | Action |
|---------|--------|
| `mouse clock` | Refresh/activate clock |
| `clock off` | Close clock |
| `clock circles` | Switch to circles mode |
| `clock grid` | Switch to grid mode |
| `clock letters` | Switch to clock letters mode |
| `clock display next` | Cycle to next mode |
| `clock display previous` | Cycle to previous mode |

### When Clock is Showing

| Command | Action |
|---------|--------|
| `<letters> <colors>` | Move mouse to position |
| `widen` / `narrow` | Adjust radius |
| `reset` | Set radius to 300 |
| `touch` | Left click + close |
| `righty` | Right click + close |
| `reverse` | Move opposite direction |

---

## Key Implementation Details

1. **Multi-Monitor Support**: One canvas per screen via `Canvas.from_screen(screen)`

2. **Tag-Driven Contexts**: Commands gated by tags, not separate Context objects

3. **Fade Animation**: Uses `FadeAnimator` class with pulse (show) and fade_out (close)

4. **Mode Persistence**: Display mode saved to `settings.json` and restored on reload

5. **Repeat Detection**: Same command twice recenters and reapplies (for stepping)

6. **Canvas Rect for Bounds**: Each screen overlay uses `canvas_obj.rect` for correct positioning
