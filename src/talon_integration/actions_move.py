"""
Mouse clock movement actions - move, opposite, original, recenter_and_move.
"""

print("reloaded actions_move.py 5 - unified mode system")

from typing import List

from talon import Module, ctrl

from .instance import get_mouse_clock_instance
from .actions_core import set_mouse_clock_tags, clear_mouse_clock_tags
from .adapter import DISPLAY_MODE_INFO, DISPLAY_MODE_CLOCK_LETTERS, DISPLAY_MODE_GRID, DISPLAY_MODE_THIS

mod = Module()
from ..core.mouse_clock import flip_letter_to_opposite, parse_voice_inputs
from ..core.logger import log_info, log_warning, log_debug, log_action, log_state
from ..features.clock_letters.targeting import get_clock_letters_target
from ..features.clock_letters.config import get_clock_letters_colors
from ..features.grid.targeting import get_grid_target
from ..features.grid.config import get_grid_colors
from ..rendering.colors import get_color


def _build_this_lines(mouse_clock, start_x: float, start_y: float):
    """Build parallel lines from start position toward target direction.

    Lines are offset perpendicular to the main direction for visualization,
    but color_targets stores actual screen positions for shift functionality.
    """
    import math
    data = mouse_clock._this_line_data
    if not data:
        log_warning("[this] No line data")
        return

    all_colors = data['colors']
    main_target = data['target']
    current_color = data.get('current_color', all_colors[0] if all_colors else 'red')

    # Calculate direction vector from start to target
    dx = main_target[0] - start_x
    dy = main_target[1] - start_y
    length = math.sqrt(dx * dx + dy * dy)
    if length == 0:
        log_warning("[this] Zero length line")
        return

    log_debug(f"[this] Building lines: start=({start_x:.0f},{start_y:.0f}) target={main_target} color={current_color}")

    # Normalize direction
    dx /= length
    dy /= length

    # Perpendicular vector for offsets
    perp_x, perp_y = -dy, dx

    # Find current color's index for centering
    try:
        current_idx = all_colors.index(current_color)
    except ValueError:
        current_idx = len(all_colors) // 2

    # Build parallel lines with perpendicular offsets
    spacing = 15.0  # Pixels between parallel lines
    lines = []
    for i, color_name in enumerate(all_colors):
        offset = (i - current_idx) * spacing
        # Offset both start and end perpendicular to direction
        s_x = start_x + perp_x * offset
        s_y = start_y + perp_y * offset
        e_x = main_target[0] + perp_x * offset
        e_y = main_target[1] + perp_y * offset
        color_hex = get_color(color_name)
        lines.append(((s_x, s_y), (e_x, e_y), color_hex))

    # Add gray line to the main target (centered, on top)
    lines.append(((start_x, start_y), main_target, "888888ff"))

    mouse_clock.set_this_lines(lines)
    log_info(f"[this] {len(lines)} parallel lines from ({start_x:.0f}, {start_y:.0f})")


@mod.action_class
class MoveActions:
    def mouse_clock_move_multiple(letters_colors: List[str]):
        """Move the mouse to the intersection(s) of letters and colors.

        If the same command is repeated, recenter the clock at the current position
        and apply the command again, effectively moving in that direction.

        In clock_letters mode, uses grid-style targeting (letter+color -> position).
        """
        mouse_clock = get_mouse_clock_instance()

        # Check if in clock_letters mode - use different targeting
        if mouse_clock.get_display_mode() == DISPLAY_MODE_CLOCK_LETTERS:
            typed_expressions = parse_voice_inputs(letters_colors)
            letters = typed_expressions['letters']
            colors = typed_expressions['colors']
            directions = typed_expressions.get('directions', [])
            styles = typed_expressions.get('styles', [])
            target_dash = 'dash' in styles

            if not letters or not colors:
                log_warning("[clock_letters] Need both letter and color for targeting")
                return

            screen_rect = mouse_clock.get_screen_rect()

            # Calculate all valid (letter, color) combinations and average their positions
            points = []
            for letter in letters:
                for color in colors:
                    # Pass all directions to apply them cumulatively
                    x, y = get_clock_letters_target(screen_rect, letter, color, directions, target_dash)
                    points.append((x, y))

            if not points:
                log_warning("[clock_letters] No valid target points")
                return

            # Average all points
            avg_x = sum(p[0] for p in points) / len(points)
            avg_y = sum(p[1] for p in points) / len(points)

            ctrl.mouse_move(avg_x, avg_y)
            dir_str = f" {' '.join(directions)}" if directions else ""
            if len(points) == 1:
                log_info(f"[clock_letters] Moved to {letters[0]} {colors[0]}{dir_str} -> ({avg_x:.0f}, {avg_y:.0f})")
            else:
                log_info(f"[clock_letters] Averaged {len(points)} points ({letters} x {colors}){dir_str} -> ({avg_x:.0f}, {avg_y:.0f})")
            return

        # Standard mouse clock behavior
        typed_expressions = parse_voice_inputs(letters_colors)
        letters = typed_expressions['letters']
        colors = typed_expressions['colors']

        # Validate: Must have at least one letter (direction)
        if not letters:
            log_warning("[mouse_clock] Ignoring command - no direction specified (letters required)")
            return

        # Store as the original command (non-reversed)
        mouse_clock.core.original_command = (letters, colors)

        # Check if this exact command was just executed
        is_repeat = (mouse_clock.core.last_command == (letters, colors) and
                     mouse_clock.core.last_command != ([], []) and
                     letters and colors)

        if is_repeat:
            # Same command repeated - recenter at current position
            mouse_clock.get_mouse_position()
            # Redraw all canvases with the new center
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()

        x, y = mouse_clock.calculate_mouse_position(letters, colors, is_repeat=is_repeat)
        mouse_clock.move_mouse(x, y)

    def mouse_clock_move_opposite():
        """Move the mouse in the opposite direction of the original command."""
        mouse_clock = get_mouse_clock_instance()

        if not mouse_clock.core.original_command or mouse_clock.core.original_command == ([], []):
            log_warning("[opposite] No original command to reverse")
            return

        orig_letters, orig_colors = mouse_clock.core.original_command

        if not orig_letters:
            log_warning("[opposite] No letters in original command to reverse")
            return

        # Always flip from the ORIGINAL letters
        opposite_letters = [flip_letter_to_opposite(letter) for letter in orig_letters]

        # Check if we're repeating the reverse command
        is_repeat_reverse = (mouse_clock.core.last_command == (opposite_letters, orig_colors))

        if is_repeat_reverse:
            # Repeating reverse - recenter and move away again
            log_info(f"[opposite] Repeating reverse - recentering and moving away")
            mouse_clock.get_mouse_position()
            # Redraw all canvases with the new center
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()

        log_info(f"[opposite] Original letters: {orig_letters} -> Opposite: {opposite_letters}")
        log_info(f"[opposite] Colors: {orig_colors}")

        x, y = mouse_clock.calculate_mouse_position(opposite_letters, orig_colors, is_repeat=is_repeat_reverse)
        mouse_clock.move_mouse(x, y)

    def mouse_clock_move_original():
        """Move the mouse in the original direction (opposite of reverse)."""
        mouse_clock = get_mouse_clock_instance()

        if not mouse_clock.core.original_command or mouse_clock.core.original_command == ([], []):
            log_warning("[original] No original command to move toward")
            return

        orig_letters, orig_colors = mouse_clock.core.original_command

        if not orig_letters:
            log_warning("[original] No letters in original command")
            return

        # Check if we're repeating the original direction command
        is_repeat_original = (mouse_clock.core.last_command == (orig_letters, orig_colors))

        if is_repeat_original:
            # Repeating original - recenter and move toward again
            log_info(f"[original] Repeating original direction - recentering and moving toward")
            mouse_clock.get_mouse_position()
            # Redraw all canvases with the new center
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()

        log_info(f"[original] Moving toward original direction: {orig_letters}")
        log_info(f"[original] Colors: {orig_colors}")

        x, y = mouse_clock.calculate_mouse_position(orig_letters, orig_colors, is_repeat=is_repeat_original)
        mouse_clock.move_mouse(x, y)

    def mouse_clock_recenter_and_move(letters_colors: List[str]):
        """Recenter clock at current position, then move to specified location"""
        mouse_clock = get_mouse_clock_instance()
        mouse_clock.recenter()
        typed_expressions = parse_voice_inputs(letters_colors)
        letters = typed_expressions['letters']
        colors = typed_expressions['colors']
        x, y = mouse_clock.calculate_mouse_position(letters, colors)
        mouse_clock.move_mouse(x, y)

    def mouse_clock_move_and_activate(letters_colors: List[str]):
        """Move mouse to position (with clock off), then activate clock at new position."""
        mouse_clock = get_mouse_clock_instance()
        typed_expressions = parse_voice_inputs(letters_colors)
        letters = typed_expressions['letters']
        colors = typed_expressions['colors']

        # Validate: Must have at least one letter (direction)
        if not letters:
            log_warning("[mouse_clock] Ignoring command - no direction specified (letters required)")
            return

        # Get current mouse position FIRST before calculating
        mouse_clock.get_mouse_position()

        # Calculate position with clock off
        log_info(f"[move_and_activate] Before calc - center: ({mouse_clock.core.center_x}, {mouse_clock.core.center_y})")
        x, y = mouse_clock.calculate_mouse_position(letters, colors)
        log_info(f"[move_and_activate] Calculated new position: ({x}, {y})")

        # Move mouse to new position FIRST
        mouse_clock.move_mouse(x, y)
        log_info(f"[move_and_activate] Mouse moved to: ({x}, {y})")

        # Update the core center to the position we just moved to
        # (Don't rely on reading it back due to timing issues)
        mouse_clock.core.update_center(x, y)
        log_info(f"[move_and_activate] Updated center to: ({x}, {y})")

        # Now setup the clock at the new position (don't update position again)
        mouse_clock.setup(update_position=False)
        log_info(f"[move_and_activate] After setup - center: ({mouse_clock.core.center_x}, {mouse_clock.core.center_y})")
        mouse_clock.show()
        mouse_clock.clear_state()
        # Set tags based on current display mode
        tags = ["user.mouse_clock_showing"]
        if mouse_clock.get_display_mode() == DISPLAY_MODE_INFO:
            tags.append("user.mouse_clock_info_mode")
        set_mouse_clock_tags(tags)

        # Store as original command for potential reversal
        mouse_clock.core.original_command = (letters, colors)

    def mouse_clock_this_line(letters_colors: List[str]):
        """Draw parallel colored lines from current position to target."""
        import math
        mouse_clock = get_mouse_clock_instance()

        # Get current mouse position as start
        start_x, start_y = ctrl.mouse_pos()

        # Parse target
        typed_expressions = parse_voice_inputs(letters_colors)
        letters = typed_expressions['letters']
        colors_input = typed_expressions['colors']
        directions = typed_expressions.get('directions', [])
        styles = typed_expressions.get('styles', [])
        target_dash = 'dash' in styles

        if not letters or not colors_input:
            log_warning("[this] Need both letter and color for line target")
            return

        screen_rect = mouse_clock.get_screen_rect()

        # Calculate target based on display mode
        mode = mouse_clock.get_display_mode()
        if mode == DISPLAY_MODE_CLOCK_LETTERS:
            end_x, end_y = get_clock_letters_target(
                screen_rect, letters[0], colors_input[0], directions, target_dash
            )
            all_colors = get_clock_letters_colors()
        elif mode == DISPLAY_MODE_GRID:
            h_style = styles[0] if styles else None
            v_style = styles[1] if len(styles) > 1 else None
            end_x, end_y = get_grid_target(
                screen_rect, letters[0], colors_input[0], h_style, v_style
            )
            all_colors = get_grid_colors()
        else:
            # For circles/boxes mode, calculate from clock position
            end_x, end_y = mouse_clock.calculate_mouse_position(letters, colors_input)
            all_colors = ["red", "blue", "green", "yellow", "purple", "pink"]

        # Calculate target position for each color (same letter, different color)
        color_targets = {}
        for color_name in all_colors:
            if mode == DISPLAY_MODE_CLOCK_LETTERS:
                cx, cy = get_clock_letters_target(
                    screen_rect, letters[0], color_name, directions, target_dash
                )
            elif mode == DISPLAY_MODE_GRID:
                h_style = styles[0] if styles else None
                v_style = styles[1] if len(styles) > 1 else None
                cx, cy = get_grid_target(
                    screen_rect, letters[0], color_name, h_style, v_style
                )
            else:
                cx, cy = mouse_clock.calculate_mouse_position(letters, [color_name])
            color_targets[color_name] = (cx, cy)

        # Store geometry for color switching
        mouse_clock._this_line_data = {
            'target': (end_x, end_y),
            'colors': all_colors,
            'color_targets': color_targets,
            'current_color': colors_input[0],  # The color user specified
        }

        # Build and set lines
        _build_this_lines(mouse_clock, start_x, start_y)

        # Switch to "this" mode using unified mode system
        mouse_clock.set_mode(DISPLAY_MODE_THIS, set_mouse_clock_tags)

    def mouse_clock_this_shift(letters_colors: List[str]):
        """Shift the center/gray line to a color's target position."""
        log_action("this_shift", input=letters_colors)
        mouse_clock = get_mouse_clock_instance()

        if not mouse_clock._this_line_data:
            log_warning("[this] No active lines to shift")
            return

        # Parse to extract just colors
        typed_expressions = parse_voice_inputs(letters_colors)
        colors = typed_expressions['colors']

        if not colors:
            log_warning("[this] No colors specified")
            return

        data = mouse_clock._this_line_data
        color_targets = data['color_targets']
        log_debug(f"[this] Shifting to {colors}")

        # Find target positions for the specified colors
        targets = []
        for color in colors:
            color_lower = color.lower()
            if color_lower in color_targets:
                targets.append(color_targets[color_lower])

        if not targets:
            log_warning(f"[this shift] Color(s) not found: {colors}")
            return

        # Average the target positions
        avg_x = sum(t[0] for t in targets) / len(targets)
        avg_y = sum(t[1] for t in targets) / len(targets)

        # Update the main target to this new position
        data['target'] = (avg_x, avg_y)
        data['current_color'] = colors[0]

        # Get current start position (from gray line)
        if mouse_clock._this_lines:
            start, _, _ = mouse_clock._this_lines[-1]
            _build_this_lines(mouse_clock, start[0], start[1])
            log_info(f"[this shift] Target moved to {colors} at ({avg_x:.0f}, {avg_y:.0f})")

    def mouse_clock_clear_this_line():
        """Clear the 'this' lines and return to previous mode."""
        mouse_clock = get_mouse_clock_instance()
        previous_mode = mouse_clock.get_previous_mode()
        mouse_clock.set_mode(previous_mode, set_mouse_clock_tags)
        log_info(f"[this] Exited to {previous_mode}")
