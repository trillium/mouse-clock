"""
Mouse clock movement actions - move, reverse_last_direction, repeat_last_direction, recenter_and_move.
"""

from typing import List

from talon import Module, actions, ctrl
from .actions_core import set_mouse_clock_tags
from .instance import get_mouse_clock_instance
from ..core.voice_parsing import flip_letter_to_opposite, parse_voice_inputs
from ..core.logger import log_info, log_warning
from ..features.clock_letters.targeting import get_clock_letters_target
from ..features.dense_grid.targeting import get_dense_grid_target
from ..core.constants import DISPLAY_MODE_CLOCK_LETTERS, DISPLAY_MODE_DENSE_GRID
from ..core.pipeline import get_next_stage, get_start_mode

mod = Module()


def _check_repeat_and_recenter(mouse_clock, letters, colors, label="mouse_clock",
                               require_both=False):
    """Check if (letters, colors) matches last command; if so, recenter. Returns True if repeat."""
    if require_both and not (letters and colors):
        return False
    command = (letters, colors)
    if mouse_clock.core.last_command == command:
        log_info(f"[{label}] Repeat detected - recentering")
        mouse_clock.get_mouse_position()
        mouse_clock.refresh_canvases()
        return True
    return False


def _resolve_partial_input(core, letters, colors, display_mode, refresh_fn):
    """Resolve partial letter/color input. Returns (letters, colors) or None for early return."""
    def _complete(l, c):
        core.pending_letter = core.pending_color = None
        core.last_move_was_partial = False
        return l, c

    def _store_pending(which, value):
        core.pending_letter = value if which == 'letter' else None
        core.pending_color = value if which == 'color' else None
        core.last_move_was_partial = True
        log_info(f"[{display_mode}] Stored pending {which}: {value}")
        refresh_fn()
        return None

    if letters and colors:
        return _complete(letters, colors)
    if letters:
        if core.pending_color is not None:
            return _complete(letters, core.pending_color)
        return _store_pending('letter', letters)
    if colors:
        if core.pending_letter is not None:
            return _complete(core.pending_letter, colors)
        return _store_pending('color', colors)
    log_warning("[clock_letters] Need at least a letter or color for targeting")
    return None


@mod.action_class
class MoveActions:
    def mouse_clock_move_multiple(letters_colors: List[str]):
        """Move mouse to intersection(s) of letters and colors. Supports partial input."""
        mouse_clock = get_mouse_clock_instance()

        # Check if in grid-based mode - use letter+color targeting
        display_mode = mouse_clock.get_display_mode()
        if display_mode in (DISPLAY_MODE_CLOCK_LETTERS, DISPLAY_MODE_DENSE_GRID):
            typed_expressions = parse_voice_inputs(letters_colors)
            letters = typed_expressions['letters']
            colors = typed_expressions['colors']
            directions = typed_expressions.get('directions', [])
            styles = typed_expressions.get('styles', [])
            target_dash = 'dash' in styles

            # Resolve partial input (letter-only or color-only commands)
            result = _resolve_partial_input(
                mouse_clock.core, letters, colors, display_mode,
                mouse_clock.refresh_canvases)
            if result is None:
                return
            letters, colors = result

            # Repeat detection: same command re-centers, then re-applies
            command = (letters, colors)
            if mouse_clock.core.last_command == command:
                log_info(f"[{display_mode}] Repeat detected - recentering")
                mouse_clock.get_mouse_position()
                mouse_clock.refresh_canvases()

            # Calculate all valid (letter, color) combinations and average their positions
            points = []
            for letter in letters:
                for color in colors:
                    if display_mode == DISPLAY_MODE_DENSE_GRID:
                        center = ctrl.mouse_pos()
                        x, y = get_dense_grid_target(center, letter, color, directions)
                    else:
                        screen_rect = mouse_clock.get_screen_rect()
                        x, y = get_clock_letters_target(screen_rect, letter, color, directions, target_dash)
                    points.append((x, y))

            if not points:
                log_warning("[clock_letters] No valid target points")
                return

            # Average all points
            avg_x = sum(p[0] for p in points) / len(points)
            avg_y = sum(p[1] for p in points) / len(points)

            # Capture delta for dense grid opposite
            if display_mode == DISPLAY_MODE_DENSE_GRID:
                cur_x, cur_y = ctrl.mouse_pos()
                mouse_clock.core.last_dense_grid_delta = (avg_x - cur_x, avg_y - cur_y)

            mouse_clock.core.original_command = (letters, colors)
            mouse_clock.core.last_command = (letters, colors)
            mouse_clock.move_mouse(avg_x, avg_y)
            dir_str = f" {' '.join(directions)}" if directions else ""
            log_info(f"[{display_mode}] {len(points)} pt(s) ({letters} x {colors}){dir_str} -> ({avg_x:.0f}, {avg_y:.0f})")
            return

        # Standard mouse clock behavior
        typed_expressions = parse_voice_inputs(letters_colors)
        letters = typed_expressions['letters']
        colors = typed_expressions['colors']

        if not letters:
            log_warning("[mouse_clock] No direction specified (letters required)")
            return

        mouse_clock.core.original_command = (letters, colors)
        is_repeat = _check_repeat_and_recenter(mouse_clock, letters, colors,
                                               require_both=True)

        x, y = mouse_clock.calculate_mouse_position(letters, colors, is_repeat=is_repeat)
        mouse_clock.move_mouse(x, y)

    def mouse_clock_move_reverse_last_direction():
        """Move the mouse in the opposite direction of the original command."""
        mouse_clock = get_mouse_clock_instance()

        if mouse_clock.get_display_mode() == DISPLAY_MODE_DENSE_GRID:
            dx, dy = mouse_clock.core.last_dense_grid_delta
            if dx == 0.0 and dy == 0.0:
                log_warning("[reverse_last_direction] No dense grid delta to reverse")
                return
            cur_x, cur_y = ctrl.mouse_pos()
            new_x, new_y = cur_x - dx, cur_y - dy
            mouse_clock.move_mouse(new_x, new_y)
            log_info(f"[reverse_last_direction] Dense grid reverse delta ({-dx:.0f}, {-dy:.0f}) -> ({new_x:.0f}, {new_y:.0f})")
            return

        orig = mouse_clock.core.original_command
        if not orig or orig == ([], []) or not orig[0]:
            log_warning("[reverse_last_direction] No original command to reverse")
            return
        orig_letters, orig_colors = orig
        opposite_letters = [flip_letter_to_opposite(letter) for letter in orig_letters]
        is_repeat_reverse = _check_repeat_and_recenter(
            mouse_clock, opposite_letters, orig_colors, label="reverse_last_direction")
        log_info(f"[reverse_last_direction] {orig_letters} -> {opposite_letters}, colors: {orig_colors}")
        x, y = mouse_clock.calculate_mouse_position(opposite_letters, orig_colors, is_repeat=is_repeat_reverse)
        mouse_clock.move_mouse(x, y)

    def mouse_clock_move_repeat_last_direction():
        """Move the mouse in the original direction (repeat of last move)."""
        mouse_clock = get_mouse_clock_instance()

        if mouse_clock.get_display_mode() == DISPLAY_MODE_DENSE_GRID:
            dx, dy = mouse_clock.core.last_dense_grid_delta
            if dx == 0.0 and dy == 0.0:
                log_warning("[repeat_last_direction] No dense grid delta to repeat")
                return
            cur_x, cur_y = ctrl.mouse_pos()
            new_x, new_y = cur_x + dx, cur_y + dy
            mouse_clock.move_mouse(new_x, new_y)
            log_info(f"[repeat_last_direction] Dense grid repeat delta ({dx:.0f}, {dy:.0f}) -> ({new_x:.0f}, {new_y:.0f})")
            return

        orig = mouse_clock.core.original_command
        if not orig or orig == ([], []) or not orig[0]:
            log_warning("[repeat_last_direction] No original command to move toward")
            return
        orig_letters, orig_colors = orig
        is_repeat_original = _check_repeat_and_recenter(
            mouse_clock, orig_letters, orig_colors, label="repeat_last_direction")
        log_info(f"[repeat_last_direction] {orig_letters}, colors: {orig_colors}")
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

        if not letters:
            log_warning("[move_and_activate] No direction specified")
            return

        mouse_clock.get_mouse_position()
        x, y = mouse_clock.calculate_mouse_position(letters, colors)
        mouse_clock.move_mouse(x, y)
        mouse_clock.core.update_center(x, y)
        mouse_clock.setup(update_position=False)
        mouse_clock.show()
        mouse_clock.clear_state()
        set_mouse_clock_tags(["user.mouse_clock_showing"])
        mouse_clock.core.original_command = (letters, colors)

    def mouse_clock_activate_with_pending(letters_colors: List[str]):
        """Activate clock, optionally with partial targeting. Supports letter-only or color-only."""
        mouse_clock = get_mouse_clock_instance()

        typed_expressions = parse_voice_inputs(letters_colors)
        letters = typed_expressions['letters']
        colors = typed_expressions['colors']

        if letters and colors:
            # Full targeting: delegate to existing move_and_activate
            actions.user.mouse_clock_move_and_activate(letters_colors)
            return

        # Activate clock at current mouse position
        mouse_clock.setup()
        mouse_clock.show()
        mouse_clock.clear_state()
        start_mode = get_start_mode()
        mouse_clock.set_mode(start_mode, set_mouse_clock_tags)

        # Store partial input as pending
        if letters:
            mouse_clock.core.pending_letter = letters
            mouse_clock.core.last_move_was_partial = True
            log_info(f"[activate_with_pending] Stored pending letter: {letters}")
        elif colors:
            mouse_clock.core.pending_color = colors
            mouse_clock.core.last_move_was_partial = True
            log_info(f"[activate_with_pending] Stored pending color: {colors}")
        else:
            log_info("[activate_with_pending] No targeting input, plain activate")

        # Refresh to show visual highlights for pending input
        mouse_clock.refresh_canvases()

    def mouse_clock_move_and_advance(letters_colors: List[str]):
        """Move mouse, then advance to next view in the pipeline."""
        # Do the move first
        actions.user.mouse_clock_move_multiple(letters_colors)

        mouse_clock = get_mouse_clock_instance()

        # If the move was partial (only letter or only color), don't advance
        if mouse_clock.core.last_move_was_partial:
            return

        current_mode = mouse_clock.get_display_mode()
        next_stage = get_next_stage(current_mode)

        # Update center to where the mouse just moved
        mx, my = ctrl.mouse_pos()
        mouse_clock.core.update_center(mx, my)

        if next_stage is not None:
            # Advance to next view in pipeline
            mouse_clock.set_mode(next_stage, set_mouse_clock_tags)
            log_info(f"[pipeline] Advanced from {current_mode} to {next_stage}, center=({mx:.0f}, {my:.0f})")
        else:
            # Last stage — stay on current mode, recenter for another targeting
            log_info(f"[pipeline] Staying on {current_mode}, recentered at ({mx:.0f}, {my:.0f})")

        mouse_clock.refresh_canvases()


