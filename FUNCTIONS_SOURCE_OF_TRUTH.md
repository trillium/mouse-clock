# Mouse Clock - Functions Source of Truth

This document lists all functions in the codebase organized by file.

---

## src/core/config.py

### get_setting
**Retrieve a setting value.**

### set_setting
**Update a setting at runtime.**

### reset_setting
**Restore a setting to its default value.**

### reset_all_settings
**Restore all settings to defaults.**

### get_all_settings
**Get copy of all current settings.**

### load_settings
**Load settings from JSON file.**

### save_settings
**Persist current settings to JSON file.**

### load_default_settings
**Load settings from the default file on startup.**

### get_active_colors
**Get the list of currently active color names.**

### get_active_styles
**Get the list of currently active line style names.**

### get_active_letters
**Get the list of currently active letters.**

### get_mode_config
**Get the active items for a mode+dimension, falling back to global.**

### set_mode_config
**Set the full list of active items for a mode+dimension.**

### add_mode_item
**Add an item to a mode's dimension list (copy-on-write from global).**

### remove_mode_item
**Remove an item from a mode's dimension list (copy-on-write from global).**

### reset_mode_config
**Delete the per-mode override, restoring fallback to global.**

---

## src/core/mouse_clock.py

### MouseClockCore.__init__
**Initialize the mouse clock core.**

### MouseClockCore.update_center
**Update the center position of the clock.**

### MouseClockCore.calculate_edge_distance
**Calculate distance from center to screen edge in given direction.**

### MouseClockCore.calculate_mouse_position
**Calculate the averaged (x, y) position for the mouse based on letters and colors.**

### MouseClockCore._process_colors
**Process color list into distance values.**

### MouseClockCore._calculate_half_distance
**Calculate 'half' distance - halfway between last color and screen edge.**

### MouseClockCore.add_to_history
**Add a position to the movement history.**

### MouseClockCore.pop_from_history
**Remove and return the last position from history.**

### MouseClockCore.widen_radius
**Increase the target radius of the clock (animates smoothly).**

### MouseClockCore.narrow_radius
**Decrease the target radius of the clock (animates smoothly).**

### MouseClockCore.set_radius
**Set the radius to a specific value (with minimum limit).**

### MouseClockCore.update_radius_animation
**Interpolate radius toward target with exponential acceleration.**

### MouseClockCore._get_dynamic_increment
**Get dynamic increment (for backwards compatibility with debug logging).**

### MouseClockCore.clear_state
**Clear the command state.**

---

## src/core/voice_parsing.py

### flip_letter_to_opposite
**Flip a clock letter to its opposite position (180 degrees).**

### parse_voice_inputs
**Parse voice input words into letters, colors, and apply ordinal multipliers.**

---

## src/core/animation.py

### exponential_lerp_factor
**Calculate an accelerating lerp factor based on elapsed time.**

### RadiusAnimator.__init__
**Initialize radius animator.**

### RadiusAnimator.update_timing
**Update animation timing on each input event.**

### RadiusAnimator.get_elapsed
**Get elapsed time since animation started.**

### RadiusAnimator.get_dynamic_increment
**Get radius increment that accelerates over time.**

### RadiusAnimator.get_lerp_factor
**Get lerp factor for interpolating radius toward target.**

### RadiusAnimator.clamp_radius
**Clamp radius within allowed bounds.**

### RadiusAnimator.reset
**Reset animation state.**

---

## src/core/logger.py

### _create_new_log_file
**Create a new timestamped log file and return its path.**

### initialize_logger
**Initialize or reinitialize the logger with a new timestamped file.**

### get_current_log_file
**Get the path to the current log file.**

### log_separator
**Log a separator line for readability.**

### log_debug
**Log a debug message.**

### log_info
**Log an info message.**

### log_warning
**Log a warning message.**

### log_error
**Log an error message.**

### log_position
**Log a position with context label.**

### log_action
**Log an action invocation with parameters.**

---

## src/core/geometry/angles.py

### to_radians
**Convert angle in degrees to radians.**

### to_cartesian
**Convert an angle in degrees to Cartesian coordinates (x, y).**

### to_angle
**Convert Cartesian coordinates (x, y) back to an angle in degrees.**

### normalize_angle
**Normalize an angle to the 0-360 range.**

### opposite_angle
**Return the opposite direction (angle + 180, normalized).**

---

## src/core/geometry/clock.py

### number_to_angle
**Convert a clock hour (1-12) to degrees.**

### letter_to_angle
**Convert a clock letter (A-L) to degrees.**

### angle_to_letter
**Return the nearest clock letter for any angle.**

### letter_to_position
**Return the position of a letter in the alphabet (1-indexed).**

### letter_to_clock_angle
**Given a letter position (1-12 for A-L), return the corresponding clock angle in degrees.**

---

## src/core/geometry/averaging.py

### average_coordinates
**Average a list of Cartesian coordinates (x, y).**

### average_angles
**Average a list of angles in degrees (360-degree system).**

### calculate_mean
**Return the arithmetic mean of a list of values.**

### average_clock_angles
**Average clock hour positions (1-12) and return both hour and degree values.**

---

## src/core/geometry/coordinates.py

### move_in_direction
**Calculate a point at a given distance in a clock-style direction.**

### distance_between
**Calculate the Euclidean distance between two points.**

### point_on_circle
**Calculate a point on a circle's perimeter at a given angle.**

### clamp_to_bounds
**Constrain a point to stay within a rectangle.**

---

## src/core/geometry/intersections.py

### ray_line_intersection
**Find where a ray intersects a line segment.**

### ray_circle_intersection
**Find where a ray from origin intersects a circle.**

### ray_rect_intersection
**Find where a ray intersects an axis-aligned rectangle.**

---

## src/input/mouse.py

### get_mouse_position
**Get current cursor position.**

### set_mouse_position
**Move cursor to absolute position.**

### move_mouse_relative
**Move cursor by offset from current position.**

### get_screen_for_mouse
**Get the screen containing the current cursor position.**

### get_screen_rect
**Get bounds of a screen.**

### get_screen_bounds
**Get screen bounds as (left, top, right, bottom).**

---

## src/input/debounce.py

### debounce
**Decorator to enforce minimum interval between calls.**

### throttle
**Decorator to limit call frequency to max rate per second.**

### set_cooldown
**Set a cooldown for an event type.**

### is_cooling_down
**Check if an event type is in cooldown period.**

### reset_cooldown
**Clear cooldown for an event type.**

### reset_all_cooldowns
**Clear all cooldowns.**

### RateLimiter.__init__
**Initialize rate limiter.**

### RateLimiter.try_acquire
**Try to acquire permission to proceed.**

### RateLimiter.time_until_ready
**Get time in seconds until next call is allowed.**

### RateLimiter.reset
**Reset the limiter, allowing immediate next call.**

---

## src/input/history.py

### PositionHistory.__init__
**Initialize position history.**

### PositionHistory.push_position
**Add position to history stack.**

### PositionHistory.pop_position
**Remove and return last position.**

### PositionHistory.peek_position
**View last position without removing.**

### PositionHistory.clear_history
**Clear all stored positions and reset origin.**

### PositionHistory.get_origin
**Get starting position for current session.**

### PositionHistory.set_origin
**Explicitly set the session origin.**

### PositionHistory.__len__
**Return number of positions in history.**

### PositionHistory.is_empty
**Check if history is empty.**

### push_position
**Add position to global history stack.**

### pop_position
**Remove and return last position from global history.**

### peek_position
**View last position without removing from global history.**

### clear_history
**Clear global position history.**

### get_origin
**Get session origin from global history.**

### set_origin
**Set session origin in global history.**

### get_history_instance
**Get the global PositionHistory instance.**

---

## src/input/guards.py

### OverlayStateManager.__init__
**Initialize overlay state manager.**

### OverlayStateManager.set_active
**Mark an overlay as active.**

### OverlayStateManager.set_inactive
**Mark an overlay as inactive.**

### OverlayStateManager.is_overlay_active
**Check if a specific overlay is showing.**

### OverlayStateManager.any_overlay_active
**Check if any mouse overlay is active.**

### OverlayStateManager.get_active_overlay
**Get name of currently active overlay.**

### OverlayStateManager.get_all_active
**Get set of all active overlay names.**

### OverlayStateManager.clear_all
**Mark all overlays as inactive.**

### set_overlay_active
**Mark overlay as active in global state.**

### set_overlay_inactive
**Mark overlay as inactive in global state.**

### is_overlay_active
**Check if specific overlay is active.**

### any_overlay_active
**Check if any overlay is active.**

### get_active_overlay
**Get name of current active overlay.**

### require_overlay
**Decorator that only runs function if overlay is active.**

### require_no_overlay
**Decorator that only runs function if NO overlay is active.**

### get_state_manager
**Get the global OverlayStateManager instance.**

---

## src/input/sound_actions.py

### SoundActionRegistry.__init__
**Initialize sound action registry.**

### SoundActionRegistry.register_sound_action
**Map a parrot sound to an action with parameters.**

### SoundActionRegistry.unregister_sound_action
**Remove a sound mapping.**

### SoundActionRegistry.get_action_for_sound
**Look up actions for a sound.**

### SoundActionRegistry.set_sound_param
**Adjust parameters for an existing mapping.**

### SoundActionRegistry.get_sound_param
**Get a parameter value for a sound mapping.**

### SoundActionRegistry.execute_sound
**Execute all actions registered for a sound.**

### SoundActionRegistry.list_sounds
**Get list of all registered sound labels.**

### SoundActionRegistry.clear
**Remove all sound mappings.**

### register_sound_action
**Register action in global registry.**

### unregister_sound_action
**Unregister action from global registry.**

### get_action_for_sound
**Get actions from global registry.**

### set_sound_param
**Set param in global registry.**

### execute_sound
**Execute sound actions from global registry.**

### get_registry
**Get the global SoundActionRegistry instance.**

---

## src/util/screen.py

### get_all_screens
**List all available screens.**

### get_primary_screen
**Get the primary/main screen.**

### get_active_window_rect
**Get bounds of the currently focused window.**

### point_to_screen
**Find which screen contains a point.**

### clamp_to_screen
**Keep point within screen bounds.**

### screen_center
**Get center point of a screen.**

### get_screen_rect
**Get screen bounds as (x, y, width, height).**

### get_screen_bounds
**Get screen bounds as (left, top, right, bottom).**

---

## src/rendering/colors.py

### get_color
**Look up hex color by name.**

### with_alpha
**Modify the alpha channel of a color.**

### parse_hex_color
**Parse an 8-digit RGBA hex string to (r, g, b, a) floats in 0-1 range.**

### relative_luminance
**Calculate WCAG relative luminance from sRGB values (0-1).**

---

## src/rendering/animation.py

### FadeAnimator.__init__
**Initialize fade animator with update and complete callbacks.**

### FadeAnimator.fade_in
**Fade in from current alpha to fully opaque.**

### FadeAnimator.fade_out
**Fade out from current alpha to fully transparent.**

### FadeAnimator.pulse
**Start continuous pulsing between min and max alpha.**

### FadeAnimator.stop_pulse
**Stop pulsing and fade to full opacity.**

### FadeAnimator.set_alpha
**Set alpha immediately without animation.**

### FadeAnimator._animate
**Start animation to target alpha.**

### FadeAnimator._tick
**Animation frame update.**

### FadeAnimator._cancel
**Cancel any running animation.**

### FadeAnimator.is_animating
**Check if an animation is currently running.**

### FadeAnimator.is_visible
**Check if alpha is above zero.**

---

## src/rendering/drawing/primitives.py

### draw_circle
**Draw a circle outline or filled.**

### draw_rect
**Draw a rectangle outline or filled.**

### draw_dot
**Draw a small filled circle marker.**

### draw_cross
**Draw a cross marker (+ or x).**

### draw_text
**Render text with configurable anchor point.**

---

## src/rendering/drawing/lines.py

### _get_line_geometry
**Calculate line geometry: direction, length, and perpendicular.**

### _draw_simple_pattern
**Draw a line with a simple dash/gap pattern.**

### _draw_morse
**Draw morse pattern: dash dash dot.**

### draw_line
**Draw a line segment with the specified style.**

### draw_dotted_line
**Draw a dotted line (small dots with gaps).**

### draw_dashed_line
**Draw a dashed line (longer dashes with gaps).**

---

## src/rendering/drawing/line_styles.py

### _draw_twin
**Draw two parallel lines.**

### _draw_chain
**Draw linked circles.**

### _draw_wave
**Draw a sine wave line.**

### _draw_zig
**Draw a zigzag line.**

### _draw_barb
**Draw line with angled ticks/barbs.**

### _draw_rail
**Draw railroad/ladder style.**

### _draw_cross
**Draw X marks along the line.**

### _draw_link
**Draw interlocking loops (disabled, draws dashed line instead).**

### _draw_bead
**Draw beads connected by thin lines.**

### _draw_spike
**Draw flat line with periodic spikes (heartbeat).**

### _draw_hash
**Draw # marks along the line.**

### _draw_saw
**Draw asymmetric sawtooth pattern.**

---

## src/rendering/drawing/composite.py

### draw_ray
**Draw a ray from origin at specified angle.**

### draw_concentric_circles
**Draw multiple circles with different colors.**

### draw_concentric_rects
**Draw multiple rectangles with different colors, centered.**

### draw_clock_rays
**Draw all 12 clock-hour directional rays.**

---

## src/rendering/canvas/clock.py

### draw_clock_letters
**Draw the clock position letters (A-L) around the outer ring.**

### draw_mouse_clock
**Draw the mouse clock visualization with concentric circles and clock position letters.**

---

## src/features/spiral_nudge.py

### calculate_spiral_point
**Calculate position on Archimedean spiral.**

### start_spiral
**Start a new spiral navigation from origin.**

### nudge_forward
**Move to next point on spiral.**

### nudge_backward
**Move to previous point on spiral.**

### reset_spiral
**Reset to spiral origin.**

### stop_spiral
**Stop spiral navigation.**

### get_spiral_state
**Get current spiral state.**

### is_spiral_active
**Check if spiral navigation is active.**

### get_current_position
**Get current position on spiral.**

### get_origin
**Get spiral origin.**

---

## src/features/grid/state.py

### get_column_offset
**Get current horizontal offset for columns.**

### get_target_offset
**Get target horizontal offset for columns.**

### set_column_offset
**Set horizontal offset for columns (immediate, no animation).**

### shift_columns_left
**Shift columns left by amount pixels (sets target for animation).**

### shift_columns_right
**Shift columns right by amount pixels (sets target for animation).**

### reset_column_offset
**Reset column offset to center.**

### reset_grid_state
**Reset all grid state including toggles.**

### end_hiss_session
**Call when hiss stops (gap detected) to toggle direction for next session.**

### end_shush_session
**Call when shush stops (gap detected) to toggle mode for next session.**

### grid_hiss
**Handle hiss in grid mode - shifts columns in current direction.**

### grid_shush
**Handle shush in grid mode - widens or narrows spacing.**

### get_hiss_direction
**Get current hiss direction as string.**

### get_shush_mode
**Get current shush mode as string.**

### update_offset_animation
**Interpolate offset toward target.**

---

## src/features/grid/config.py

### get_text_color
**Get the text color for grid labels.**

### get_text_bg_color
**Get the background color for grid labels.**

### get_grid_colors
**Get the list of active colors for grid columns.**

### get_grid_styles
**Get the list of active line styles for the grid (legacy, uses horizontal).**

### get_horizontal_styles
**Get the list of active styles for horizontal (letter) lines.**

### get_vertical_styles
**Get the list of active styles for vertical (color) lines.**

### get_grid_letters
**Get the list of active letters for grid rows.**

### get_column_spacing
**Get spacing between color columns in pixels.**

---

## src/features/grid/layout.py

### get_visible_letters
**Get letters that fit on screen given spacing.**

### calculate_row_positions
**Calculate Y positions for each letter row.**

### calculate_column_positions
**Calculate X positions for each color column, distributed evenly across screen.**

---

## src/features/grid/render.py

### _apply_alpha
**Apply current fade alpha to a color.**

### draw_grid_overlay
**Draw the letter/color grid overlay.**

### _draw_row_lines
**Draw horizontal lines with labels.**

### _draw_column_lines
**Draw vertical lines with labels.**

### _draw_intersections
**Draw markers at grid intersections.**

---

## src/features/grid/targeting.py

### get_grid_target
**Get the (x, y) position for a letter+color+style target.**

---

## src/features/clock_letters/config.py

### get_text_color
**Get the text color for clock letters labels.**

### get_text_bg_color
**Get the background color for clock letters labels.**

### get_clock_letters_colors
**Get the list of active colors for clock letters columns.**

### get_clock_letters_letters
**Get the list of active letters for clock letters rows.**

---

## src/features/clock_letters/layout.py

### calculate_row_positions
**Calculate Y positions for each letter row.**

### calculate_column_positions
**Calculate X positions for each color column, distributed evenly across screen.**

---

## src/features/clock_letters/render.py

### _apply_alpha
**Apply current fade alpha to a color.**

### draw_clock_letters_overlay
**Draw the clock letters overlay.**

---

## src/features/clock_letters/targeting.py

### get_clock_letters_target
**Get the (x, y) position for a letter+color target.**

---

## src/talon_integration/instance.py

### get_mouse_clock_instance
**Get the global mouse clock instance, recreating on module reload.**

### get_context
**Get the mouse clock context.**

### get_module
**Get the mouse clock module.**

---

## src/talon_integration/adapter.py

### MouseClockTalonAdapter.__init__
**Initialize mouse clock adapter.**

### MouseClockTalonAdapter.get_display_mode
**Get current display mode.**

### MouseClockTalonAdapter.set_display_mode
**Set display mode and save to settings.**

### MouseClockTalonAdapter.refresh_canvases
**Trigger a redraw on all canvases.**

### MouseClockTalonAdapter.get_mouse_position
**Get current mouse position from Talon and update core.**

### MouseClockTalonAdapter.get_screen_rect
**Get the screen rectangle bounds for the current screen.**

### MouseClockTalonAdapter.calculate_mouse_position
**Calculate mouse position using core logic with Talon screen info.**

### MouseClockTalonAdapter.setup
**Set up canvases for all screens.**

### MouseClockTalonAdapter._on_fade_update
**Called when fade animation updates alpha.**

### MouseClockTalonAdapter._on_fade_out_complete
**Called when fade out animation completes.**

### MouseClockTalonAdapter.show
**Show the mouse clock on all canvases with fade in.**

### MouseClockTalonAdapter.close
**Close the mouse clock with fade out animation.**

### MouseClockTalonAdapter.draw
**Draw callback for Talon canvas.**

### MouseClockTalonAdapter.move_mouse
**Move the mouse to the specified position and add to history.**

### MouseClockTalonAdapter.go_back
**Revert to the previous mouse position.**

### MouseClockTalonAdapter.widen_radius
**Increase the radius of the circle.**

### MouseClockTalonAdapter.narrow_radius
**Decrease the radius of the circle.**

### MouseClockTalonAdapter.set_radius
**Set the radius to a specific value and refresh the canvas if active.**

### MouseClockTalonAdapter.clear_state
**Clear the command state.**

### MouseClockTalonAdapter.recenter
**Recenter the clock at the current mouse position and redraw.**

---

## src/talon_integration/actions.py (Captures)

### clock_face
**Capture a single clock face letter.**

### color
**Capture a color.**

### mouse
**Capture the word mouse.**

### line_style
**Capture a line style (solid, dashed, dotted).**

### styled_target
**Capture an optional line style followed by a letter or color.**

### letters_colors
**Capture any number of styled targets.**

---

## src/talon_integration/actions_core.py

### mouse_clock_activate
**Show mouse clock.**

### mouse_clock_show
**Alias for mouse_clock_activate.**

### mouse_clock_close
**Close the mouse clock.**

### mouse_clock_toggle
**Toggle mouse clock on/off.**

### mouse_clock_go_back
**Revert to the previous mouse position.**

### mouse_clock_widen
**Increases the radius of the circle.**

### mouse_clock_narrow
**Decreases the radius of the circle.**

### mouse_clock_set_radius
**Sets the radius of mouse clock.**

### mouse_clock_recenter
**Recenter the clock at the current mouse position.**

### mouse_clock_scoot
**Shift the whole clock a direction.**

---

## src/talon_integration/actions_move.py

### mouse_clock_move_multiple
**Move the mouse to the intersection(s) of letters and colors. In clock_letters mode, uses grid-style targeting.**

### mouse_clock_move_opposite
**Move the mouse in the opposite direction of the original command.**

### mouse_clock_move_original
**Move the mouse in the original direction (opposite of reverse).**

### mouse_clock_recenter_and_move
**Recenter clock at current position, then move to specified location.**

### mouse_clock_move_and_activate
**Move mouse to position (with clock off), then activate clock at new position.**

---

## src/talon_integration/actions_display.py

### _set_mode_and_refresh
**Set display mode and activate clock if not showing.**

### mouse_clock_mode_circles
**Switch to circles display mode.**

### mouse_clock_mode_grid
**Switch to grid display mode (letters + colors).**

### mouse_clock_mode_clock_letters
**Switch to clock letters display mode (letters in colors).**

### mouse_clock_get_mode
**Get current display mode.**

### mouse_clock_cycle_mode
**Cycle to next display mode.**

### mouse_clock_cycle_mode_previous
**Cycle to previous display mode.**

---

## src/talon_integration/actions_grid.py

### _get_target
**Get target position based on current display mode.**

### grid_move_to
**Move mouse to grid intersection (letter + color + style).**

### grid_move_to_full
**Move mouse to grid intersection with separate horizontal/vertical styles.**

### grid_move_simple
**Move mouse to grid intersection (letter + color, default styles).**

---

## src/talon_integration/parrot_actions.py

### _log_parrot_event
**Log parrot event with debug info matching visual display.**

### noise_hiss (override)
**Hiss widens the clock radius.**

### noise_shh (override)
**Shush narrows the clock radius.**

### noise_lip_pop (override)
**Pop clicks and closes the clock.**

### noise_tongue_click (override)
**Cluck toggles visibility.**

### mouse_clock_parrot_hiss
**Handle hiss sound for mouse clock (manual trigger for testing).**

### mouse_clock_parrot_shush
**Handle shush sound for mouse clock (manual trigger for testing).**

### mouse_clock_parrot_reset_config
**Reset parrot sound configuration to defaults.**

### mouse_clock_parrot_reload
**Reload parrot sound configuration.**

### mouse_clock_parrot_set_param
**Set a parrot sound parameter (e.g., 'hiss amount 30').**

### mouse_clock_keyboard_hiss_start
**Start continuous hiss triggered by keyboard.**

### mouse_clock_keyboard_hiss_stop
**Stop keyboard-triggered hiss.**

### mouse_clock_keyboard_shush_start
**Start continuous shush triggered by keyboard.**

### mouse_clock_keyboard_shush_stop
**Stop keyboard-triggered shush.**

### register_overlay_active
**Call when mouse clock becomes active.**

### register_overlay_inactive
**Call when mouse clock is closed.**

---

## src/talon_integration/parrot_handlers.py

### _update_animation_timing
**Update animation timing on every sound event (before rate limiting).**

### _get_limiter
**Get or create rate limiter for a sound.**

### clear_rate_limiters
**Clear all rate limiters (call after config reload).**

### on_parrot
**Parrot event handler.**

### execute_action
**Execute action based on active overlay.**

### _execute_toggle_action
**Toggle the primary overlay visibility.**

### _execute_mouse_clock_action
**Execute mouse clock specific action.**

### _execute_spiral_action
**Execute spiral nudge specific action.**

### _execute_box_overlay_action
**Execute box overlay specific action.**

