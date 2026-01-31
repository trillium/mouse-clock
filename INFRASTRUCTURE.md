# Mouse Navigation Infrastructure

*Shared low-level primitives for MouseClock and related navigation systems*

This document identifies common functions and utilities that can be shared across the various mouse navigation features described in FEATURES.md: MouseClock, Lettered Line Intersection Overlay, Spiral Nudge Navigation, Concentric Box Targeting, and Parrot Sound Actions.

---

## 1. Geometry Primitives

Core mathematical functions used by multiple systems.

### 1.1 Angle and Direction

| Function | Description | Used By |
|----------|-------------|---------|
| `letter_to_angle(letter)` | Convert clock letter (A–L) to degrees (A=30°, B=60°, ..., L=360°/0°) | MouseClock, Concentric Box, Line Overlay |
| `number_to_angle(hour)` | Convert clock hour (1–12) to degrees | MouseClock, Concentric Box |
| `angle_to_letter(degrees)` | Reverse mapping from angle to nearest clock letter | Spiral Nudge (for feedback) |
| `normalize_angle(degrees)` | Normalize angle to 0–360 range | All directional systems |
| `opposite_angle(degrees)` | Return angle + 180° (normalized) | MouseClock reverse command |
| `average_angles(angle_list)` | Compute average of multiple angles (handling wraparound) | MouseClock multi-letter commands |

### 1.2 Point and Vector Math

| Function | Description | Used By |
|----------|-------------|---------|
| `move_in_direction(origin, angle, distance)` | Compute point at given angle and distance from origin | MouseClock, Spiral Nudge, Concentric Box |
| `distance_between(point_a, point_b)` | Euclidean distance between two points | Spiral Nudge (bounds check), history |
| `point_on_circle(center, radius, angle)` | Point on circle perimeter at given angle | MouseClock, Concentric Box |
| `clamp_to_bounds(point, rect)` | Constrain point to stay within rectangle | All systems (screen bounds) |

### 1.3 Intersection Calculations

| Function | Description | Used By |
|----------|-------------|---------|
| `ray_circle_intersection(origin, angle, center, radius)` | Where a ray from origin intersects a circle | MouseClock |
| `ray_rect_intersection(origin, angle, rect)` | Where a ray from origin intersects an axis-aligned rectangle | Concentric Box |
| `ray_line_intersection(ray_origin, ray_angle, line_start, line_end)` | General ray-to-line-segment intersection | Line Overlay, Concentric Box |

---

## 2. Drawing Primitives

Canvas rendering utilities shared across overlay systems.

### 2.1 Basic Shapes

| Function | Description | Used By |
|----------|-------------|---------|
| `draw_line(canvas, start, end, color, thickness, dashed=False)` | Draw a line segment, optionally dashed | All overlay systems |
| `draw_circle(canvas, center, radius, color, thickness, filled=False)` | Draw circle outline or filled | MouseClock |
| `draw_rect(canvas, rect, color, thickness, filled=False)` | Draw rectangle outline or filled | Concentric Box, Line Overlay |
| `draw_dot(canvas, center, radius, color)` | Draw a small filled circle (marker) | All systems (intersection markers) |
| `draw_cross(canvas, center, size, color, thickness)` | Draw a + or × marker | MouseClock, Concentric Box |
| `draw_text(canvas, position, text, color, font_size, anchor="center")` | Render text label | All systems (labels) |

### 2.2 Composite Shapes

| Function | Description | Used By |
|----------|-------------|---------|
| `draw_ray(canvas, origin, angle, length, color, thickness, dashed=False)` | Draw a ray from origin at angle | MouseClock, Concentric Box |
| `draw_concentric_circles(canvas, center, radii, colors, thickness)` | Draw multiple circles with different colors | MouseClock |
| `draw_concentric_rects(canvas, center, sizes, colors, thickness)` | Draw multiple rectangles with different colors | Concentric Box |
| `draw_clock_rays(canvas, center, length, color, thickness, dashed=False)` | Draw all 12 clock-hour rays | MouseClock, Concentric Box |

### 2.3 Canvas Management

| Function | Description | Used By |
|----------|-------------|---------|
| `create_overlay_canvas(screen)` | Create a transparent overlay canvas for a screen | All overlay systems |
| `clear_canvas(canvas)` | Clear all drawings from canvas | All overlay systems |
| `refresh_canvas(canvas)` | Trigger redraw (freeze) | All overlay systems |
| `close_canvas(canvas)` | Dispose of canvas resources | All overlay systems |
| `get_canvas_for_point(point, canvases)` | Find which canvas contains a given point (multi-monitor) | All overlay systems |

---

## 3. Color Management

Centralized color definitions and utilities.

### 3.1 Color Registry

A shared color registry that maps color names to hex values, used consistently across all systems:

```
COLOR_REGISTRY = {
    "red": "ff0000ff",
    "blue": "0000ffff",
    "green": "00ff00ff",
    "yellow": "ffd700ff",
    "purple": "800080ff",
    "pink": "ff00ffff",
    "gold": "ffa500ff",
    "center": "000000ff",
    ...
}
```

### 3.2 Color Functions

| Function | Description | Used By |
|----------|-------------|---------|
| `get_color(name)` | Look up hex color by name | All systems |
| `get_color_index(name)` | Get numeric index for a color (for ring/box ordering) | MouseClock, Concentric Box |
| `index_to_color(index)` | Reverse lookup from index to color name | MouseClock, Concentric Box |
| `with_alpha(color_hex, alpha)` | Modify alpha channel of a color | All systems (transparency) |
| `contrasting_color(color_hex)` | Return a high-contrast color for text/markers | Label rendering |

---

## 4. Mouse Control Primitives

Low-level cursor manipulation shared across systems.

### 4.1 Position Management

| Function | Description | Used By |
|----------|-------------|---------|
| `get_mouse_position()` | Get current cursor (x, y) | All systems |
| `set_mouse_position(x, y)` | Move cursor to absolute position | MouseClock, Concentric Box, Line Overlay |
| `move_mouse_relative(dx, dy)` | Move cursor by offset | Spiral Nudge |
| `get_screen_for_mouse()` | Get the screen containing the cursor | All systems |
| `get_screen_rect(screen)` | Get bounds of a screen | All systems |

### 4.2 Position History

| Function | Description | Used By |
|----------|-------------|---------|
| `push_position(position)` | Add position to history stack | MouseClock, Spiral Nudge |
| `pop_position()` | Remove and return last position | MouseClock go_back, Spiral reset |
| `peek_position()` | View last position without removing | Spiral Nudge |
| `clear_history()` | Clear all stored positions | All systems (on close) |
| `get_origin()` | Get the starting position for current session | Spiral Nudge |

---

## 5. Input Event Infrastructure

Shared utilities for handling voice and sound triggers.

### 5.1 Debounce and Rate Limiting

| Function | Description | Used By |
|----------|-------------|---------|
| `debounce(callback, min_interval_ms)` | Wrap a callback to enforce minimum time between calls | Parrot sounds, Spiral Nudge |
| `throttle(callback, max_rate_per_sec)` | Limit call frequency | Continuous sound triggers |
| `is_cooling_down(event_type)` | Check if an event type is in cooldown period | All sound-triggered actions |
| `reset_cooldown(event_type)` | Clear cooldown for an event type | Cancel commands |

### 5.2 Sound-to-Action Mapping

| Function | Description | Used By |
|----------|-------------|---------|
| `register_sound_action(sound_label, action, params)` | Map a parrot sound to an action with parameters | Parrot integration |
| `unregister_sound_action(sound_label)` | Remove a sound mapping | Configuration |
| `get_action_for_sound(sound_label)` | Look up action for a sound | Parrot event handler |
| `set_sound_param(sound_label, param_name, value)` | Adjust parameters for a sound mapping | Runtime configuration |

### 5.3 State Guards

| Function | Description | Used By |
|----------|-------------|---------|
| `is_overlay_active(overlay_name)` | Check if a specific overlay is showing | Parrot guards, Spiral guards |
| `any_overlay_active()` | Check if any mouse overlay is active | Sound action guards |
| `get_active_overlay()` | Get name of currently active overlay | Mode switching |
| `require_overlay(overlay_name)` | Decorator/guard that only runs if overlay is active | Action definitions |

---

## 6. Screen and Window Utilities

Multi-monitor and window-aware functions.

| Function | Description | Used By |
|----------|-------------|---------|
| `get_all_screens()` | List all available screens | Canvas setup |
| `get_primary_screen()` | Get the primary/main screen | Default overlay placement |
| `get_active_window_rect()` | Get bounds of focused window | "clock win" command |
| `point_to_screen(point)` | Find which screen contains a point | Multi-monitor support |
| `clamp_to_screen(point, screen)` | Keep point within screen bounds | Spiral Nudge safety |
| `screen_center(screen)` | Get center point of a screen | Default positioning |

---

## 7. Configuration Infrastructure

Shared settings and configuration management.

### 7.1 Settings Registry

| Setting | Type | Default | Used By |
|---------|------|---------|---------|
| `default_radius` | int | 300 | MouseClock, Concentric Box |
| `radius_increment` | int | 20 | widen/narrow commands |
| `min_radius` | int | 20 | Radius bounds |
| `debounce_interval_ms` | int | 150 | Sound triggers |
| `spiral_step_size` | int | 10 | Spiral Nudge |
| `spiral_max_radius` | int | 100 | Spiral Nudge safety |
| `line_thickness` | int | 2 | All drawing |
| `dashed_line_pattern` | list | [5, 3] | Dashed lines |

### 7.2 Configuration Functions

| Function | Description | Used By |
|----------|-------------|---------|
| `get_setting(name)` | Retrieve a setting value | All systems |
| `set_setting(name, value)` | Update a setting at runtime | Voice configuration |
| `reset_setting(name)` | Restore default value | Reset commands |
| `load_settings(file_path)` | Load settings from file | Initialization |
| `save_settings(file_path)` | Persist current settings | Configuration persistence |

---

## 8. Logging and Diagnostics

Shared logging infrastructure for debugging and analysis.

| Function | Description | Used By |
|----------|-------------|---------|
| `log_debug(message)` | Debug-level log entry | All systems |
| `log_info(message)` | Info-level log entry | All systems |
| `log_warning(message)` | Warning-level log entry | All systems |
| `log_separator()` | Visual separator in logs | Session boundaries |
| `log_position(label, x, y)` | Log a position with context | Position tracking |
| `log_action(action_name, params)` | Log an action invocation | Action tracing |
| `get_log_file()` | Get path to current log file | Diagnostics command |

---

## 9. Implementation Notes

### 9.1 Module Organization

Suggested file structure for shared infrastructure:

```
src/
  core/
    geometry.py      # Sections 1.1, 1.2, 1.3
    config.py        # Section 7
    logger.py        # Section 8
  rendering/
    canvas.py        # Section 2.3
    drawing.py       # Sections 2.1, 2.2
    colors.py        # Section 3
  input/
    mouse.py         # Section 4
    debounce.py      # Section 5.1
    sound_actions.py # Section 5.2
    guards.py        # Section 5.3
  util/
    screen.py        # Section 6
```

### 9.2 Existing Code to Refactor

The current MouseClock implementation already contains versions of many of these primitives in:
- `src/core/geometry.py` — angle/direction functions
- `src/core/config.py` — color definitions, settings
- `src/rendering/canvas.py` — drawing functions

These should be reviewed and generalized to support the additional systems.

### 9.3 Talon Integration Layer

All primitives should be pure Python where possible, with a thin Talon integration layer that:
- Wraps `ctrl.mouse_move()`, `ctrl.mouse_pos()` for mouse control
- Wraps `canvas.Canvas` for overlay rendering
- Wraps `ui.screens()`, `ui.active_window()` for screen/window queries
- Provides action decorators for voice command bindings

This separation allows the core logic to be tested independently of Talon.
