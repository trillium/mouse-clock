"""
Mouse clock movement actions - move, opposite, original, recenter_and_move.
"""

from typing import List

from .instance import mod, ctx_tags, get_mouse_clock_instance
from .adapter import DISPLAY_MODE_INFO
from ..core.mouse_clock import flip_letter_to_opposite, parse_voice_inputs
from ..core.logger import log_info, log_warning


@mod.action_class
class MoveActions:
    def mouse_clock_move_multiple(letters_colors: List[str]):
        """Move the mouse to the intersection(s) of letters and colors.

        If the same command is repeated, recenter the clock at the current position
        and apply the command again, effectively moving in that direction.
        """
        mouse_clock = get_mouse_clock_instance()
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
        ctx_tags.tags = tags

        # Store as original command for potential reversal
        mouse_clock.core.original_command = (letters, colors)
