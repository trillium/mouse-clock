import math
from typing import Union, TypedDict, Any, List

from talon import Context, Module, actions, canvas, ctrl, screen, ui, settings
from talon.skia import Paint, Rect
from talon.types.point import Point2d

from ..utils import utils
from .constants import CLOCK_LETTERS, colors, COLORS, COLOR_BACKGROUND, COLOR_TEXT, COLOR_DOT, COLOR_CROSS, COLOR_ACTIVE, COLOR_INACTIVE, COLOR_LIST, COLOR_MAP, COLOR_POS
from .draw import draw_mouse_clock

ctx = Context()
ctx.lists["user.mouse"] = ["mouse"]

mod = Module()






mod.tag("use_mouse_clock", desc="Tag enables using mouse clock")
mod.tag("mouse_clock_showing", desc="Tag indicates whether the mouse clock is showing")

# Only use if tag is active
ctx.matches = r"""
tag: user.use_mouse_clock
"""

def flip_letter_to_opposite(letter: str) -> str:
    """Flip a clock letter to its opposite position (180 degrees).

    Clock positions:
    A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9, J=10, K=11, L=12

    Opposites (add 6 positions, wrap around):
    A↔G, B↔H, C↔I, D↔J, E↔K, F↔L
    """
    letter_index = CLOCK_LETTERS.index(letter.lower())
    opposite_index = (letter_index + 6) % 12
    return CLOCK_LETTERS[opposite_index]


def talon_expression_sort(words: list[str]):
    """Parse voice input words into letters, colors, and apply ordinal multipliers.

    Ordinals following a letter or color will multiply that item.
    Example: ["red", "3", "a", "pink"] ->  (where "3" came from saying "third")
             letters: ["a"], colors: ["red", "red", "red", "pink"]
    """
    letters_list = []
    colors_list = []
    unknowns_list = []

    i = 0
    while i < len(words):
        val = str(words[i]).lower()

        # Check if this is a numeric string (ordinals come through as "1", "2", "3" etc)
        is_ordinal = False
        multiplier = 0
        try:
            multiplier = int(val)
            if 1 <= multiplier <= 99:  # Valid ordinal range
                is_ordinal = True
        except ValueError:
            is_ordinal = False

        if is_ordinal:
            # This is an ordinal - it should apply to the previous item
            # Repeat the last added letter or color that many times
            if letters_list:
                # Repeat the last letter (multiplier - 1) more times
                # (since it's already in the list once)
                last_letter = letters_list[-1]
                for _ in range(multiplier - 1):
                    letters_list.append(last_letter)
                print(f"[ordinal] Repeated letter '{last_letter}' {multiplier} times total")
            elif colors_list:
                # Repeat the last color (multiplier - 1) more times
                last_color = colors_list[-1]
                for _ in range(multiplier - 1):
                    colors_list.append(last_color)
                print(f"[ordinal] Repeated color '{last_color}' {multiplier} times total")
            # Note: Ordinals by themselves are handled by the separate repeater action

        elif val in CLOCK_LETTERS:
            letters_list.append(val)
        elif val == "mouse":
            # "mouse" means center point
            colors_list.append("center")
        elif val == "half":
            # "half" means halfway to screen edge from last color
            colors_list.append("half")
        elif val in COLOR_MAP:
            colors_list.append(val)
        else:
            unknowns_list.append(val)

        i += 1

    result = {
        "letters": letters_list,
        "colors": colors_list,
        "unknowns": unknowns_list
    }
    return result


class MouseClock:
    def __init__(self):
        self.screen = None

        self.center_x, self.center_y = self.get_mouse_position()
        self.center = Point2d(self.center_x, self.center_y)

        self.radius = 300
        self.mcanvas = None
        self.active = False
        self.history = []
        self.last_command = ([], [])
        self.last_letters = []
        self.last_colors = []
        self.original_command = ([], [])  # Stores the original command before any reversal
        

    def get_mouse_position(self):
        '''returns (x, y) mouse position'''
        mouse_x, mouse_y = ctrl.mouse_pos()
        self.center_x = mouse_x
        self.center_y = mouse_y
        self.center = Point2d(self.center_x, self.center_y)
        return mouse_x, mouse_y

    def calculate_edge_distance(self, angle_degrees):
        """Calculate distance from center to screen edge in given direction.

        Args:
            angle_degrees: Angle in degrees (clock-style, 0=12 o'clock)

        Returns:
            Distance in pixels from center to screen edge in that direction
        """
        # Get screen dimensions
        if not self.screen:
            screens = ui.screens()
            self.screen = screens[0]

        screen_rect = self.screen.rect
        screen_left = screen_rect.x
        screen_top = screen_rect.y
        screen_right = screen_rect.x + screen_rect.width
        screen_bottom = screen_rect.y + screen_rect.height

        # Convert clock angle to standard math angle (radians)
        # Clock: 0° = up, 90° = right
        # Math: 0° = right, 90° = up
        angle_rad = math.radians((angle_degrees - 90) % 360)

        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)

        # Calculate distance to each edge
        distances = []

        # Distance to right edge
        if dx > 0:
            dist_right = (screen_right - self.center_x) / dx
            distances.append(dist_right)

        # Distance to left edge
        if dx < 0:
            dist_left = (screen_left - self.center_x) / dx
            distances.append(dist_left)

        # Distance to bottom edge
        if dy > 0:
            dist_bottom = (screen_bottom - self.center_y) / dy
            distances.append(dist_bottom)

        # Distance to top edge
        if dy < 0:
            dist_top = (screen_top - self.center_y) / dy
            distances.append(dist_top)

        # Return the minimum positive distance (the edge we'll hit first)
        valid_distances = [d for d in distances if d > 0]
        return min(valid_distances) if valid_distances else 0

    def get_new_mouse_position(self, letter_list, color_list, is_repeat=False):
        """Calculate the averaged (x, y) position for the mouse based on lists of letters and color_indices.

        Args:
            letter_list: List of letter inputs (a-l)
            color_list: List of color inputs
            is_repeat: If True, skip the incremental merging logic (for repeated commands)
        """
        self.last_command = (letter_list, color_list)
        prev_letters = self.last_letters
        prev_colors = self.last_colors

        # Only do incremental merging if this is NOT a repeat command
        if not is_repeat:
            if len(letter_list) > 0 and len(color_list) == 0:
                if prev_letters:
                    letter_list = prev_letters + letter_list
                if prev_colors:
                    color_list = prev_colors
            elif len(color_list) > 0 and len(letter_list) == 0:
                if prev_colors:
                    color_list = prev_colors + color_list
                if prev_letters:
                    letter_list = prev_letters
            else:
                self.last_letters = []
                self.last_colors = []

        self.last_letters = letter_list
        self.last_colors = color_list
        print("letter:", letter_list)
        print("color:", color_list)
        print()
        letter_ords = [utils.get_letter_ordinal(letter) for letter in letter_list]
        angles = [utils.letter_to_clock_angle(letter_ord) for letter_ord in letter_ords]
        avg_angle = utils.average_angles(angles)
        avg_hour, avg_deg = utils.average_clock_angles(letter_ords)

        # Use the full number of color rings, including center
        num_rings = len(COLOR_LIST)

        # Process colors - handle "half" specially
        color_index_list = []
        for i in color_list:
            if i == 'center':
                color_index_list.append(0)
            elif i == 'half':
                # Calculate halfway between last color and screen edge
                # Special case: if clock is not active, treat current position as starting point
                if not self.active:
                    # Clock is off - current mouse position is the reference
                    # "half" means halfway from HERE to screen edge
                    edge_distance = self.calculate_edge_distance(avg_deg)
                    half_distance = edge_distance / 2
                    color_index_list.append(half_distance)
                    print(f"[half] Clock off - current position to edge: {edge_distance}, Half distance: {half_distance}")
                else:
                    # Clock is on - use last color circle as reference
                    # Get the last non-"half" color, or use outermost ring if none
                    if color_index_list:
                        last_color_radius = color_index_list[-1]
                    else:
                        # Default to pink (outermost) if no previous color
                        last_color_radius = self.radius

                    # Calculate distance to screen edge in the average direction
                    edge_distance = self.calculate_edge_distance(avg_deg)

                    # Halfway between last color and edge
                    half_distance = (last_color_radius + edge_distance) / 2
                    color_index_list.append(half_distance)
                    print(f"[half] Clock on - Last color radius: {last_color_radius}, Edge distance: {edge_distance}, Half distance: {half_distance}")
            else:
                # Regular color from COLOR_POS
                color_index_list.append(self.radius * (COLOR_POS[i]) / (num_rings - 1))

        lengths_average = utils.average_over_lengths(color_index_list)
        radius = lengths_average
        new_mouse_pos = utils.move_in_direction(avg_deg, radius, origin=(self.center_x, self.center_y))
        return new_mouse_pos[0], new_mouse_pos[1]

    def setup(self):
        self.get_mouse_position()

        screens = ui.screens()
        # Close any existing canvases
        if hasattr(self, 'mcanvases') and self.mcanvases:
            for c in self.mcanvases:
                c.close()
        self.mcanvases = []

        # Create a canvas for each screen
        for s in screens:
            c = canvas.Canvas.from_screen(s)
            self.mcanvases.append(c)
            if self.active:
                c.register("draw", self.draw)
                c.freeze()

        # For compatibility, set self.mcanvas and self.screen to the one under the mouse
        mouse_point = Point2d(self.center_x, self.center_y)
        screen_found = None
        for s in screens:
            if s.rect.contains(mouse_point):
                screen_found = s
                break
        if screen_found is None:
            screen_found = screens[0]
        self.screen = screen_found
        self.mcanvas = self.mcanvases[screens.index(self.screen)]

    def show(self):
        if self.active:
            return
        for c in self.mcanvases:
            c.register("draw", self.draw)
            c.freeze()
        self.active = True

    def close(self):
        if not self.active:
            return
        for c in self.mcanvases:
            c.unregister("draw", self.draw)
            c.close()
        self.mcanvases = []
        self.mcanvas = None
        self.active = False

    def draw(self, canvas):
        draw_mouse_clock(
            canvas,
            self.center.x,
            self.center.y,
            self.radius,
            COLOR_LIST,
            COLOR_ACTIVE,
            COLOR_TEXT
        )

    def move_mouse(self, x,y):
        ctrl.mouse_move(x, y)
        self.history.append((x, y))

    def go_back(self):
        if self.history:
            x, y = self.history.pop()
            ctrl.mouse_move(x, y)
    
    def widen_radius(self):
        self.radius += 20
        if self.active and self.mcanvas:
            self.mcanvas.freeze()

    def narrow_radius(self):
        self.radius = max(20, self.radius - 20)
        if self.active and self.mcanvas:
            self.mcanvas.freeze()

    def set_radius(self, num):
        """Set the radius to a specific value and refresh the canvas if active."""
        self.radius = max(20, num)
        if self.active and self.mcanvas:
            self.mcanvas.freeze()

    def scoot(self, num: int, letter: str):
        print(num, letter)

    def clear(self):
        self.last_command = None
        self.last_letters = None
        self.last_colors = None

    def recenter(self):
        """Recenter the clock at the current mouse position and redraw, maintaining the same relative position."""
        # Get current mouse position
        current_x, current_y = ctrl.mouse_pos()

        # Recenter the clock at current position
        self.get_mouse_position()

        # If there was a last command, recalculate and move to the same relative position
        if self.last_command and (self.last_command[0] or self.last_command[1]):
            letters, colors = self.last_command
            x, y = self.get_new_mouse_position(letters, colors)
            self.move_mouse(x, y)

        if self.active:
            # Redraw all canvases with the new center
            for c in self.mcanvases:
                c.freeze()
        


mc = MouseClock()


@mod.action_class
class ClockActions:
    def mouse_clock_activate():
        """Show mouse clock"""
        if not mc.mcanvas:
            mc.setup()
        mc.show()
        mc.clear()
        ctx.tags = ["user.mouse_clock_showing"]

    def mouse_clock_close():
        """Close the mouse clock"""
        ctx.tags = []
        mc.close()

    def mouse_clock_move_multiple(letters_colors: List[str]):
        """Move the mouse to the intersection(s) of letters and colors.

        If the same command is repeated, recenter the clock at the current position
        and apply the command again, effectively moving in that direction.
        """
        typed_expressions = talon_expression_sort(letters_colors)
        letters = typed_expressions['letters']
        colors = typed_expressions['colors']

        # Validate: Must have at least one letter (direction)
        if not letters:
            print("[mouse_clock] Ignoring command - no direction specified (letters required)")
            return

        # Store as the original command (non-reversed)
        mc.original_command = (letters, colors)

        # Check if this exact command was just executed (and not empty)
        is_repeat = (mc.last_command == (letters, colors) and
                     mc.last_command != ([], []) and
                     letters and colors)  # Ensure both lists have content

        if is_repeat:
            # Same command repeated - recenter at current position
            # This moves the clock's origin to the current mouse position
            mc.get_mouse_position()
            # Redraw all canvases with the new center
            if mc.active:
                for c in mc.mcanvases:
                    c.freeze()

        x, y = mc.get_new_mouse_position(letters, colors, is_repeat=is_repeat)
        mc.move_mouse(x, y)


    def mouse_clock_move_opposite():
        """Move the mouse in the opposite direction of the original command.

        Always flips from the ORIGINAL command (stored in original_command), not last_command.
        If called repeatedly, recenters and keeps moving away in the same opposite direction.

        Example workflow:
        1. "red air" (C=3 o'clock) -> moves TO red C (90°)
           original_command = (['c'], ['red'])
        2. "reverse" -> flips C→I, moves to red I (270°)
           last_command = (['i'], ['red'])
        3. "reverse" (repeated) -> still flips C→I, recenters, moves to red I (270°) again
           Continues moving in the 270° direction
        """
        if not mc.original_command or mc.original_command == ([], []):
            print("[opposite] No original command to reverse")
            return

        orig_letters, orig_colors = mc.original_command

        if not orig_letters:
            print("[opposite] No letters in original command to reverse")
            return

        # Always flip from the ORIGINAL letters
        opposite_letters = [flip_letter_to_opposite(letter) for letter in orig_letters]

        # Check if we're repeating the reverse command
        # If last_command already matches the flipped version, we're repeating
        is_repeat_reverse = (mc.last_command == (opposite_letters, orig_colors))

        if is_repeat_reverse:
            # Repeating reverse - recenter and move away again
            print(f"[opposite] Repeating reverse - recentering and moving away")
            mc.get_mouse_position()
            # Redraw all canvases with the new center
            if mc.active:
                for c in mc.mcanvases:
                    c.freeze()

        print(f"[opposite] Original letters: {orig_letters} -> Opposite: {opposite_letters}")
        print(f"[opposite] Colors: {orig_colors}")

        x, y = mc.get_new_mouse_position(opposite_letters, orig_colors, is_repeat=is_repeat_reverse)
        mc.move_mouse(x, y)

    def mouse_clock_move_original():
        """Move the mouse in the original direction (opposite of reverse).

        Moves toward the original command direction. This is the opposite of the reverse action.
        If called repeatedly, recenters and keeps moving toward the original direction.

        Example workflow:
        1. "red air" -> original_command = (['a'], ['red'])
        2. "reverse" -> moves to opposite (G)
        3. Call this action -> moves back toward original (A)
        4. Repeat -> recenters and keeps moving toward A
        """
        if not mc.original_command or mc.original_command == ([], []):
            print("[original] No original command to move toward")
            return

        orig_letters, orig_colors = mc.original_command

        if not orig_letters:
            print("[original] No letters in original command")
            return

        # Check if we're repeating the original direction command
        is_repeat_original = (mc.last_command == (orig_letters, orig_colors))

        if is_repeat_original:
            # Repeating original - recenter and move toward again
            print(f"[original] Repeating original direction - recentering and moving toward")
            mc.get_mouse_position()
            # Redraw all canvases with the new center
            if mc.active:
                for c in mc.mcanvases:
                    c.freeze()

        print(f"[original] Moving toward original direction: {orig_letters}")
        print(f"[original] Colors: {orig_colors}")

        x, y = mc.get_new_mouse_position(orig_letters, orig_colors, is_repeat=is_repeat_original)
        mc.move_mouse(x, y)

    def mouse_clock_go_back():
        """Revert to the previous mouse position"""
        mc.go_back()

    def mouse_clock_widen():
        """Increases the radius of the circle"""
        mc.widen_radius()
        if mc.last_command:
            letters, colors = mc.last_command
            x,y = mc.get_new_mouse_position(letters, colors)
            mc.move_mouse(x,y)

    def mouse_clock_narrow():
        """Decreases the radius of the circle"""
        mc.narrow_radius()
        if mc.last_command:
            letters, colors = mc.last_command
            x,y = mc.get_new_mouse_position(letters, colors)
            mc.move_mouse(x,y)

    def mouse_clock_set_radius(num: int):
        """Sets the radius of mouse clock"""
        mc.set_radius(num)

    def mouse_clock_scoot(num: int, letter_list: str):
        """Shift the whole clock a direction"""
        mc.scoot(num, letter_list)

    def mouse_clock_recenter():
        """Recenter the clock at the current mouse position"""
        mc.recenter()

    def mouse_clock_recenter_and_move(letters_colors: List[str]):
        """Recenter clock at current position, then move to specified location"""
        mc.recenter()
        typed_expressions = talon_expression_sort(letters_colors)
        letters = typed_expressions['letters']
        colors = typed_expressions['colors']
        x, y = mc.get_new_mouse_position(letters, colors)
        mc.move_mouse(x, y)

    def mouse_clock_move_and_activate(letters_colors: List[str]):
        """Move mouse to position (with clock off), then activate clock at new position.

        This is for when the clock is currently off. It:
        1. Calculates the new position (treating current position as reference for 'half')
        2. Moves the mouse there
        3. Activates the clock at that NEW position
        """
        typed_expressions = talon_expression_sort(letters_colors)
        letters = typed_expressions['letters']
        colors = typed_expressions['colors']

        # Validate: Must have at least one letter (direction)
        if not letters:
            print("[mouse_clock] Ignoring command - no direction specified (letters required)")
            return

        # Calculate position with clock off (self.active will be False)
        print(f"[move_and_activate] Before calc - center: ({mc.center_x}, {mc.center_y})")
        x, y = mc.get_new_mouse_position(letters, colors)
        print(f"[move_and_activate] Calculated new position: ({x}, {y})")

        # Move mouse to new position FIRST
        mc.move_mouse(x, y)
        print(f"[move_and_activate] Mouse moved to: ({x}, {y})")

        # Now setup() will get the NEW mouse position as the center
        mc.setup()  # This calls get_mouse_position() which updates center to current mouse pos
        print(f"[move_and_activate] After setup - center: ({mc.center_x}, {mc.center_y})")
        mc.show()
        mc.clear()
        ctx.tags = ["user.mouse_clock_showing"]

        # Store as original command for potential reversal
        mc.original_command = (letters, colors)

