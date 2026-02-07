_V = "0.0.11"; print(f"[v{_V}] {__name__}")
"""Build radial fan lines for 'this' mode targeting."""

import math
from typing import List, Tuple, Optional

# (start, end, color_name_or_label)
Line = Tuple[Tuple[float, float], Tuple[float, float], str]


def build_parallel_lines(
    start: Tuple[float, float],
    target: Tuple[float, float],
    colors: List[str],
    spacing: float = 5.0,
) -> Optional[List[Line]]:
    """Build radial fan: same start, same length, rotated apart by `spacing` degrees.

    Gray line points from start to target.
    Color lines share the same start and length, each rotated by
    `spacing` degrees apart, centered on the gray direction.

    Returns a list of (start, end, color_name) tuples:
      - lines[0] is always the gray center indicator
      - lines[1:] are the color lines in fixed order

    Returns None if the line has zero length.
    """
    start_x, start_y = start
    target_x, target_y = target

    dx = target_x - start_x
    dy = target_y - start_y
    length = math.sqrt(dx * dx + dy * dy)
    if length == 0:
        return None

    # Gray line angle
    base_angle = math.atan2(dy, dx)

    n = len(colors)
    deg_step = math.radians(spacing)

    lines: List[Line] = []

    # Gray line FIRST (center indicator, drawn underneath)
    lines.append((start, target, "gray"))

    # Color lines: all start at target, fan out toward cursor
    # N colors + 1 gray = N+1 evenly spaced lines, gray in center slot
    toward_cursor = math.atan2(start_y - target_y, start_x - target_x)
    total = n + 1
    gray_slot = n // 2  # gray sits in the middle

    for pos in range(total):
        angle = toward_cursor + (pos - gray_slot) * deg_step
        if pos == gray_slot:
            continue  # gray already added as lines[0]
        color_idx = pos if pos < gray_slot else pos - 1
        e_x = target_x + length * math.cos(angle)
        e_y = target_y + length * math.sin(angle)
        lines.append((target, (e_x, e_y), colors[color_idx]))

    return lines
