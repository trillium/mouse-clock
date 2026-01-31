# MouseClock Features

## Overview

TBD

## Core Navigation

TBD

## Visual Overlay

TBD

## Configuration and Settings

TBD

## Integration with Talon

TBD

## Planned Extensions

### Parrot Sound Actions Integration

A non-verbal sound integration that allows controlling MouseClock via hiss, shush, and other parrot-detected sounds. This enables hands-free radius adjustments without interrupting speech.

**Initial Sound Mappings:**
- `hiss` → widen MouseClock radius (small increment)
- `shush` → narrow MouseClock radius (small decrement)

**Design Goals:**
- Extensible mapping system so additional sounds can be bound to actions later
- Configurable parameters (e.g., widen/narrow amount per sound)
- Works only when MouseClock is active (respects `user.mouse_clock_showing` tag)

### Possible Future Sound-to-Action Mappings

- Toggle MouseClock visibility on/off
- Recenter the clock at current mouse position
- Jump to previous or next stored position in history
- Execute touch/click at current position
- Switch between navigation modes (MouseClock vs centroid grid vs other)
- Cycle through radius presets (small/medium/large)
- Undo last movement (go back)

### Implementation Approach (High Level)

**Architecture:**
- A small adapter module (`parrot_mouse_clock.py` or similar) that listens to parrot events
- Calls existing `user.mouse_clock_*` actions—no changes to core MouseClock logic needed
- Talon file with parrot bindings, guarded by appropriate tags

**Configuration:**
- Mapping from sound labels to MouseClock actions stored in a simple dict or settings
- Adjustable parameters per action (e.g., `hiss_widen_amount = 15`, `shush_narrow_amount = 15`)
- Easy to add new sound→action pairs without modifying core code

**Safety Considerations:**
- Debounce repeated sounds to prevent runaway radius changes from sustained hiss/shush
- Minimum interval between accepted sound events (e.g., 100-200ms)
- Quick cancel mechanism if sounds are mis-detected
- Only active when MouseClock is showing to avoid accidental triggers

---

## Lettered Line Intersection Overlay

*Future design — a complementary screen navigation system*

### Concept

A system that divides the screen into horizontal bands labeled with letters (e.g., A, B, C, D, E). Speaking a letter activates a horizontal line representing that Y-axis sector. Once a horizontal line is active, vertical lines are drawn that visually intersect it; these vertical lines are color-coded and may be individually addressable in later iterations.

The intended use is to quickly identify and mark likely problem or focus areas at the intersections of a chosen horizontal band and one or more vertical markers—useful for debugging UI layouts, targeting screen regions, or guiding attention during screen sharing.

### Core Drawing Primitive

A utility that can render straight horizontal or vertical lines in a specified color, with an optional length parameter:

- **Axis**: horizontal or vertical
- **Color**: configurable per line
- **Length behavior**:
  - If length is omitted, the line spans the full viewport along its axis
  - If length is provided, the line is drawn to that distance from its origin
- **Origin**: starting point for partial-length lines (e.g., center, edge, or cursor position)

### Parameters and Behavior

- **Togglable**: Lines should be togglable on/off by voice command (e.g., "line alpha on", "line alpha off")
- **Configurable appearance**:
  - Line color (per line or per category)
  - Line thickness / stroke width
  - Optional transparency/alpha
- **Bulk clear**: A command to clear all active lines at once (e.g., "lines off", "clear lines")
- **Layer ordering**: Lines should render above normal content but below other overlays like MouseClock or cursor indicators

### Possible Voice Commands (Sketch)

- `line <letter>` — activate horizontal line for that band
- `line <letter> off` — deactivate that horizontal line
- `verticals on` / `verticals off` — toggle vertical intersection markers
- `lines off` / `clear lines` — remove all active lines

### Integration Considerations

- Could share rendering infrastructure with MouseClock (canvas, colors, stroke utilities)
- Should respect screen/window boundaries and multi-monitor setups
- May eventually integrate with MouseClock for hybrid navigation (e.g., "line C" + clock-based fine positioning within that band)

---

## Spiral Nudge Navigation

*Future design — sound-driven cursor micro-positioning*

### Concept

A low-level infrastructure that nudges the mouse relative to its current position, moving it stepwise in a spiral pattern. The idea is to provide fine-grained cursor adjustment without requiring precise voice commands or manual input—useful when an overlay like MouseClock gets you close but not quite on target.

### Behavior

When triggered (e.g., by hiss or shush via parrot), the mouse moves through a spiral path around its starting point. Each nudge advances the cursor one step along the spiral, causing overlays like MouseClock to re-render at the new position. The user continues triggering nudges until an intersection or targeting indicator covers the intended click area.

This creates a "search pattern" around the original position, systematically covering nearby pixels without requiring the user to specify exact directions.

### Relationship to Existing Talon

Talon already provides cursor-move-relative capabilities (e.g., `ctrl.mouse_move()` with relative offsets). This system builds a structured spiral trajectory on top of those primitives, maintaining state about the current spiral position and calculating the next offset for each nudge.

### Parameters

- **Step size**: Distance in pixels per nudge (e.g., 5px, 10px)
- **Spiral growth rate**: How quickly the radius increases per revolution (e.g., add N pixels per full rotation)
- **Direction**: Clockwise or counterclockwise; could support alternation patterns (spiral out, then back in)
- **Maximum radius / safety bounds**: Limit how far the cursor can drift from the starting point (e.g., 100px max radius) to prevent losing the target area entirely
- **Starting angle**: Initial direction for the first nudge (e.g., 0° = right, 90° = down)

### Integration with Parrot Sounds

- **Example mapping**:
  - `hiss` → start or continue outward spiral (advance to next position)
  - `shush` → pause, reverse direction, or step inward toward origin
- **Configurable**: Sound-to-nudge behavior should be adjustable so users can customize which sounds trigger which spiral actions
- **Extensible**: Other sounds (pop, cluck, etc.) could be mapped to actions like "jump back to origin" or "confirm position"

### Safety and UX Considerations

- **Overlay guard**: Should only run while a relevant overlay (like MouseClock) is active; disabled when no targeting UI is visible
- **Quick cancel**: Provide a voice command (e.g., "stop", "cancel") or sound to immediately halt spiral motion and optionally return to origin
- **Debounce**: Enforce minimum interval between accepted sound triggers to avoid runaway motion from sustained or rapidly repeated sounds
- **Visual feedback**: Consider showing a faint trail or origin marker so the user knows where the spiral started and how far they've drifted
- **Reset command**: Allow returning to the spiral origin without closing the overlay (e.g., "spiral reset" or a specific sound)

---

## Concentric Box Targeting

*Future design — rectangular targeting zones with clock-style directionals*

### Concept

Instead of (or in addition to) concentric circles, render concentric squares or rectangles centered at the cursor, each with a distinct color. Along the usual MouseClock directional rays (the same angles as the clock hours A–L), draw dashed guide lines that intersect these colored boxes. The effective target point is the intersection between a chosen direction and a chosen box color.

For example, saying "gold nine" would target the intersection of the "gold" box boundary and the direction corresponding to 9 o'clock (letter I).

### Visual Details

- **Box geometry**: Axis-aligned rectangles or squares, growing outward from center in discrete steps. Can be uniform squares or aspect-ratio-matched rectangles that fit the screen/window shape.
- **Color coding**: Each ring/box has a stable, distinct color (e.g., innermost = red, next = blue, then green, gold, purple). Colors should have good contrast and be easily distinguishable.
- **Labels**: Optionally display color names or short labels near each box boundary for quick reference.
- **Directional guides**: Thinner, dashed lines radiating from center at each clock-hour angle. These are visual guides, not heavy strokes—meant to help the eye find intersections without cluttering the display.
- **Intersection markers**: Small dots or crosses at the intersection points where directional rays meet box boundaries, making target points visually obvious.

### Parameters and Behavior

- **Number of boxes**: Configurable count (e.g., 3, 5, 7 concentric boxes)
- **Size progression**: Relative sizes of each box—could be linear (equal steps) or geometric (each box N% larger than previous)
- **Color mapping**: Dict or list mapping box index to color name and hex value
- **Integration with radius**: Map existing MouseClock radius/step concepts to box boundaries where possible, so widen/narrow commands can jump between boxes
- **Aspect ratio**: Option for square boxes vs. rectangles matching screen or window aspect ratio

### Display Modes

- **Pure clock mode**: Original circular MouseClock with color rings (current behavior)
- **Concentric box mode**: Rectangular boxes only, no circles
- **Hybrid mode**: Both circles and boxes visible, with boxes perhaps rendered more subtly (thinner strokes, lower opacity) behind the clock rings
- **Mode switching**: Voice command to toggle between modes (e.g., "clock circles", "clock boxes", "clock hybrid")

### Target Computation

For a given (direction, box) command pair:

1. Determine the angle from the direction (A–L mapped to clock angles)
2. Identify the box boundary from the color name
3. Compute the ray from center at that angle
4. Find the intersection point where the ray crosses the specified box boundary
5. Move cursor to that intersection point

Note: For axis-aligned boxes, the intersection calculation differs from circular—the ray may hit a corner region or a flat edge depending on angle.

### Possible Voice Commands (Sketch)

- `<color> <letter>` — target intersection of that box and direction (e.g., "gold cap" for gold box + C direction)
- `<color> <number>` — same using numeric clock positions (e.g., "gold nine")
- `box <color>` — highlight or select a specific box without moving
- `clock boxes` / `clock circles` / `clock hybrid` — switch display modes

### Relationship to Existing MouseClock

- Reuses the same directional semantics (A–L letters or numeric aliases) but adds a second dimension via box selection
- Existing color names (red, blue, green, etc.) can map to box indices, maintaining voice command consistency
- Could be especially useful when combined with non-verbal triggers (hiss/shush to cycle boxes) or spiral nudges to refine position within a selected box region
- Shares canvas infrastructure, color definitions, and drawing utilities with the circular clock
