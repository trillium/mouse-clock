import math
from talon.skia import Paint
from talon import ui

CLOCK_LETTERS = "abcdefghijkl"


def get_screen_dimensions(center_x, center_y):
    """
    Get the screen dimensions for the screen containing the given point.

    Args:
        center_x: X coordinate of the point
        center_y: Y coordinate of the point

    Returns:
        Tuple of (width, height) for the screen containing the point
    """
    from talon.types.point import Point2d

    screens = ui.screens()
    point = Point2d(center_x, center_y)

    for screen in screens:
        if screen.rect.contains(point):
            return screen.rect.width, screen.rect.height

    # Fallback to first screen if point not found
    if screens:
        return screens[0].rect.width, screens[0].rect.height

    # Ultimate fallback
    return 1920, 1080


def setup_paint(canvas, color, stroke_width=2):
    """
    Configure canvas paint settings.

    Args:
        canvas: Talon canvas object
        color: Color to set
        stroke_width: Width of stroke lines

    Returns:
        Configured paint object
    """
    paint = canvas.paint
    paint.color = color
    paint.style = Paint.Style.STROKE
    paint.stroke_width = stroke_width
    return paint


def calculate_ring_radius(ring_index, total_rings, outer_radius):
    """
    Calculate the radius for a specific ring in the concentric circle pattern.

    Args:
        ring_index: Index of the ring (0 = center)
        total_rings: Total number of rings
        outer_radius: Radius of the outermost ring

    Returns:
        Radius for the specified ring
    """
    if ring_index == 0:
        return 0
    return outer_radius * ring_index / (total_rings - 1)


def calculate_clock_position(letter_index, radius, center_x, center_y):
    """
    Calculate the (x, y) position for a clock letter.

    Args:
        letter_index: Index of the letter (1-12, where 1 = A at 12 o'clock)
        radius: Radius at which to place the letter
        center_x: X coordinate of clock center
        center_y: Y coordinate of clock center

    Returns:
        Tuple of (x, y) coordinates
    """
    # 30 degrees per hour, starting at -90 (12 o'clock position)
    angle = math.radians(30 * letter_index - 90)
    x = center_x + radius * math.cos(angle)
    y = center_y + radius * math.sin(angle)
    return x, y


def draw_concentric_rings(canvas, center_x, center_y, radius, COLOR_LIST):
    """
    Draw the concentric colored rings of the mouse clock.

    Args:
        canvas: Talon canvas object
        center_x: X coordinate of clock center
        center_y: Y coordinate of clock center
        radius: Outer radius of the clock
        COLOR_LIST: List of colors for the rings
    """
    paint = canvas.paint
    num_rings = len(COLOR_LIST)

    for i in range(num_rings):
        paint.color = COLOR_LIST[i]
        ring_radius = calculate_ring_radius(i, num_rings, radius)
        canvas.draw_circle(center_x, center_y, ring_radius)


def draw_clock_position_dots(canvas, center_x, center_y, radius, COLOR_LIST, dot_radius=5):
    """
    Draw colored dots at each of the 12 clock positions on different rings.

    Args:
        canvas: Talon canvas object
        center_x: X coordinate of clock center
        center_y: Y coordinate of clock center
        radius: Outer radius of the clock
        COLOR_LIST: List of colors for each ring of dots
        dot_radius: Size of each dot (default: 5 pixels)
    """
    paint = canvas.paint
    paint.style = Paint.Style.FILL  # Use FILL instead of STROKE for solid dots

    num_rings = len(COLOR_LIST)

    # For each color ring
    for ring_index in range(num_rings):
        paint.color = COLOR_LIST[ring_index]
        ring_radius = calculate_ring_radius(ring_index, num_rings, radius)

        # Draw a dot at each of the 12 clock positions on this ring
        for position in range(1, 13):  # 1-12 for clock positions
            x, y = calculate_clock_position(position, ring_radius, center_x, center_y)
            canvas.draw_circle(x, y, dot_radius)


def calculate_edge_distance(ring_index, total_rings, screen_dimension, current_position):
    """
    Calculate distance from edge for a specific ring.

    Args:
        ring_index: Index of the ring (0 = at current position)
        total_rings: Total number of rings
        screen_dimension: Total screen dimension (width or height)
        current_position: Current mouse position in that dimension

    Returns:
        Distance from current position towards the edge
    """
    if ring_index == 0:
        return 0

    # Distance available to the edge
    distance_to_edge = screen_dimension - current_position

    # Divide the distance into equal segments
    return (distance_to_edge / total_rings) * ring_index


def draw_edge_distance_dots(canvas, center_x, center_y, screen_width, screen_height, COLOR_LIST, dot_radius=5):
    """
    Draw colored dots at clock positions, with colors representing distance from screen edge.

    Args:
        canvas: Talon canvas object
        center_x: X coordinate of clock center (current mouse position)
        center_y: Y coordinate of clock center (current mouse position)
        screen_width: Width of the screen
        screen_height: Height of the screen
        COLOR_LIST: List of colors for each distance ring
        dot_radius: Size of each dot (default: 5 pixels)
    """
    paint = canvas.paint
    paint.style = Paint.Style.FILL

    num_rings = len(COLOR_LIST)

    # For each color ring
    for ring_index in range(num_rings):
        paint.color = COLOR_LIST[ring_index]

        # Draw a dot at each of the 12 clock positions
        for position in range(1, 13):  # 1-12 for clock positions
            angle = math.radians(30 * position - 90)

            # Calculate which edge we're heading towards
            dx = math.cos(angle)
            dy = math.sin(angle)

            # Determine the limiting dimension based on direction
            if abs(dx) > abs(dy):
                # Primarily horizontal movement
                if dx > 0:  # Moving right
                    edge_distance = screen_width - center_x
                else:  # Moving left
                    edge_distance = center_x
            else:
                # Primarily vertical movement
                if dy > 0:  # Moving down
                    edge_distance = screen_height - center_y
                else:  # Moving up
                    edge_distance = center_y

            # Calculate distance for this ring
            distance = (edge_distance / num_rings) * ring_index

            # Calculate final position
            x = center_x + distance * dx
            y = center_y + distance * dy

            canvas.draw_circle(x, y, dot_radius)


def draw_clock_letters(canvas, center_x, center_y, radius, COLOR_TEXT):
    """
    Draw the clock position letters (A-L) around the outer ring.

    Args:
        canvas: Talon canvas object
        center_x: X coordinate of clock center
        center_y: Y coordinate of clock center
        radius: Radius at which to place letters
        COLOR_TEXT: Color for the letter text
    """
    paint = canvas.paint
    paint.color = COLOR_TEXT

    for i, letter in enumerate(CLOCK_LETTERS.upper(), start=1):
        x, y = calculate_clock_position(i, radius, center_x, center_y)
        canvas.draw_text(letter, x, y)


def draw_mouse_clock(canvas, center_x, center_y, radius, COLOR_LIST, COLOR_ACTIVE, COLOR_TEXT, style="?", dot_radius=5, screen_width=None, screen_height=None):
    """
    Draw the mouse clock visualization with concentric circles and clock position letters.

    Args:
        canvas: Talon canvas object
        center_x: X coordinate of clock center
        center_y: Y coordinate of clock center
        radius: Outer radius of the clock
        COLOR_LIST: List of colors for the concentric rings
        COLOR_ACTIVE: Color for active elements
        COLOR_TEXT: Color for letter labels
        style: Drawing style - "rings", "dots", or "edge"
        dot_radius: Radius of dots when style="dots" or "edge" (default: 5 pixels)
        screen_width: Screen width (optional, auto-detected if not provided)
        screen_height: Screen height (optional, auto-detected if not provided)
    """
    setup_paint(canvas, COLOR_ACTIVE)

    if style == "edge":
        # Auto-detect screen dimensions if not provided
        if screen_width is None or screen_height is None:
            screen_width, screen_height = get_screen_dimensions(center_x, center_y)
        draw_edge_distance_dots(canvas, center_x, center_y, screen_width, screen_height, COLOR_LIST, dot_radius)
    elif style == "dots":
        draw_clock_position_dots(canvas, center_x, center_y, radius, COLOR_LIST, dot_radius)
    else:  # Default to "rings"
        draw_concentric_rings(canvas, center_x, center_y, radius, COLOR_LIST)

    draw_clock_letters(canvas, center_x, center_y, radius, COLOR_TEXT)
