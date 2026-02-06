_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Debug overlay for the mouse clock.

Draws animation debug info (lerp factor, increment, elapsed) at the clock center.
"""

import time
from talon.skia import Paint


def draw_debug_info(canvas_obj, core):
    """Draw debug info (lerp factor, increment, elapsed) at center."""
    paint = Paint()
    paint.color = "white"
    paint.textsize = 14
    paint.style = paint.Style.FILL

    # Get animation values
    animator = core._animator
    elapsed = animator.get_elapsed()
    lerp = animator.get_lerp_factor()
    inc = animator.get_dynamic_increment()

    # Calculate time since last input
    if animator._last_input_time:
        since_input = time.time() - animator._last_input_time
        since_str = f"{since_input:.2f}s"
    else:
        since_str = "--"

    # Format debug text
    lines = [
        f"lerp: {lerp:.2f}",
        f"inc: {inc:.0f}",
        f"dur: {elapsed:.2f}s",
        f"gap: {since_str}",
    ]

    # Draw at center, stacked vertically
    x = core.center_x
    y = core.center_y - 28  # Start above center

    for line in lines:
        canvas_obj.draw_text(line, x - 30, y, paint)
        y += 16
