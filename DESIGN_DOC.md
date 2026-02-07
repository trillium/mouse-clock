### Design Specification for "Mouse Clock"

#### Overview

The "Mouse Clock" is a Python-based tool that maps the hours on a standard 12-hour clock to the first 12 letters of the English alphabet (A-L). The tool will allow users to reposition the mouse by saying the corresponding commands representing the letters A to L.

2. **Concentric Circles**:
   - The clock will have five concentric circles, each representing a different color:
     - Red
     - Blue
     - Pink
     - Green
     - Yellow
   - Each circle will be evenly spaced and centered around the clock's origin.
   - The user can specify a color to select a specific circle.
   - The intersection of a circle (color) and a letter (hour position) will determine the mouse's repositioning point.

---

### Requirements

#### Functional Requirements

1. **Clock Representation**:
   - The clock will display 12 "hour" positions, each labeled with a letter from A to L.
   - Each letter corresponds to an hour:
     - A = 1 o'clock
     - B = 2 o'clock
     - ...
     - L = 12 o'clock.

### Design Specification for "Mouse Clock"

#### Overview

The "Mouse Clock" is a Python-based tool that maps the 12-hour clock to the first 12 letters of the alphabet (A–L). Users can reposition the mouse by speaking these letters. The clock includes concentric colored circles (red, blue, pink, green, yellow). Saying a color and a letter together moves the mouse to their intersection.

---

### Requirements

#### Functional Requirements

1. **Clock Representation**

   - 12 positions labeled A–L.
   - A = 1 o'clock, B = 2 o'clock, ..., L = 12 o'clock.

2. **Concentric Circles**

   - 5 circles: Red, Blue, Pink, Green, Yellow.
   - Evenly spaced around the clock’s center.
   - User can specify a circle by color.
   - Mouse is positioned where a color circle intersects a letter position.

3. **Averaging Input**

   - Users can combine multiple letters (e.g., "A" and "B") to calculate a midpoint between those positions.
   - Similarly, users can repeat or combine colors to average between corresponding concentric circles.
   - The final mouse position is determined by averaging the angles (letters) and radii (colors) of the inputs.
   - Example: Saying "pink pink red" would place the mouse 2/3 of the way from the center toward the pink circle, averaging two pinks and one red.
   - This allows for fine-tuned control over both direction (letter) and distance (color).

4. **History and Undo**
   - The tool maintains a history of previous mouse positions.
   - Users can revert to a prior position if an incorrect or accidental command is issued.
   - This supports error recovery and smoother control.
5. **Talon Voice Integration**
   - The system is designed to operate within the Talon voice control ecosystem.
   - It will utilize Talon's custom capture system to accept multiple utterances of letters (A–L) and colors (Red, Blue, Pink, Green, Yellow).
   - A custom capture rule will be implemented to recognize and parse sequences of letters and colors.
   - This enables users to naturally speak commands like "blue A B" or "pink pink red C" to control the mouse position.

### Edge Cases and Additional Considerations

- **Equal Averaging (Opposite Letters)**:

  - When letters on opposite sides of the clock are averaged (e.g., "A" + "G"), the resulting position is the midpoint angle between them (i.e., directly horizontal), with configurable logic for tie-breaking if needed.

- **Ambiguity in Circle Spacing**:i,

  - Spacing between concentric circles is evenly divided based on the radius from the center to the outermost circle.
  - The total radius is configurable to accommodate different screen sizes.

- **Out-of-Bounds Result**:

  - If averaging results in a position beyond the outermost circle, the position is clamped to the edge of the outermost circle to prevent going off-screen.

- **"Edge" Command**:

  - A special command "edge" can be used to position the mouse at the intersection of a direction (letter) and the outermost circle.

- **Feedback Mechanism**:

  - Visual and/or auditory feedback will confirm successful recognition and execution of mouse moves.
  - This could include a brief on-screen indicator or sound.

- **Calibration**:
  - Users can recalibrate the clock’s center point and adjust circle scaling to fit different screen dimensions or setups.

---

### Implementation Notes

- **Canvas Drawing APIs**:

  - Existing APIs available within the Talon Voice system for drawing on the canvas will be utilized.
  - These APIs will be wrapped in utility functions within `mouse_clock` for easier abstraction and reuse.

- **Modular Talon Integration**:

  - Talon-specific integration will be kept in separate files to maintain modularity.
  - The `mouse_clock` core logic will be decoupled from Talon, allowing for better testability and reuse.
  - Talon scripts will import functionality from the `mouse_clock` module.

- **Wrapper Functions**:

  - All interactions with the Talon canvas and voice APIs will go through wrapper functions in `mouse_clock`.
  - This approach allows for potential substitution or extension with non-Talon environments in the future.

- **Settings File**:
  - A dedicated `settings` module will define:
    - Default and user-customized colors.
    - Circle radii and spacing.
    - Clock center calibration data.
    - Additional configuration for averaging behavior, clamping, and feedback mechanisms.

---

### Talon Canvas Integration

- **Canvas Object Creation**:

  - The canvas is created using `canvas.Canvas.from_screen(screen)` within the `setup` method.
  - This initializes a canvas tied to the current screen, ready for drawing the clock UI.

- **Draw Callback Registration**:

  - The `draw` method is registered as a callback handler for the canvas.
  - Talon automatically invokes this method and supplies the canvas object when a draw event occurs.

- **Canvas Usage**:
  - All visual elements of the "Mouse Clock" (circles, labels, indicators) are rendered using Talon’s canvas drawing APIs.
  - The `draw` method uses the passed-in canvas object to render current state based on user input (e.g., letter and color selection).

---

### Current Implementation Details

Based on the codebase analysis, the following updates and clarifications apply to the design:

- **Concentric Circles**:

  - The implementation uses **7 concentric circles** instead of 5, with the following colors (from innermost to outermost):
    - Center (black `#000000ff`, zero radius)
    - Red (`#ff0000ff`)
    - Blue (`#0000ffff`)
    - Green (`#00ff00ff`)
    - Yellow (`#FFD700ff`)
    - Purple (`#800080ff`)
    - Pink (`#ff00ffff`)
  - Colors are mapped via `color.talon-list`, with aliases (e.g., "gold" → yellow, "plum" → purple).

- **Averaging Input**:

  - Implemented using Cartesian averaging for angles and simple averaging for radii.
  - Letters are converted to clock angles (A=12 o'clock), averaged, then back to Cartesian coordinates.
  - Colors are indexed (0-6) and scaled by radius for averaging; 'center' always has radius 0.
  - History tracks previous commands for incremental averaging (e.g., saying "red" then "A" appends to previous inputs).

- **History and Undo**:

  - Fully implemented: maintains a list of mouse positions; `go_back()` reverts to the last position.

- **Talon Voice Integration**:

  - Captures use `({user.mouse} | {user.color} | {user.letter_directional})+` for parsing sequences.
  - Separate talon files for always-active, active-when-showing, and settings.
  - Actions include `mouse_clock_move_multiple()` for processing parsed inputs.

- **Canvas Drawing**:

  - Circles are drawn with `paint.color` set to each `COLOR_LIST` entry.
  - Letters A-L are positioned at 30° intervals starting from -90° (12 o'clock).
  - Canvas is screen-wide, with mouse position as center.

- **Additional Features**:

  - Radius adjustment: `widen`/`narrow` commands change circle sizes dynamically.
  - Screen selection: `clock screen [<number>]` activates on specific screens.
  - Keybinds: e.g., `cmd-ctrl-alt-shift-a` for automated sequences.
  - Touch/click integration: Commands like "touch" close the clock and click.

- **Discrepancies from Design**:

  - 7 colors instead of 5 (added center, purple/pink).
  - No "edge" command implemented yet.
  - No feedback mechanism or calibration features in current code.
  - Averaging clamps to outermost ring if needed, but not explicitly handled in code.
  - Boxes and info display modes were removed during cleanup (Feb 2026). Three modes remain: circles, grid, clock_letters.

- **Modular Structure**:
  - Core logic in `src/core/` (mouse_clock.py, config.py, animation.py).
  - Geometry in `src/core/geometry/` (angles, averaging, coordinates, intersections).
  - Features in `src/features/` (grid, clock_letters).
  - Rendering in `src/rendering/` (canvas, animation, drawing primitives).
  - Talon integration in `src/talon_integration/` (adapter, actions, talon files).
